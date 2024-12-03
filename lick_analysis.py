import numpy as np

class LickAnalysis:
    def __init__(self, arr, ICI=0.5):
        self.arr = np.array(arr)
        self.ICI = ICI
        self.clusters = self.get_clusters()

    def get_clusters(self):
        if len(self.arr) == 0:
            # print('No lick detected on this trial')
            return [[np.nan]]
        else:
            # Main logic for clustering
            if len(self.arr) == 1:

                return [[self.arr[0]]]
            else:
                inter_lick_intervals = np.diff(self.arr)
                cluster_change_indices = np.where(inter_lick_intervals > self.ICI)[0] + 1
                clusters = np.split(self.arr, cluster_change_indices)

                return [list(cluster) for cluster in clusters]  # Convert to list of lists for consistency

#         cluster_n = 0
#         clusters = [[]]
        
#         if len(self.arr) > 1:
#             clusters[0].append(self.arr[0])
#             for i in range(1, len(self.arr)):
#                 if self.arr[i] - self.arr[i - 1] <= self.ICI:
#                     clusters[cluster_n].append(self.arr[i])
#                 else:
#                     clusters.append([])
#                     cluster_n += 1
#                     clusters[cluster_n].append(self.arr[i])
#         elif len(self.arr) == 1:
#             clusters[cluster_n].append(self.arr[0])
#         else:
#             print('No lick detected on this trial')
#             clusters[cluster_n].append(np.nan)

#         return clusters
    def bout_mean(self):
        """
        Calculate the mean size of bouts.

        Returns:
        - Mean size of bouts or NaN if no licks are detected
        """
        bout_sizes = []

        if self.clusters:
            for cluster in self.clusters:
                bout_sizes.append(np.nansum(~np.isnan(cluster)))
                # try:
                #     bout_sizes.append(np.nansum(~np.isnan(cluster)))
                # except:
                #     bout_sizes.append(np.nan)
            return np.nanmean(bout_sizes)
        else:
            return np.nan

    def lick_sum(self):
        """
        Calculate the total number of licks.

        Returns:
        - Total number of licks or NaN if no licks are detected
        """
        return len(self.arr)
#         n_licks = []

#         if self.clusters:
#             for cluster in self.clusters:
#                 try:
#                     n_licks.append(len(cluster))
#                 except:
#                     n_licks.append(np.nan)
#             return np.nansum(n_licks)
#         else:
#             return np.nan

    def get_bout(self, bout_number):
        """
        Retrieve the number of licks for the specified bout.

        Parameters:
        - bout_number: The index of the bout to retrieve (0-based index)

        Returns:
        - Number of licks in the specified bout or NaN if the bout is not available
        """
        if 0 <= bout_number < len(self.clusters) and not np.isnan(self.clusters[bout_number][0]):
            return len(self.clusters[bout_number])
        else:
            return np.nan
