import numpy as np
from opt_algos import Grad_Descend, test_result

lamb1 = 0.01
lamb2 = 0.01
eta = 0.01
epsilon = 1e-5

load = np.load("data/X300y50.npz")
X = load['X']
y = load['y']

beta_0 = np.zeros(X.shape[1])
beta_star, iteration = Grad_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
MSE, norm0, norm1, norm2 = test_result(X, beta_star, y)
print("Iteration:", iteration)
print("beta:", beta_star)
print("MSE:", MSE)
print("norm0:", norm0)
print("norm1:", norm1)
print("norm2:", norm2)


