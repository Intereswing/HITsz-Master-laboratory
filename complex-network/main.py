import numpy as np
import function as f

G = np.load('data/adjacent_matrix.npy')
f.visualization_graph(G)

degree_count = f.node_degree_distribution(G)
f.visualization_distribution(degree_count, 10, 'Degree')

avg_path_len, length_count = f.average_shortest_path_length(G)
f.visualization_distribution(length_count, 50, 'Length')
print(avg_path_len)

print(f.average_clustering_coefficient(G))

attack_pros = np.linspace(0, 1, 100, endpoint=False)
random_attack_paths, random_attack_sgs = f.attack_random(G, attack_pros)
intentional_attack_paths, intentional_attack_sgs = f.attack_intentional(G, attack_pros)
f.visualization_attack(
    attack_proportions=attack_pros,
    random_attack=random_attack_paths,
    intentional_attack=intentional_attack_paths,
    attr='Average Shortest Path Length'
)
f.visualization_attack(
    attack_proportions=attack_pros,
    random_attack=random_attack_sgs,
    intentional_attack=intentional_attack_sgs,
    attr='Largest Subgraph'
)
f.visualization_coreness(f.coreness(G))