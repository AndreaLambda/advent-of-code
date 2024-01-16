from math import sqrt

### array utils
def rev(x):
    return x[::-1]

def filter_none[T](arr: list[T]) -> list[T]:
    return [x for x in arr if x is not None]

def flatten(arr):
    return [x for sub_arr in arr for x in sub_arr]

### math utils
# quadratic formula
def quad(a,b,c):
    left = -b / (2*a)
    right = sqrt(b*b - 4*a*c) / (2*a)
    return (left+right, left-right)

# -1 if negative, +1 if positive, 0 if zero
def sign(num: int) -> int:
    return num // abs(num) if num != 0 else 0
