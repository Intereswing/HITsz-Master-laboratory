import numpy as np

#np.random.seed(1)
n_samples, n_features = 300, 50
X = np.random.randn(n_samples, n_features)

# ⽣成稀疏系数
beta_true = np.zeros(n_features)
non_zero_indices = np.random.choice(n_features, size=10, replace=False)
beta_true[non_zero_indices] = np.random.randn(10)

# ⽣成⽬标变量
y = X.dot(beta_true) + 0.01 * np.random.randn(n_samples)