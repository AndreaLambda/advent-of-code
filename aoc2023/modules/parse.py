### parsing utils
from modules.types import Loc

def load_input_file(fname):
    with open(fname) as f:
        return f.read()

def get_input(num, test=False, file=None):
    file = file or ("test" if test else "input")
    return load_input_file(f"inputs/{num:02}/{file}.txt")

def find_in_input(input: str, char: str) -> Loc:
    # add 1 for the newline character
    line_plus_newline_len = input.index("\n") + 1
    idx = input.index(char)
    char_col = idx % line_plus_newline_len
    char_row = idx // line_plus_newline_len
    return Loc(char_row, char_col)
