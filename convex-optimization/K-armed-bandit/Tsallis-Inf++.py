import numpy as np

# Haven't used
def Lagrange_Min_P(p, eta, c_hat, v, alpha, It):
    p_min = (p ** (1/alpha - 1) + eta * c_hat + eta * v) ** (alpha / (1 - alpha))

    value = c_hat[It] * p_min[It]
    value += ((1/eta) *
              (-alpha * np.sum(p_min ** (1 / alpha)) +
               (alpha - 1) * np.sum(p ** (1 / alpha)) +
               np.sum(p_min * p ** (1 / alpha - 1))))
    value += v * (np.sum(p_min) - 1)
    return value, p_min


def KKT(p, eta, c_hat, v, alpha, It):
    p_min = (p ** (1 / alpha - 1) + eta * c_hat + eta * v) ** (alpha / (1 - alpha))
    original_feasible = np.sum(p_min) - 1
    return p_min, original_feasible


def tsallis_inf_once(C, alpha, epsilon, p=None):
    T, K = C.shape
    eta = 1/np.sqrt(T)
    if p is None:
        p = np.full(K, 1 / K)
    result_cost = 0
    fix_choice_cost = np.zeros(K)

    for i in range(T):
        It = np.random.choice(K, p=p)
        c = C[i, :]
        result_cost += c[It]
        fix_choice_cost += c

        c_hat = np.zeros_like(c)
        if p[It] >= eta:
            c_hat[It] = c[It] / p[It]
        else:
            c_hat[It] = c[It] / (p[It] + eta)

        # Binary search for argmax Lagrange.
        start = -c_hat[It]
        end = 0
        while end - start > epsilon:
            mid = (start + end) / 2
            _, orig_feasible = KKT(p, eta, c_hat, mid, alpha, It)
            if orig_feasible > 0:
                start = mid
            else:
                end = mid

        v = (start + end) / 2
        p, _ = KKT(p, eta, c_hat, v, alpha, It)
        p = p / np.sum(p)
    return p, result_cost, fix_choice_cost


if __name__ == '__main__':
    C = np.loadtxt('Loss_matrix.txt')
    T, K = C.shape
    alpha = 2
    epsilon = 1e-5

    print("Independently run 10 times.")
    result_p = np.zeros(K)
    result_cost = 0
    fix_choice_cost = np.zeros(K)
    for _ in range(10):
        result_p_i, result_cost_i, fix_choice_cost_i = tsallis_inf_once(C, alpha, epsilon)
        result_p += result_p_i
        result_cost += result_cost_i
        fix_choice_cost += fix_choice_cost_i
    print("p_10001:", result_p / 10)
    print("result cost:", result_cost / 10)
    print("fix choice cost:", fix_choice_cost / 10)

    print("")
    print("Sequentially run 10 times.")
    p = np.full(K, 1 / K)
    for _ in range(10):
        p, result_cost, fix_choice_cost = tsallis_inf_once(C, alpha, epsilon, p=p)
    print("p_10001:", p)
    print("result cost:", result_cost)
    print("fix choice cost:", fix_choice_cost)



