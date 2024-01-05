from itertools import islice
from math import sqrt

### array utils
def rev(x):
    return x[::-1]

### iter utils
# from https://docs.python.org/3/library/itertools.html#itertools.batched
def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch

### math utils
# quadratic formula
def quad(a,b,c):
    left = -b / (2*a)
    right = sqrt(b*b - 4*a*c) / (2*a)
    return (left+right, left-right)
