import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def node_degree_distribution(adj_G):
    degree_array = np.sum(adj_G, axis=1)
    degree_count = {}
    for degree in degree_array:
        if degree in degree_count:
            degree_count[degree] += 1
        else:
            degree_count[degree] = 1

    sorted_degree = sorted(degree_count.keys())
    sorted_count = [degree_count[sort] for sort in sorted_degree]

    max_degree = max(sorted_degree)
    max_node = max(sorted_count)
    degrees_range = np.arange(0, max_degree + 1)
    node_range = np.arange(0, max_node + 1)
    plt.bar(sorted_degree, sorted_count)
    plt.xticks(degrees_range)
    plt.yticks(node_range)
    plt.xlabel('Degree')
    plt.ylabel('Number of Nodes')
    plt.title('Degree Distribution')
    plt.show()


def floyd_warshall(adj_matrix):
    # 邻接矩阵的大小
    n = adj_matrix.shape[0]

    # 初始化距离矩阵，inf 表示不可达
    dist_matrix = np.full((n, n), float('inf'))

    # 将邻接矩阵转化为距离矩阵，1 表示有边，0 表示无边
    for i in range(n):
        for j in range(n):
            if i == j:
                dist_matrix[i][j] = 0  # 自己到自己的距离为 0
            elif adj_matrix[i][j] != 0:
                dist_matrix[i][j] = 1  # 有边的地方距离为 1

    # Floyd-Warshall 算法
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist_matrix[i][j] > dist_matrix[i][k] + dist_matrix[k][j]:
                    dist_matrix[i][j] = dist_matrix[i][k] + dist_matrix[k][j]

    return dist_matrix


def average_shortest_path_length(adj_matrix):
    dist_matrix = floyd_warshall(adj_matrix)
    n = adj_matrix.shape[0]

    total_length = 0
    count = 0

    # 计算所有可达节点之间的最短路径和总数
    for i in range(n):
        for j in range(i + 1, n):
            if dist_matrix[i][j] < float('inf'):
                total_length += dist_matrix[i][j]
                count += 1

    # 返回平均最短路径长度
    return total_length / count if count > 0 else float('inf')




# 计算给定节点的聚类系数
def clustering_coefficient_for_node(adj_G, node):
    neighbors = [i for i, val in enumerate(adj_G[node]) if val == 1]
    num_neighbors = len(neighbors)

    if num_neighbors < 2:
        # 如果邻居少于2个，聚类系数为0
        return 0.0

    # 计算邻居之间的连接数
    edges_between_neighbors = 0
    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            if adj_G[neighbors[i], neighbors[j]] == 1:
                edges_between_neighbors += 1

    # 计算可能的最大连接数，即 C(num_neighbors, 2) = num_neighbors * (num_neighbors - 1) / 2
    possible_connections = num_neighbors * (num_neighbors - 1) / 2

    # 聚类系数为邻居间的实际连接数除以可能的最大连接数
    return edges_between_neighbors / possible_connections


# 计算整个图的平均聚类系数
def average_clustering_coefficient(adj_G):
    total_clustering = 0.0
    num_nodes = adj_G.shape[0]

    for node in range(num_nodes):
        total_clustering += clustering_coefficient_for_node(adj_G, node)

    return total_clustering / num_nodes

