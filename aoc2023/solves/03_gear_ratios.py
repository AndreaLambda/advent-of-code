# day 3: gear ratios
import re
from modules.parse import get_input

# 3-1
def find_numbers(input):
    res = []
    for (idx, row) in enumerate(input):
        checks = re.finditer(r"[\d]+", row)
        res += [(idx, *m.span(0), int(m.group(0))) for m in checks]
    return res

def check_if_part(input, rownum, start, end, num):
    col_start = max(start - 1, 0)
    col_end = min(end + 1, len(input[0]))
    row_start = max(rownum - 1, 0)
    row_end = min(rownum + 1, len(input) - 1)
    check = "".join([input[row][col_start:col_end] for row in range(row_start, row_end + 1)])
    return num if re.search(r"[^\d\.]", check) else None

def find_parts(input):
    res = find_numbers(input)
    res = [check_if_part(input, *check) for check in res]
    res = [part for part in res if part]
    res = sum(res)
    return res

# 3-2
def find_stars(input):
    res = []
    for (idx, row) in enumerate(input):
        checks = re.finditer(r"\*", row)
        res += [(idx, m.span(0)[0]) for m in checks]
    return res

def check_if_gear(star, nums):
    res = [num[3] for num in nums
        if star[0]-1 <= num[0] <= star[0]+1
        and num[1] <= star[1]+1
        and num[2] >= star[1]]
    return res[0]*res[1] if len(res) == 2 else None
    
def find_gears(input):
    nums = find_numbers(input)
    stars = find_stars(input)
    res = [check_if_gear(star, nums) for star in stars]
    res = [gear for gear in res if gear]
    res = sum(res)
    return res

def process_input(input, gears=False):
    input = input.splitlines()
    if gears:
        return find_gears(input)
    else:
        return find_parts(input)

# process_input(get_input(3, True))
# process_input(get_input(3))
# process_input(get_input(3, True), True)
process_input(get_input(3), True)