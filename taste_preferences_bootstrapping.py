"""
Get the lick data from pickle files generated from read_licks.py
using boostrapping to create the distribution of taste palatability ranking orders 

"""
import numpy as np
import easygui
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import permutations


# list tastes based on their palatability ranking (but not need to)    
#tastes = ['SUCROSE', 'NACL', 'WATER', 'CITRIC_ACID', 'QHCL']
tastes = ['SUCROSE', 'NACL', 'CITRIC_ACID', 'QHCL']

# # load data from a pickle file
# lick_data = []
# for f in ['./data/km35_day01/0723KM35_TEST1.pkl', './data/km35_day02/0724KM35_TEST2.pkl']:
#     # pkl_name = './data/day2/0817KM41_TEST2.pkl'
#     with open(f, 'rb') as pkl_file:
#         lick_data.append(pickle.load(pkl_file))


# trial_licks = []
# # obtain lick number for each trial,also remove 0-lick trials
# for dat in lick_data:
#     this_trial_licks = {}
#     for k in dat.keys():
#         if 'sum' in k:
#             these_licks = dat[k]
#             this_trial_licks[k[:-9]] = [i for i in these_licks if i > 0]
#     trial_licks.append(this_trial_licks)


# for this code to work, you will need to make a list named "trial_licks" with 2 dictionaries in it.

trial_licks = [{'NACL': [73, 68, 66, 64, 61, 67, 69, 64, 65],
  'WATER': [55, 63, 34, 59, 65, 52, 61, 60, 67],
  'SUCROSE': [21, 17, 17, 12, 26, 31, 18],
  'QHCL': [17, 7, 10, 3, 2, 18],
  'CITRIC_ACID': [15, 11, 6, 3, 5, 3]},
 {'NACL': [55, 50, 66, 65, 66, 64, 2],
  'WATER': [56, 3, 18, 67, 63, 40, 58, 64, 48, 47, 10],
  'SUCROSE': [59, 33, 45, 59, 2],
  'QHCL': [40, 19, 6, 6, 6, 2, 5, 2],
  'CITRIC_ACID': [14, 4, 27, 2]}]


# trial_licks
# most possible orders of the items
sequencing = [[3,2,1,0], [3,2,0,1], [2,3,1,0], [2,3,0,1], [3,1,2,0]]
taste_dict = {3:'S', 2:'N', 1:'CA', 0:'Q'}
t_tables = [taste_dict[i] for i in np.concatenate(sequencing)]
t_tables = np.array(t_tables).reshape(len(sequencing),-1)
y_ticklabels = ["-".join(i) for i in t_tables]
y_ticklabels.append('Others')
y_ticklabels

# list(permutations(np.arange(len(tastes))))
# define a function to get the pal-ranking of the list of trials
def ranking(array):
    #a = list(array)
    sort_a = list(np.sort(array))
    ranks = [sort_a.index(i) for i in array]
    return ranks

# random choose trial lick count for each taste 1000 times
n_samples = 500
result = []
for dat in trial_licks:
    bst = {}
    bst_list = []
    for k in tastes:
        samples = np.random.choice(dat[k], size = n_samples, replace=True)
        bst[k] = samples
        bst_list.append(samples)
    bst_array = np.array(bst_list)
    bst_array.shape

    order_positions = [[] for _ in range(len(sequencing))]
    for trials in range(bst_array.shape[1]): 
        for i, j in enumerate(sequencing):
            if list(j) == ranking(bst_array[:, trials]):
                order_positions[i].append(i)
                break

    frequency = [len(i) + int(n_samples*0.01) for i in order_positions]
    frequency.insert(len(frequency)+1, n_samples-np.sum(frequency))
    result.append(frequency)
print(result)

fig, ax = plt.subplots(1, 2, sharey=True, sharex=True, figsize=(8,4))
for i in range(2):
    ax[i].bar(np.arange(len(result[i])), result[i])
    ax[i].set_xticks(np.arange(len(result[i])))
    ax[i].set_xticklabels(y_ticklabels, rotation=90)
    if i ==0:
        ax[i].set_ylabel('Frequency of the ranking order')
    ax[i].set_title(f'KM35- Day {i+1}')
plt.tight_layout()

