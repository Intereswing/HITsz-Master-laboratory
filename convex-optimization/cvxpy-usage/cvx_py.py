import cvxpy as cp
import numpy as np

def pro_1(sol: str):
    x_1 = cp.Variable()
    x_2 = cp.Variable()

    constraints = [
        2*x_1 + x_2 >= 1,
        x_1 + 3*x_2 >= 1,
        x_1 >= 0,
        x_2 >= 0
    ]
    obj = cp.Maximize(-x_1 - x_2)
    prob = cp.Problem(obj, constraints)

    prob.solve(solver=sol)
    print(f'problem 1(solver = {sol}):')
    print('status:', prob.status)
    print('period:', prob.compilation_time)
    print('optimal value:', prob.value)
    print('optimal var', x_1.value, x_2.value)
    print()

def pro_2(sol: str):
    x = cp.Variable(2)
    A = np.array([[1, 1], [-1, 2], [2, 1]])
    b = np.array([2, 2, 3])
    Q = np.array([[2, 0], [0, 2]])
    c = np.array([-2, -6])

    constraints = [A@x <= b]
    obj = cp.Minimize(x@Q@x/2 + c@x)
    prob = cp.Problem(obj, constraints)

    prob.solve(solver=sol)
    print(f'problem 2(solver = {sol}):')
    print('status:', prob.status)
    print('period:', prob.compilation_time)
    print('optimal value:', prob.value)
    print('optimal var', x.value)
    print()

def pro_3(sol: str):
    x_1 = cp.Variable()
    x_2 = cp.Variable()

    constraints = [x_1**2 + x_2**2 <= 1,
                   x_1 + x_2 <= 0]
    obj = cp.Minimize(x_1**2 + x_2**2 + 2*x_1 + 4*x_2)
    prob = cp.Problem(obj, constraints)

    prob.solve(solver=sol)
    print(f'problem 3(solver = {sol}):')
    print('status:', prob.status)
    print('period:', prob.compilation_time)
    print('optimal value:', prob.value)
    print('optimal var', x_1.value, x_2.value)
    print()

if __name__ == '__main__':
    solvers = ['ECOS', 'SCS', 'CVXOPT']
    problems = [pro_1, pro_2, pro_3]
    for problem in problems:
        for solver in solvers:
            problem(solver)


