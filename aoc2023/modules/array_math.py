# array math
from functools import reduce

# add to each element in an array
def add(arr: list[int], num: int) -> list[int]:
    return [val + num for val in arr]

# product of all elements in the array
def product(arr: list[int]) -> int:
    return reduce(lambda a,b: a*b, arr)