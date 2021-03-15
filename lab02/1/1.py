import numpy as np


M = np.arange(2, 27)
print(M)
print()

M = M.reshape(5, 5)
print(M)
print()

M[1:-1, 1:-1] = 0
print(M)
print()

M = M.dot(M)
print(M)
print()

v = M[0, :]
print(np.sqrt(np.sum(v ** 2)))
