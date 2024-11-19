import numpy as np
from numpy import ndarray


# f_1(beta) = ||X*beta||^2_2/2n + lamb1*||beta||_1 + lamb2*||beta||_2^2
def evaluate_func(X: ndarray, beta, y, lamb1, lamb2):
    N = X.shape[0]
    value = 1/(2*N) * np.sum((X@beta-y)**2)
    value = value + lamb1 * np.sum(np.abs(beta)) + lamb2 * np.sum(beta**2)
    return value


# get f_1'(beta)
def gradient(X: ndarray, beta, y, lamb1, lamb2):
    N = X.shape[0]
    grad = (1/N) * X.transpose() @ (X@beta - y) + 2*lamb2*beta

    # sub-gradient of norm1.
    norm1_grad = np.select([beta<0, beta==0, beta>0], [-1, 0, 1], 0) * lamb1

    return grad + norm1_grad


def Hessian(X: ndarray, beta, y, lamb1, lamb2):
    N = X.shape[0]
    d = beta.shape[0]
    return (1/N) * X.transpose() @ X + 2*lamb2*np.eye(d)


def Grad_Descend(X: ndarray, beta, y, lamb1, lamb2, eta, epsilon, max_iteration=5000):
    iteration = 0

    beta_k = beta.copy()
    f_k = evaluate_func(X, beta_k, y, lamb1, lamb2)

    while abs(f_k_plus - f_k) > epsilon and iteration < max_iteration:
        beta_k = beta_k_plus
        f_k = f_k_plus

        beta_k_plus = beta_k - eta * gradient(X, beta_k, y, lamb1, lamb2)
        f_k_plus = evaluate_func(X, beta_k_plus, y, lamb1, lamb2)
