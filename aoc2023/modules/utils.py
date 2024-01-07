from itertools import islice, tee
from math import sqrt

### array utils
def rev(x):
    return x[::-1]

def filter_none(arr: list) -> list:
    return [x for x in arr if x is not None]

def flatten(arr):
    return [x for sub_arr in arr for x in sub_arr]

### iter utils
# from https://docs.python.org/3/library/itertools.html#itertools.batched
def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch

# from https://docs.python.org/3/library/itertools.html#itertools.pairwise
def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

### math utils
# quadratic formula
def quad(a,b,c):
    left = -b / (2*a)
    right = sqrt(b*b - 4*a*c) / (2*a)
    return (left+right, left-right)

# -1 if negative, +1 if positive, 0 if zero
def sign(num: int) -> int:
    return num // abs(num) if num != 0 else 0
