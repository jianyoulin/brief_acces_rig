# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 17:22:39 2018

This code extract data from each lick file

@author: JYlabPC
"""

import numpy as np
import easygui
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Ask the user for the directory where the lick data exist	
dirs = []
dir_name = easygui.diropenbox(msg = 'Choose a directory with lick data')
dirs.append(dir_name)

trial_array = [] #index of trials for each tastant for each rat
licks_array = [] #number of licks for each trial for each rat

###
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
###

for index, dir_name in enumerate(dirs):
	# Change to the directory
    os.chdir(dir_name)
    #Look for the txt files in the directory
    file_list = os.listdir('./')
    lick_files = [file for file in file_list if "txt" in file]        
    
    for file in lick_files:
        with open(file, 'r') as f:
          
            #read to the line with "PRESENTATION"
            find_presentation = False
            while not find_presentation:
                if f.readline().split(',')[0] == 'PRESENTATION':
                    find_presentation = True
            
            #Read to the empty line to get taste name of each trial
            taste_array = []
            line_characters = 2#len(f.readline())
            while line_characters > 1:
                line = f.readline().split(',')
                line_characters = len(line)
                if line_characters > 1:
                    taste_array.append(line[3]+line[1])
                
            #Read to the last line to the interlick intervals from each trial
            this_file_licks = []
            line = ['start']    
            while len(line) > 0:
                try:
                    line = np.int_(f.readline().split(','))
                    if len(line) > 1:
                        #this_file_licks.append(line[1:]) #np.int_(f.readline().split(',')[1:]))
                        this_file_licks.append(remove_short_lick(line[1:], 50)) 
                    else:
                        this_file_licks.append([])
                except ValueError:
                    break
            licks_array.append(this_file_licks)
    
            #Based on the taste array, extract the trial numbers for each taste 
            taste_list = (e for e in set(taste_array))
            taste_list = list(taste_list)
            this_trial_array = []
            for item in range(len(taste_list)):
                this_trial_array.append([i for i, e in enumerate(taste_array) if e == taste_list[item]])
            trial_array.append(np.array(this_trial_array))
    
       
        tastes_licks = []
        for taste in range(len(taste_list)):
            tastes_licks.append([])
            for trial in trial_array[index][taste, :]:
                if len(licks_array[index][trial]) > 0:
                    tastes_licks[taste].append(np.array(len(licks_array[index][trial])+1))
                else:
                    tastes_licks[taste].append(np.array(len(licks_array[index][trial])))
        tastes_licks = np.array(tastes_licks)
        
        lick_data = {}
        for taste in taste_list:
            taste_s = taste.replace(' ', '')
            lick_data[taste_s] = [licks_array[index][trial] for trial in trial_array[index][taste_list.index(taste), :]]
            lick_data[f'{taste_s}_sumlick'] = tastes_licks[taste_list.index(taste), :]
        
        # Save the lick data dictionaries into disk
        output = open(f"{file.split('.')[0]}.pkl", "wb")
        pickle.dump(lick_data, output)
        output.close()

### Code below are for plotting of data  
lick_data_list = []
for dir_name in dirs:
	# Change to the directory
    os.chdir(dir_name)
	# Locate the hdf5 file
    file_list = os.listdir('./')
    for files in file_list:
        if files[-3:] == 'pkl':
            pkl_name = files
    with open(pkl_name, 'rb') as pkl_file:
        this_lick_data = pickle.load(pkl_file)
        lick_data_list.append(this_lick_data)

def sns_plot(array, bin_size, hist = True, kde = True):
    sns.histplot(filtered_array, kde=kde, 
                 bins=int((filter_range[1]-filter_range[0])/bin_size), 
                 color = plt.cm.Pastel1(index/5), label = taste,
                 cbar_kws={'edgecolor':'black', 'range': [filter_range[0],filter_range[1]]}) 

#define plotting function 
def plot_ITI_hist(array, method = "sns", bin_size = 5):
    if method == "sns":
        # seaborn histogram
        sns_plot(array, bin_size)
    else:
        ax.hist(filtered_array, int((filter_range[1]-filter_range[0])/bin_size), 
                range = (filter_range[0],filter_range[1]), 
                facecolor = plt.cm.Pastel1(index/5), edgecolor = 'black', label = taste)
    ax.set(xlabel = 'Inter-lick Intervals', ylabel = 'Frequency', xlim = (filter_range[0]-5, filter_range[1]+5))
    ax.annotate(f'{round(len(filtered_array)/len(array), 3)}% of ILI data', xy = (ax.get_xlim()[1]*0.6, ax.get_ylim()[1]*0.8))
    ax.legend(loc = "best")

# Plotting histogram of inter-lick-intervals for each tastant

taste_list = [i for i in lick_data_list[0].keys() if 'sum' not in i]
taste_list.sort()
for index, taste in enumerate(taste_list):
    for ses in range(len(lick_data_list)):
        num_trials = len(lick_data_list[ses][taste])
        this_taste_licks = np.concatenate(tuple(lick_data_list[ses][taste][trial] for trial in range(num_trials)))
    
    #setting up histogram  parameters
    filter_range = [50, 500]
    filtered_array = this_taste_licks[(this_taste_licks >= filter_range[0]) & (this_taste_licks < filter_range[1])]
    #Plot histogram of ITIs values
    fig, ax = plt.subplots()#nrows = 1, ncols=laser_cond, squeeze=False, figsize = figsize)
    plot_ITI_hist(this_taste_licks, method = "sns", bin_size = 5)
    plt.savefig(f'hist_{taste.replace(" ", "")}.png')
    plt.close()

# plotting average number of licks for each tastant
sum_lick_list = [i for i in lick_data_list[0].keys() if 'sum' in i]
sum_lick_list.sort()
sum_lick = []
plt.plot()
for index, taste in enumerate(sum_lick_list):
    this_taste_sum = np.concatenate(tuple(lick_data_list[ses][taste] for ses in range(len(lick_data_list))))
    sum_lick.append(this_taste_sum)
    this_taste_mean = np.mean([licks for licks in this_taste_sum if licks > 0])
    plt.bar(index+1, this_taste_mean, color = plt.cm.Pastel1(index/5), label = taste.replace(' ', '')[:-8], zorder=0)
    for trial in range(len(this_taste_sum)):
        plt.scatter(index+1+np.random.choice([-0.2,-0.1,0,0.1,0.2]), 
                    this_taste_sum[trial], marker = r"$ {} $".format(trial), 
                    color = 'grey', alpha = 0.5, zorder=5)
x_ticklabels = [taste.replace(' ', '')[:-8] for taste in sum_lick_list]
plt.xticks(np.arange(len(sum_lick_list))+1, x_ticklabels, rotation = 45)
plt.ylabel('Number of Licks per Trial')
plt.savefig('mean_licks.png')
plt.close()


