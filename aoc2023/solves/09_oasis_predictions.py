# day 9: oasis predictions
from modules.parse import get_input
from modules.utils import pairwise

def parse_input(input):
    return [[int(num) for num in line.split(" ")] for line in input.splitlines()]

def get_diffs(values):
    diffs = [values]
    while any(num != 0 for num in diffs[-1]):
        diffs.append([v2 - v1 for (v1, v2) in pairwise(diffs[-1])])
    return diffs    

# 9-1
def predict_next(values):
    diffs = get_diffs(values)
    diff = 0
    for line in reversed(diffs):
        diff = diff + line[-1]
    return diff

# 9-2
def predict_prev(values):
    diffs = get_diffs(values)
    diff = 0
    for line in reversed(diffs):
        diff = line[0] - diff
    return diff

def process_input(input, predictor=predict_next):
    lines = parse_input(input)
    return sum([predictor(line) for line in lines])

# process_input(get_input(9, test=True), predict_next)
# process_input(get_input(9), predict_next)
# process_input(get_input(9, test=True), predict_prev)
process_input(get_input(9), predict_prev)
