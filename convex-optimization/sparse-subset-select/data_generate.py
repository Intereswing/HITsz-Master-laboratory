import numpy as np

#np.random.seed(1)
for n_samples, n_features in [(100, 20), (300, 50), (500, 100)]:
    X = np.random.randn(n_samples, n_features)

    # ⽣成稀疏系数
    beta_true = np.zeros(n_features)
    non_zero_indices = np.random.choice(n_features, size=int(n_features/5), replace=False)
    beta_true[non_zero_indices] = np.random.randn(int(n_features/5))

    # ⽣成⽬标变量
    y = X.dot(beta_true) + 0.01 * np.random.randn(n_samples)
    np.savez(f"data/X{n_samples}y{n_features}.npz", X=X, y=y)
