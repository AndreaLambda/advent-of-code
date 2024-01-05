# day 11: galaxies
import re
from functools import reduce
from itertools import combinations
from modules.parse import get_input

def to_row_col(loc, cols):
    # add 1 for the newline character
    row_len = cols + 1
    loc_col = loc % row_len
    loc_row = int((loc - loc_col) / row_len)
    return (loc_row, loc_col)

def missing(idxs, len_idx):
    full_set = set(range(len_idx))
    idx_set = set(idxs)
    return sorted(list(full_set - idx_set))

# preserves initial ordering of idxs
def expand_dim(idxs, len_idx, ratio):
    total = 0
    missing_idxs = missing(idxs, len_idx)
    new_idxs = {old_idx: old_idx + ratio * len([idx for idx in missing_idxs if idx < old_idx]) for old_idx in idxs}
    return ([new_idxs[old_idx] for old_idx in idxs], len_idx + ratio * len(missing_idxs))
    
def expand_universe(galaxies, rows, cols, ratio):
    (new_row_nums, new_rows) = expand_dim([row_num for (row_num, _) in galaxies], rows, ratio)
    (new_col_nums, new_cols) = expand_dim([col_num for (_, col_num) in galaxies], cols, ratio)
    # can use zip, since initial orderings are preserved
    new_galaxies = list(zip(new_row_nums, new_col_nums))
    return (new_galaxies, new_rows, new_cols)
    
def parse_input(input):
    lines = input.splitlines()
    num_rows = len(lines)
    num_cols = len(lines[0])

    raw_locs = [m.start() for m in re.finditer("#", input)]
    galaxies = [to_row_col(loc, num_cols) for loc in raw_locs]
    return (galaxies, num_rows, num_cols)

def dist(a, b):
    return abs(b[1]-a[1]) + abs(b[0]-a[0])

def sum(list):
    return reduce(lambda x,y: x+y, list)

def calc_distance(galaxies):
    dists = [dist(a,b) for (a,b) in combinations(galaxies, 2)]
    return sum(dists)

def process_input(input, ratio=2):
    (galaxies, num_rows, num_cols) = parse_input(input)
    (galaxies, num_rows, num_cols) = expand_universe(galaxies, num_rows, num_cols, ratio-1)
    return calc_distance(galaxies)

# process_input(get_input(11, test=True))
# process_input(get_input(11))
# process_input(get_input(11, test=True), ratio=100)
process_input(get_input(11), ratio=1_000_000)