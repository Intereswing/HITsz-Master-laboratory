import numpy as np
from numpy import ndarray

from opt_algos import Grad_Descend, Steepest_Descend, Newton_Descend, test_result, Coordinator_Descend, Lagrange_Duel

lamb1 = 0.01
lamb2 = 0.01
eta = 0.01
epsilon = 1e-6
k = 30

load = np.load("data/X300y50.npz")
X: ndarray = load['X']
y: ndarray = load['y']

beta_0 = np.zeros(X.shape[1])
v_0 = 0
# beta_0 = np.linalg.inv(X.transpose() @ X) @ X.transpose() @ y
# beta_star, iteration = Grad_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
# beta_star, iteration = Steepest_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
# beta_star, iteration = Newton_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
# beta_star, iteration = Coordinator_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
beta_star, iteration = Lagrange_Duel(X, beta_0, y, v_0, k, eta, epsilon)
MSE, norm0, norm1, norm2 = test_result(X, beta_star, y)
print("Iteration:", iteration)
print("beta:", beta_star)
print("MSE:", MSE)
print("norm0:", norm0)
print("norm1:", norm1)
print("norm2:", norm2)


