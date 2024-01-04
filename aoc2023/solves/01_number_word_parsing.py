# day 1: number word parsing
import re
from modules.parse import get_input
from modules.utils import rev

nums = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
nums_rev = {rev(k): v for (k,v) in nums.items()}

def get_first(line, parse_nums):
    numstr = f"|{('|').join(list(nums))}" if parse_nums else ""
    res = re.search(rf"([\d]{numstr})", line, flags=re.ASCII).group(0)
    return nums.get(res) or int(res)

def get_last(line, parse_nums):
    numstr = f"|{('|').join(list(nums_rev))}" if parse_nums else ""
    res = re.search(rf"([\d]{numstr})", rev(line), flags=re.ASCII).group(0)
    return nums_rev.get(res) or int(res)

def process_input(input, parse_nums=False):
    res = [10 * get_first(line, parse_nums) + get_last(line, parse_nums) for line in input.splitlines()]
    return sum(res)

# process_input(get_input(1, file="test_1"))
# process_input(get_input(1))
# process_input(get_input(1, file="test_2"), True)
process_input(get_input(1), True)