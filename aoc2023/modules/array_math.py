# array math
from functools import reduce
from typing import TypeVar

T = TypeVar("T")

# add to each element in an array
def add(arr: list[T], num: T) -> list[T]:
    return [val + num for val in arr]

# multiply each element in an array
def mult(arr: list[T], num: T) -> list[T]:
    return [val * num for val in arr]

# product of all elements in the array
def product(arr: list[T]) -> T:
    return reduce(lambda a,b: a*b, arr)

# add two arrays of same length element-wise
def addwise(arr1: list[T], arr2: list[T]) -> list[T]:
    return [a + b for (a,b) in zip(arr1,arr2)]

# subtracts elements which are idx_shift apart
# ex: arr=[1,3,6,10,15], idx_shift=2, result=[5,7,9] ([6 - 1, 10 - 3, 15 - 6])
def shifted_diff(arr: list[T], idx_shift: int) -> list[T]:
    return [arr[idx] - arr[idx - idx_shift] for idx in range(idx_shift, len(arr))]
