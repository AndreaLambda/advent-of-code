# day 6: quadratic races
import re
from math import ceil
from modules.array_math import product
from modules.parse import get_input
from modules.utils import quad

# 6-1
"""
    time = t + t_move ("t" is time spent charging which we solve for, "time" is total race time from input)
    dist = speed * t_move
         = t * t_move
         = t * (time - t)
    dist = t * time - t^2
       0 = -t^2 + t*time - dist, use quadratic formula to solve for t
"""
def get_wins(time: int, dist: int) -> int:
    (t_min, t_max) = quad(-1, time, -dist)
    # next integer value greater than t_min (race is a tie if t_min is already an int)
    t_min = ceil(t_min) if ceil(t_min) > t_min else ceil(t_min) + 1
    t_max = time - t_min
    return t_max - t_min + 1

def parse_line(line: str) -> list[int]:
    return [int(num) for num in re.split(r"[ ]+", line)[1:]]
        
def process_input(input: str, parser: callable):
    input = input.splitlines()
    times, dists = [parser(line) for line in input]
    wins = [get_wins(time, dist) for (time, dist) in zip(times, dists)]
    return product(wins) 

# 6-2
def parse_kerning(line: str) -> list[int]:
    line = line.replace(" ","")
    return [int(line.split(":")[1])]

# process_input(get_input(6, test=True), parse_line)
# process_input(get_input(6), parse_line)
# process_input(get_input(6, test=True), parse_kerning)
process_input(get_input(6), parse_kerning)