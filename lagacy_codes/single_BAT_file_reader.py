"""
This code reads in data from the text file generated from Med-associates Davis Rig software, 
and then saves it as a Pandas Dataframe.

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

# read in text file generated from BAT program
file_path = easygui.diropenbox(msg = 'Choose a directory with lick data')
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

# clean the dataframe before read in inter-lick intervals for each trial
# make column names all lower case
col_names = [i.lower() for i in df.columns]
df.columns = col_names
# drop unused column
df = df.drop('openerror', axis=1)
df = df.drop('closeerror\n', axis=1)

# reading in ilis and save to dataframe
ilis = []
for i in range(Trial_data_stop+1, len(lines)):
    this_line = lines[i].split(',')[1:]
    num_line = [int(i) for i in this_line]
    ilis.append(num_line)
# sanity check
if np.max(df.presentation) == len(ilis):
    df['ilis'] = ilis
else:
    print('Something wrong with the itis reading! please check your text files')

# save the dataframe to the folder where the text file was read in
df_name = Detail_Dict['Animal'].strip() + '_' + Detail_Dict['StartDate'].replace('/', '')
df.to_pickle(os.path.join(file_path, f"{df_name}.pkl"))

