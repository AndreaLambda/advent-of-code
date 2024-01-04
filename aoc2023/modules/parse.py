### parsing utils
def load_input_file(fname):
    with open(fname) as f:
        return f.read()

def get_input(num, test=False, file=None):
    file = file or ("test" if test else "input")
    return load_input_file(f"inputs/{num:02}/{file}.txt")
