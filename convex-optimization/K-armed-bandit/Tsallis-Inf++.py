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
            mid_left = (start + end)/2 - (end - start)/20
            mid_right = (start + end)/2 + (end - start)/20
            f_left, _ = Lagrange_Min_P(p, eta, c_hat, mid_left, alpha, It)
            f_right, _ = Lagrange_Min_P(p, eta, c_hat, mid_right, alpha, It)
            if f_left > f_right:
                start = mid_left
            else:
                end = mid_right

        v = (start + end) / 2
        _, p = Lagrange_Min_P(p, eta, c_hat, v, alpha, It)
        p = p / np.sum(p)
    break


print("p_10001:", p)
print("result cost:", result_cost)
print("fix choice cost:", fix_choice_cost)

