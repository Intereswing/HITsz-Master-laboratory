from turtledemo.penrose import start

import numpy as np

def Lagrange_Min_P(p, eta, c_hat, v, alpha, It):
    p_min = (p ** (1/alpha - 1) + eta * c_hat - eta * v) ** (alpha / (1 - alpha))

    value = c_hat[It] * p_min[It]
    value += ((1/eta) *
              (-alpha * np.sum(p_min ** (1 / alpha)) +
               (alpha - 1) * np.sum(p ** (1 / alpha)) +
               np.sum(p_min * p ** (1 / alpha - 1))))
    value += v * (np.sum(p_min) - 1)
    return value, p_min

def KKT(p, eta, c_hat, v, alpha, It):
    p_min = (p ** (1 / alpha - 1) + eta * c_hat - eta * v) ** (alpha / (1 - alpha))
    original_feasible = np.sum(p_min) - 1
    return p_min, original_feasible

alpha = 2
K = 20
T = 10000
eta = 1/np.sqrt(T)
epsilon = 1e-6

C = np.loadtxt('Loss_matrix.txt')

p = np.full(K, 1/K)
result_cost = 0
fix_choice_cost = np.zeros(K)

for _ in range(10):
    for i in range(C.shape[0]):
        It = np.argmax(p)
        c = C[i, :]
        result_cost += c[It]
        fix_choice_cost += c

        c_hat = np.zeros_like(c)
        if p[It] >= eta:
            c_hat[It] = c[It] / p[It]
        else:
            c_hat[It] = c[It] / (p[It] + eta)

        # Binary search for argmax Lagrange.
        start = 0
        end = c_hat[It]
        while end - start > epsilon:
            mid = (start + end) / 2
            _, orig_feasible = KKT(p, eta, c_hat, mid, alpha, It)
            if orig_feasible > 0:
                end = mid
            else:
                start = mid

        v = (start + end) / 2
        p, _ = KKT(p, eta, c_hat, v, alpha, It)
        p = p / np.sum(p)



print("p_10001:", p)
print("result cost:", result_cost / 10)
print("fix choice cost:", fix_choice_cost / 10)

