"""
This code reads in data from the text file generated from Med-associates Davis Rig software,
use Brad's function to generate bout analysis results,
and then saves it as a Pandas Dataframe.

At the current status, the code searches the med-associates text file in a folder (so, one folder one file)
then using 500ms as the criterion of inter-cluster-interval to execute lick bout analysis

then save the result in a pickle file with the form of dataframe
"""


# import  Built-in Python libraries

import os # functions for interacting w operating system

# 3rd-party libraries
import numpy as np # module for low-level scientific computing
import easygui
import pandas as pd
import itertools
import glob
from datetime import date

#Define a padding function
def boolean_indexing(v, fillval=np.nan):
    lens = np.array([len(item) for item in v])
    mask = lens[:,None] > np.arange(lens.max())
    out = np.full(mask.shape,fillval)
    out[mask] = np.concatenate(v)
    return out

def LickMicroStructure_stone(dFrame_lick, latency_array, bout_crit):
# =============================================================================
#     Function takes in the dataframe and latency matrix pertaining to all 
#     licking data obtained from MedMS8_reader_stone as the data sources. This 
#     requires a bout_crit 
#     
#     Input: 1) Dataframe and Licking Matrix (obtained from MedMS8_reader_stone)
#            2) Bout_crit; variable which is the time (ms) needed to pause between
#               licks to count as a bout (details in: Davis 1996 & Spector et al. 1998).
# 
#     Output: Appended dataframe with the licks within a bout/trial, latency to 
#             to first lick within trial    
# =============================================================================
    #Find where the last lick occured in each trial
    last_lick = list(map(lambda x: [i for i, x_ in enumerate(x) if not \
                                    np.isnan(x_)][-1], latency_array))
    
    #Create function to search rows of matrix avoiding 'runtime error' caused
    #by Nans
    crit_nan_search = np.frompyfunc(lambda x: (~np.isnan(x)) & (x >=bout_crit), 1, 1)
    
    #Create empty list to store number of bouts by trial
    bouts = []; ILIs_win_bouts = []
    for i in range(latency_array.shape[0]):
        #Create condition if animal never licks within trial
        if last_lick[i] == 0:
            bouts.append(last_lick[i])
            ILIs_win_bouts.append(last_lick[i])
            
        else:
            bout_pos = np.where(np.array(crit_nan_search(latency_array[i,:])).astype(int))
            
            #Insert the start number or row to get accurate count
            bout_pos = np.insert(bout_pos,0,1)
            
            #Caclulate bout duration
            bout_dur = np.diff(bout_pos) 

            #Flip through all bouts and calculate licks between and store
            if last_lick[i] != bout_pos[-1]:
                #Insert the last lick row to get accurate count
                bout_pos = np.insert(bout_pos,len(bout_pos),last_lick[i])
                
                #Calculate bout duration
                bout_dur = np.diff(bout_pos) 
            
            #Append the time diff between bouts to list (each number symbolizes a lick)
            bouts.append(np.array(bout_dur))                

            #Grab all ILIs within bouts and store
            trial_ILIs = []
            
			#append list if only one lick occurs post intial lick
            if len(bout_pos) ==1:
                trial_ILIs.append(latency_array[i,1])
			
            if len(bout_pos) !=1:
	            for lick in range(len(bout_pos)-1):	
	                if lick ==0:
	                    trial_ILIs.append(latency_array[i,1:bout_pos[lick+1]])
	                else:
	                    trial_ILIs.append(latency_array[i,bout_pos[lick]:1+bout_pos[lick+1]])
	            
			#Append for trial total
            ILIs_win_bouts.append(trial_ILIs)

    #Store bout count into dframe
    dFrame_lick["Bouts"] = bouts
    dFrame_lick["ILIs"] = ILIs_win_bouts         
    dFrame_lick["Lat_First"] = latency_array[:,1]
    
    #Return the appended dataframe
    return dFrame_lick	  
    
# read in text file generated from BAT program
file_path = easygui.diropenbox(msg = 'Choose a directory with lick data')
#file_path = 'C:\\Users\\JianYouLin\\OneDrive\\code_repositories\\bat_licks\\brief_acces_rig\\lagacy_codes\\test'
os.chdir(file_path)
for i in os.listdir():
    if 'txt' in i:
        text_file = i
file_name = os.path.join(file_path, text_file)
file_input = open(file_name)

# read in each line of the text file
lines = file_input.readlines()

# read in experimental related information
# then convert it into pandas dataframe
Detail_Dict = {'FileName': None,
               'StartDate': None,
               'StartTime': None,
               'Animal': None,
               'MAXFLick': None,
               'Trials': None,
               'LickDF': None,
               'LatencyMatrix': None}

#Extract file name and store
Detail_Dict['FileName'] = file_name[file_name.rfind('/')+1:]

#Store details in dictionary and construct dataframe	
for i in range(len(lines)):
    if "Start Date" in lines[i]:
        Detail_Dict['StartDate'] = lines[i].split(',')[-1][:-1].strip()
    if "Start Time" in lines[i]:
        Detail_Dict['StartTime'] = lines[i].split(',')[-1][:-1]
    if "Animal ID" in lines[i]:
        Detail_Dict['Animal'] = lines[i].split(',')[-1][:-1]		
    if "Max Wait" in lines[i]:
        Detail_Dict['MAXFLick'] = lines[i].split(',')[-1][:-1]			
    if "Max Number" in lines[i]:
        Detail_Dict['Trials'] = lines[i].split(',')[-1][:-1]			
    if "PRESENTATION" and "TUBE" in lines[i]:		
        ID_line = i
    if len(lines[i].strip()) == 0:		
        Trial_data_stop = i		
        if ID_line > 0 and Trial_data_stop > 0:
            #Create dataframe
            df = pd.DataFrame(columns=lines[ID_line].split(','),\
                      data=[row.split(',') for row in \
                     lines[ID_line+1:Trial_data_stop]])
            
            #Remove spaces in column headers (caused by split)
            df.columns = df.columns.str.replace(' ', '')
            
            #Set concentrations to 0 if concentration column blank
            df['CONCENTRATION']=df['CONCENTRATION'].str.strip()
            df['CONCENTRATION'] = df['CONCENTRATION'].apply(lambda x: 0 if x == '' else x)

            #Convert specific columns to numeric
            df["SOLUTION"] = df["SOLUTION"].str.strip()
            df[["PRESENTATION","TUBE","CONCENTRATION","LICKS","Latency"]] = \
                df[["PRESENTATION","TUBE","CONCENTRATION","LICKS","Latency"]].apply(pd.to_numeric)
            
            #Add in identifier columns
            df.insert(loc=0, column='Animal', value=Detail_Dict['Animal'])
            df.insert(loc=3, column='Trial_num', value='')
            df['Trial_num'] = df.groupby('TUBE').cumcount()+1
            
            #Store in dataframe
            Detail_Dict['LickDF'] = df		
            
            #Grab all ILI data, pad with NaNs to make even matrix
            #Store in dictionary (TrialXILI count)
            Detail_Dict['LatencyMatrix'] = boolean_indexing([row.split(',')\
                                              for row in lines[Trial_data_stop+1:]])

# reading in ilis and save to dataframe
ilis = []
for i in range(Trial_data_stop+1, len(lines)):
    this_line = lines[i].split(',')[1:]
    num_line = [int(i) for i in this_line]
    ilis.append(num_line)

# sanity check
if np.max(df.PRESENTATION) == len(ilis):
    df['ilis'] = ilis
else:
    print('Something wrong with the ilis reading! please check your text files')

bout_pause = 500

df_bout = LickMicroStructure_stone(df, Detail_Dict['LatencyMatrix'], bout_pause)

#Untack all the ILIs across all bouts to performa math
df_lists = df_bout[['Bouts']].unstack().apply(pd.Series)
df_bout['bout_count'] = np.array(df_lists.count(axis='columns'))
df_bout['Bouts_mean']=np.array(df_lists.mean(axis = 1, skipna = True))


# make column names all lower case
col_names = [i.lower() for i in df_bout.columns]
df_bout.columns = col_names
# drop unused column
df_bout = df_bout.drop('openerror', axis=1)
df_bout = df_bout.drop('closeerror\n', axis=1)

# save the dataframe to the folder where the text file was read in
df_name = Detail_Dict['Animal'].strip() + '_' + Detail_Dict['StartDate'].replace('/', '')
df_bout.to_pickle(os.path.join(file_path, f"{df_name}.pkl"))

