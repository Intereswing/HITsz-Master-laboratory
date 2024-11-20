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
    grad = X@beta
    grad = grad - y
    grad = X.transpose() @ grad
    grad = (1/N) * grad
    grad = grad + 2 * lamb2 * beta
    # grad = (1/N) * X.transpose() @ (X@beta - y) + 2*lamb2*beta

    # sub-gradient of norm1.
    norm1_grad = np.select([beta<0, beta==0, beta>0], [-1, 0, 1], 0) * lamb1

    return grad + norm1_grad


def Hessian(X: ndarray, beta, y, lamb1, lamb2):
    N = X.shape[0]
    d = beta.shape[0]
    return (1/N) * X.transpose() @ X + 2*lamb2*np.eye(d)


def test_result(X: ndarray, beta, y):
    N = X.shape[0]
    MSE = 1 / (2 * N) * np.sum((X @ beta - y) ** 2)
    norm0 = np.count_nonzero(beta)
    norm1 = np.sum(np.abs(beta))
    norm2 = np.sum(beta**2)

    return MSE, norm0, norm1, norm2


def Grad_Descend(X: ndarray, beta: ndarray, y, lamb1, lamb2, eta, epsilon, max_iteration=10000):
    iteration = 0

    beta = beta.copy()
    f = evaluate_func(X, beta, y, lamb1, lamb2)

    beta_new = beta - eta * gradient(X, beta, y, lamb1, lamb2)
    f_new = evaluate_func(X, beta_new, y, lamb1, lamb2)
    # Sparse select: remove small absolute value.
    beta_star = np.where(np.abs(beta_new) < 1e-3, 0, beta_new)
    f_star = evaluate_func(X, beta_star, y, lamb1, lamb2)


    while (abs(f_new - f) > epsilon or abs(f_star - f_new) > epsilon)  and  iteration < max_iteration:
        beta, f = beta_new, f_new
        beta_new = beta - eta * gradient(X, beta, y, lamb1, lamb2)
        f_new = evaluate_func(X, beta_new, y, lamb1, lamb2)
        beta_star = np.where(np.abs(beta_new) < 1e-3, 0, beta_new)
        f_star = evaluate_func(X, beta_star, y, lamb1, lamb2)

        iteration += 1

    return beta_star, iteration
















