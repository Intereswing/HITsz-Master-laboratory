import numpy as np
from numpy import ndarray
from scipy.optimize import direct


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


def Steepest_Descend(X: ndarray, beta: ndarray, y, lamb1, lamb2, eta, epsilon, max_iteration=10000):
    iteration = 1

    beta = beta.copy()
    f = evaluate_func(X, beta, y, lamb1, lamb2)
    golden = 0.618
    while True:
        direction = gradient(X, beta, y, lamb1, lamb2)
        step = eta
        # find the range of minimum
        while evaluate_func(X, beta - step * direction, y, lamb1, lamb2) < f:
            step = step/golden
        while evaluate_func(X, beta - golden * step * direction, y, lamb1, lamb2) > f:
            step = step * golden
        # golden search for the best step
        start = 0
        end = step
        golden_mid = step * golden
        while end - start > 1e-5:
            if golden_mid - start > end - golden_mid:
                golden_new = start + golden * (golden_mid - start)
                f_gold_mid = evaluate_func(X, beta - golden_mid * direction, y, lamb1, lamb2)
                f_gold_new = evaluate_func(X, beta - golden_new * direction, y, lamb1, lamb2)
                if f_gold_mid < f_gold_new:
                    start = golden_new
                else:
                    end = golden_mid
                    golden_mid = golden_new
            else:
                golden_new = end - golden * (end - golden_mid)
                f_gold_mid = evaluate_func(X, beta - golden_mid * direction, y, lamb1, lamb2)
                f_gold_new = evaluate_func(X, beta - golden_new * direction, y, lamb1, lamb2)
                if f_gold_mid < f_gold_new:
                    end = golden_new
                else:
                    start = golden_mid
                    golden_mid = golden_new
        step = golden_mid

        beta_new = beta - step * direction
        f_new = evaluate_func(X, beta_new, y, lamb1, lamb2)
        beta_star = np.where(np.abs(beta_new) < 1e-2, 0, beta_new)
        f_star = evaluate_func(X, beta_star, y, lamb1, lamb2)

        if (abs(f_new - f) > epsilon or abs(f_star - f_new) > epsilon)  and  iteration < max_iteration:
            beta, f = beta_new, f_new
            iteration += 1
        else:
            break

    return beta_star, iteration


def Newton_Descend(X: ndarray, beta: ndarray, y, lamb1, lamb2, eta, epsilon, max_iteration=10000):
    beta = beta.copy()
    f = evaluate_func(X, beta, y, lamb1, lamb2)

    iteration = 1
    while True:
        direction = np.linalg.inv(Hessian(X, beta, y, lamb1, lamb2)) @ gradient(X, beta, y, lamb1, lamb2)
        beta_new = beta - eta * direction
        f_new = evaluate_func(X, beta_new, y, lamb1, lamb2)
        # beta_star = np.where(np.abs(beta_new) < 1e-3, 0, beta_new)
        # f_star = evaluate_func(X, beta_star, y, lamb1, lamb2)

        if abs(f_new - f) > epsilon and iteration < max_iteration:
            beta, f = beta_new, f_new
            iteration += 1
        else:
            break

    beta_star = np.where(np.abs(beta_new) < 1e-2, 0, beta_new)
    return beta_star, iteration


def Coordinator_Descend(X: ndarray, beta: ndarray, y, lamb1, lamb2, eta, epsilon, max_iteration=10000):
    beta = beta.copy()
    f = evaluate_func(X, beta, y, lamb1, lamb2)

    iteration = 1
    while True:
        beta_new = beta.copy()
        # for every axis
        for i in range(beta.shape[0]):
            f_min = f
            beta_i = beta[i]
            # search min in [-eta, eta]
            for step in np.linspace(-eta, eta, 11):
                beta[i] = beta_i + step
                if evaluate_func(X, beta, y, lamb1, lamb2) < f_min:
                    f_min = evaluate_func(X, beta, y, lamb1, lamb2)
                    beta_new[i] = beta[i]
            beta[i] = beta_i

        f_new = evaluate_func(X, beta_new, y, lamb1, lamb2)

        if abs(f_new - f) > epsilon and iteration < max_iteration:
            beta, f = beta_new, f_new
            iteration += 1
        else:
            break

    beta_star = np.where(np.abs(beta_new) < 1e-2, 0, beta_new)
    return beta_star, iteration


def Lagrange_Duel_Function(X: ndarray, beta: ndarray, y, v, k):
    N = X.shape[0]
    value = 1/(2*N) * np.sum((X@beta-y)**2)
    value += v*(np.sum(beta!=0) - k)
    return value


def Lagrange_Duel(X: ndarray, beta: ndarray, y, v, k, eta, epsilon, max_iteration=10000):
    beta = beta.copy()
    f = Lagrange_Duel_Function(X, beta, y, v, k)

    iteration = 1
    while True:
        while True:
            beta_new = beta.copy()
            # for every axis
            for i in range(beta.shape[0]):
                f_min = f
                beta_i = beta[i]
                # search min in [-eta, eta]
                for step in np.linspace(-eta, eta, 11):
                    beta[i] = beta_i + step
                    if Lagrange_Duel_Function(X, beta, y, v, k) < f_min:
                        f_min = Lagrange_Duel_Function(X, beta, y, v, k)
                        beta_new[i] = beta[i]
                beta[i] = beta_i

            f_new = Lagrange_Duel_Function(X, beta_new, y, v, k)

            if abs(f_new - f) > epsilon and iteration < max_iteration:
                beta, f = beta_new, f_new
                iteration += 1
            else:
                break
        beta_star = np.where(np.abs(beta_new) < 1e-2, 0, beta_new)

        v_new = max(v + eta * (np.sum(beta_star!=0) - k), 0)
        f_new = Lagrange_Duel_Function(X, beta_star, y, v_new, k)
        if abs(f_new - f) > epsilon and iteration < max_iteration:
            beta, f = beta_new, f_new
            iteration += 1
        else:
            break

    return beta_star, iteration

