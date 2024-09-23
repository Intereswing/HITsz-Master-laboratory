import pandas as pd
import numpy as np

# Formulate graph
routes = pd.read_csv('data/routes.dat', header=None)
# print(routes.iloc[7])

adjacent_matrix = np.zeros((0, 0))
airport_nodes = []
for line in routes.iterrows():
    if line[1][3] != '\\N' and line[1][5] != '\\N':
        if line[1][3] not in airport_nodes:
            airport_nodes.append(line[1][3])
            adjacent_matrix = np.vstack((adjacent_matrix, np.zeros((1, len(airport_nodes)-1))))
            adjacent_matrix = np.hstack((adjacent_matrix, np.zeros((len(airport_nodes), 1))))
        if line[1][5] not in airport_nodes:
            airport_nodes.append(line[1][5])
            adjacent_matrix = np.vstack((adjacent_matrix, np.zeros((1, len(airport_nodes)-1))))
            adjacent_matrix = np.hstack((adjacent_matrix, np.zeros((len(airport_nodes), 1))))
        adjacent_matrix[airport_nodes.index(line[1][3]), airport_nodes.index(line[1][5])] = 1
        adjacent_matrix[airport_nodes.index(line[1][5]), airport_nodes.index(line[1][3])] = 1

# print(len(set(list(routes[3]) + list(routes[5])))) # How many airports
np.save('data/adjacent_matrix.npy', adjacent_matrix)
print(adjacent_matrix.shape)
print(len(airport_nodes))
