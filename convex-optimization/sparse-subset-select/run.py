import time
import numpy as np
from numpy import ndarray

from opt_algos import Grad_Descend, Steepest_Descend, Newton_Descend, test_result, Coordinator_Descend, Lagrange_Duel

def show_result(X, beta_star, y, iteration):
    MSE, norm0, norm1, norm2 = test_result(X, beta_star, y)
    print("Iteration:", iteration)
    print("beta:", beta_star)
    print("MSE:", MSE)
    print("norm0:", norm0)
    print("norm1:", norm1)
    print("norm2:", norm2)

lamb1 = 0.01
lamb2 = 0.01
eta = 0.01
epsilon = 1e-5


# beta_star, iteration = Coordinator_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
lagrange_flag = False
if lagrange_flag:
    # Lagrange Duel
    k = 30
    v_0 = 0

    print("lagrange, 100 * 20")
    load = np.load("data/X100y20.npz")
    X: ndarray = load['X']
    y: ndarray = load['y']
    beta_0 = np.zeros(X.shape[1])

    t = time.time()
    beta_star, iteration = Lagrange_Duel(X, beta_0, y, v_0, k, eta, epsilon)
    t_end = time.time()
    print(f"100 * 20 Time:{t_end - t} s")
    show_result(X, beta_star, y, iteration)

    print("lagrange, 300 * 50")
    load = np.load("data/X300y50.npz")
    X: ndarray = load['X']
    y: ndarray = load['y']
    beta_0 = np.zeros(X.shape[1])

    t = time.time()
    beta_star, iteration = Lagrange_Duel(X, beta_0, y, v_0, k, eta, epsilon)
    t_end = time.time()
    print(f"300 * 50 Time:{(t_end - t)} s")
    show_result(X, beta_star, y, iteration)

    print("lagrange, 500 * 100")
    load = np.load("data/X500y100.npz")
    X: ndarray = load['X']
    y: ndarray = load['y']
    beta_0 = np.zeros(X.shape[1])

    t = time.time()
    beta_star, iteration = Lagrange_Duel(X, beta_0, y, v_0, k, eta, epsilon)
    t_end = time.time()
    print(f"500 * 100 Time:{(t_end - t)} s")
    show_result(X, beta_star, y, iteration)

Grad_Descend_flag = False
if Grad_Descend_flag:
    load = np.load("data/X300y50.npz")
    X: ndarray = load['X']
    y: ndarray = load['y']
    beta_0 = np.zeros(X.shape[1])

    print("Grad Descend, lamb1 = 0.01, lamb2 = 0.01")
    beta_star, iteration = Grad_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Grad Descend, lamb1 = 0.1, lamb2 = 0.1")
    beta_star, iteration = Grad_Descend(X, beta_0, y, 0.1, 0.1, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Grad Descend, lamb1 = 0.001, lamb2 = 0.001")
    beta_star, iteration = Grad_Descend(X, beta_0, y, 0.001, 0.001, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Grad Descend, lamb1 = 0.01, lamb2 = 0.01, eta = 0.001, epsilon = 1e-5")
    beta_star, iteration = Grad_Descend(X, beta_0, y, lamb1, lamb2, 0.001, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Grad Descend, lamb1 = 0.01, lamb2 = 0.01, eta = 0.001, epsilon = 1e-7")
    beta_star, iteration = Grad_Descend(X, beta_0, y, lamb1, lamb2, 0.001, 1e-7)
    show_result(X, beta_star, y, iteration)

Steepest_Descend_flag = False
if Steepest_Descend_flag:
    load = np.load("data/X300y50.npz")
    X: ndarray = load['X']
    y: ndarray = load['y']
    beta_0 = np.zeros(X.shape[1])

    print("Steepest_Descend, lamb1 = 0.01, lamb2 = 0.01")
    beta_star, iteration = Steepest_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Steepest_Descend, lamb1 = 0.1, lamb2 = 0.1")
    beta_star, iteration = Steepest_Descend(X, beta_0, y, 0.1, 0.1, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Steepest_Descend, lamb1 = 0.001, lamb2 = 0.001")
    beta_star, iteration = Steepest_Descend(X, beta_0, y, 0.001, 0.001, eta, epsilon)
    show_result(X, beta_star, y, iteration)

Newton_Descend_flag = False
if Newton_Descend_flag:
    load = np.load("data/X300y50.npz")
    X: ndarray = load['X']
    y: ndarray = load['y']

    print("Newton_Descend, beta_0 = 0")
    beta_0 = np.zeros(X.shape[1])
    beta_star, iteration = Newton_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Newton_Descend, beta_0 = (X.T @ X).I @ X.T @ y")
    beta_0 = np.linalg.inv(X.transpose() @ X) @ X.transpose() @ y
    beta_star, iteration = Newton_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Newton_Descend, beta_0 = 0, lamb1 = 0.1, lamb2 = 0.1")
    beta_0 = np.zeros(X.shape[1])
    beta_star, iteration = Newton_Descend(X, beta_0, y, 0.1, 0.1, eta, epsilon)
    show_result(X, beta_star, y, iteration)

Coordinator_Descend_flag = True
if Coordinator_Descend_flag:
    load = np.load("data/X300y50.npz")
    X: ndarray = load['X']
    y: ndarray = load['y']
    beta_0 = np.zeros(X.shape[1])

    print("Coordinator_Descend, lamb1 = 0.01, lamb2 = 0.01")
    beta_star, iteration = Coordinator_Descend(X, beta_0, y, lamb1, lamb2, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Coordinator_Descend, lamb1 = 0.1, lamb2 = 0.1")
    beta_star, iteration = Coordinator_Descend(X, beta_0, y, 0.1, 0.1, eta, epsilon)
    show_result(X, beta_star, y, iteration)

    print("Coordinator_Descend, lamb1 = 0.001, lamb2 = 0.001")
    beta_star, iteration = Coordinator_Descend(X, beta_0, y, 0.001, 0.001, eta, epsilon)
    show_result(X, beta_star, y, iteration)




