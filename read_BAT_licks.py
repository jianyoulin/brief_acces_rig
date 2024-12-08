# load modules
import numpy as np
import pandas as pd
import easygui
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
from lick_analysis import LickAnalysis
from util_tools import *

# define functions to correct lick data
def remove_short_lick(ITIs, ctn):
    index_ctn = np.where(ITIs <= ctn)[0]
    if len(index_ctn) > 0:
        adj_ITIs = ITIs.copy()
        if index_ctn[-1] == len(ITIs)-1:
            adj_ITIs[index_ctn[:-1]+1] = ITIs[index_ctn[:-1]] + ITIs[index_ctn[:-1]+1]
        else: adj_ITIs[index_ctn+1] = ITIs[index_ctn] + ITIs[index_ctn+1]
        ITIs_rm = adj_ITIs[adj_ITIs>50]
    else: ITIs_rm = ITIs
    return ITIs_rm

def ili_to_licktime(inter_lick_intervals=None):
    ilis = np.insert(inter_lick_intervals, 0, 0)
    return np.cumsum(ilis)

# Ask the user for the BAT data files that need to be merged together
manual_add = False
try:
     dirs = easygui.multchoicebox(msg = 'Choose which folder(s) to be involved in analysis',
                             choices = dirs)
except:
     print("No imported dirs, please add in manually")
     manual_add = True
if manual_add:  
    dirs = []
    while True:
        dir_name = easygui.diropenbox(msg = 'Choose a directory with a hdf5 file, hit cancel to stop choosing')
        try:
            if len(dir_name) > 0:	
                dirs.append(dir_name)
        except:
            break

for dir_name in dirs:        
	# Change to the directory
    os.chdir(dir_name)
    #Look for the txt files in the directory
    file_list = os.listdir('./')
    lick_files = [file for file in file_list if "txt" in file]
       
    for file in lick_files:
        # create empty dictionary to save lick data
        lick_dic = {}
        with open(file, 'r') as f:

            # find animal id
            animal_id = None
            while not animal_id:
                this_line = f.readline().split(',')
                if this_line[0] == 'Animal ID':
                    animal_id = this_line[1].strip()
          
            #read to the line with "PRESENTATION"
            find_presentation = False
            while not find_presentation:
                this_line = f.readline().split(',')
                if this_line[0] == 'PRESENTATION':
                    for k in this_line:
                        lick_dic[k] = []
                    find_presentation = True
            
            #Read to the empty line to get taste name of each trial
            line_characters = 2#len(f.readline())
            while line_characters > 1:
                trial_info = f.readline().split(',')
                line_characters = len(trial_info)
                if line_characters > 1:
                    for index_, k in enumerate(lick_dic.keys()):
                        lick_dic[k].append(trial_info[index_].strip())

            # add variables to the lick dictionary
            lick_vars = ['ilis', 'lick_times', 'mbout_size', '1st_bout', 'bouts']
            for l_v in lick_vars:
                lick_dic[l_v] = []
            
            #Read to the last line to the interlick intervals from each trial
            line = ['start']    
            while len(line) > 0:
                try:
                    line = np.int_(f.readline().split(','))
                    # print(line, len(line))
                    if len(line) > 1:
                        ilis = remove_short_lick(line[1:], 50)
                        lick_times = ili_to_licktime(inter_lick_intervals=ilis)
                        clusters = LickAnalysis(lick_times, ICI=500)
                        dat_list = [ilis, lick_times, clusters.bout_mean(), 
                                    clusters.get_bout(0), clusters.get_clusters()]
                        for index, l_v in enumerate(lick_vars):
                            lick_dic[l_v].append(dat_list[index])
                        
                    else:
                        for index, l_v in enumerate(lick_vars):
                            lick_dic[l_v].append(np.nan)
                except ValueError:
                    print('The end of interlick interval recordings')
                    break

            lick_df = pd.DataFrame(lick_dic)
            lick_df.insert(loc = 0, column = 'rat_id', value = animal_id)
            etype = '_'.join(file.split('.')[0].split('_')[1:])
            lick_df.insert(loc = 1, column = 'exp_type', 
                           value = etype)

            # clean the dataframe
            # make column names all lower case, and remove space/line characters
            col_names = [i.lower().strip() for i in lick_df.columns]
            lick_df.columns = col_names
            # drop useless columns
            lick_df = lick_df.drop('open error', axis=1)
            lick_df = lick_df.drop('close error', axis=1)
            lick_df = lick_df.drop('retries', axis=1)

            save_name = os.path.join(dir_name, f"{file.split('.')[0]}.pkl")
            lick_df.to_pickle(save_name)
