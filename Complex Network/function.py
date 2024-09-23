import numpy as np
import matplotlib.pyplot as plt
from numpy import ndarray
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
    return total_length / count if count > 0 else 0


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


# largest subgraph size
def largest_subgraph(G: ndarray):
    largest = 0
    nodes_number = len(G[0])
    all_nodes = [i for i in range(nodes_number)]

    while len(all_nodes) > 0:
        stack = [all_nodes[0]] # next subgraph
        visited = []
        while stack: # subgraph include all_nodes[0]
            node = stack.pop()
            if node not in visited:
                visited.append(node)
                all_nodes.remove(node)
                stack.extend([i for i in all_nodes if G[node][i] > 0])
        largest =max(largest, len(visited)) # compare this subgraph's size with previous largest size.

    return largest


def coreness(G: ndarray):
    all_nodes = np.array([i for i in range(len(G[0]))])
    coreness_list = [] # coreness_list[i] is a list of all nodes that has coreness i.
    coreness_value = 1
    while len(all_nodes) > 0:
        coreness_list.append([])
        HasCoreness = True # Indicate that maybe there are more nodes has coreness coreness_value.

        while HasCoreness:
            G_coreness = G[all_nodes, :][:, all_nodes]
            degree_list = list(G_coreness.sum(axis=0))
            indices_coreness = [i for i, degree in enumerate(degree_list) if degree < coreness_value]
            if len(indices_coreness) == 0:
                HasCoreness = False

            coreness_list[coreness_value-1].extend(all_nodes[indices_coreness])
            all_nodes = np.delete(all_nodes, indices_coreness)

        coreness_value += 1
    return coreness_list


def attack_random(G: ndarray, attack_proportions: ndarray):
    all_nodes = np.array([i for i in range(G.shape[0])])
    attack_node_numbers = (G.shape[0] * attack_proportions).astype(int)
    paths = []
    sub_graphs = []
    for att_node_num in attack_node_numbers:
        res_nodes = np.random.choice(all_nodes, G.shape[0]-att_node_num, replace=False)
        res_G = G[res_nodes, :][:, res_nodes]
        paths.append(average_shortest_path_length(res_G))
        sub_graphs.append(largest_subgraph(res_G))

    origin_path = paths[0]
    origin_sgs = sub_graphs[0]
    return np.array([path/origin_path for path in paths]), np.array([sgs/origin_sgs for sgs in sub_graphs])


def attack_intentional(G: ndarray, attack_proportions: ndarray):
    degree_list = np.sum(G, axis=1)
    nodes_by_degree = np.argsort(degree_list) # Increasing

    attack_node_numbers = (G.shape[0] * attack_proportions).astype(int)
    paths = []
    sub_graphs = []

    for att_node_num in attack_node_numbers:
        if att_node_num > 0:
            res_nodes = nodes_by_degree[:-att_node_num]
        else:
            res_nodes = nodes_by_degree
        res_G = G[res_nodes, :][:, res_nodes]
        paths.append(average_shortest_path_length(res_G))
        sub_graphs.append(largest_subgraph(res_G))

    origin_path = paths[0]
    origin_sgs = sub_graphs[0]
    return np.array([path/origin_path for path in paths]), np.array([sgs/origin_sgs for sgs in sub_graphs])


def visualization_attack(attack_proportions, random_attack, intentional_attack, attr):
    plt.scatter(attack_proportions, random_attack, label='Random failure', color='blue', marker='o')
    plt.scatter(attack_proportions, intentional_attack, label='Intentional attack', color='red', marker='s')

    plt.xlabel('Attack Proportion')
    plt.ylabel(attr)
    plt.title('Robustness')
    plt.legend()
    plt.show()


def visualization_coreness(coreness_list):
    x = np.arange(len(coreness_list))
    y = np.array([len(nodes) for nodes in coreness_list])
    plt.bar(x, y)

    plt.xlabel('Coreness')
    plt.ylabel('Number of Nodes')
    plt.show()


# TEST
if __name__ == '__main__':
    sample_graph = np.array([[0,1,0,0,1],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,1],[1,1,0,1,0]])
    print(largest_subgraph(sample_graph))
    print(coreness(sample_graph))

    attack_pros = np.linspace(0, 1, 5, endpoint=False)
    random_attack_paths, random_attack_sgs = attack_random(sample_graph, attack_pros)
    intentional_attack_paths, intentional_attack_sgs = attack_intentional(sample_graph, attack_pros)
    print('random_attack_paths')
    print(random_attack_paths)
    print("random_attack_sgs")
    print(random_attack_sgs)
    print('intentional_attack_paths')
    print(intentional_attack_paths)
    print('intentional_attack_sgs')
    print(intentional_attack_sgs)

    visualization_attack(
        attack_proportions=attack_pros,
        random_attack=random_attack_paths,
        intentional_attack=intentional_attack_paths,
        attr='Average Shortest Path Length'
    )
    visualization_attack(
        attack_proportions=attack_pros,
        random_attack=random_attack_sgs,
        intentional_attack=intentional_attack_sgs,
        attr='Largest Subgraph'
    )
    visualization_coreness(coreness(sample_graph))
