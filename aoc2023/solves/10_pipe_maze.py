# day 10: pipe maze
from modules.parse import get_input

(left, right, up, down) = ["left", "right", "up", "down"]
# travel based on lines indexing
travels = {left: (0, -1), right: (0, 1), up: (-1, 0), down: (1, 0)}
opposites = {left: right, right: left, up: down, down: up}
pipes = {
    "|": [up, down],
    "-": [left, right],
    "L": [up, right],
    "J": [left, up],
    "7": [left, down],
    "F": [right, down],
    ".": [],
    "S": [up, down, left, right],
}

vert_pipes = {pipe: [dir for dir in dirs if dir in [up, down]] for (pipe, dirs) in pipes.items()}

class Looper:
    def __init__(self, maze, row, col):
        self.maze = maze
        self.row = row
        self.col = col
        self.pipe = maze[row][col]
        self.history = [(row, col)]
        self.last = ""
        self.moves = 0

    def move_next(self):
        for next in pipes[self.pipe]:
            if next == self.last:
                continue
            next_travel = travels[next]
            next_row = self.row + next_travel[0]
            next_col = self.col + next_travel[1]
            next_pipe = self.maze[next_row][next_col]
            next_last = opposites[next]
            if next_last not in pipes[next_pipe]:
                continue
            if 0 <= next_row < len(self.maze) and 0 <= next_col < len(self.maze[0]):
                # commit to the first valid move
                self.row = next_row
                self.col = next_col
                self.pipe = next_pipe
                self.last = next_last
                self.moves += 1
                if not self.is_looped():
                    self.history.append((next_row, next_col))
                return

    def is_looped(self):
        return self.pipe == "S" and self.moves > 0

    def get_start_pipe(self):
        to_first = get_direction(self.history[0], self.history[1])
        to_last = get_direction(self.history[0], self.history[-1])
        start_moves = sorted([to_first, to_last])
        for (pipe, pipe_moves) in pipes.items():
            if start_moves == sorted(pipe_moves):
                return pipe
        
    def draw_outline(self):
        outline_draw = [list("." * len(self.maze[0])) for row in range(len(self.maze))]
        for (row, col) in self.history:
            outline_draw[row][col] = self.maze[row][col]
        (start_row, start_col) = self.history[0]
        outline_draw[start_row][start_col] = self.get_start_pipe()
        outline_draw = [''.join(row) for row in outline_draw]
        return outline_draw
        
    def get_outline(self):
        all_rows = {row: {} for row in range(len(self.maze))}
        for (row, col) in self.history:
            all_rows[row][col] = self.maze[row][col]
        (start_row, start_col) = self.history[0]
        all_rows[start_row][start_col] = self.get_start_pipe()
        outline = {row: sorted(item for item in pipes.items() if item[1] != "-") for (row, pipes) in all_rows.items() if len(pipes) > 0}
        return outline

    def count_enclosed_tiles(self):
        outline = self.get_outline()
        total = 0
        for (row, row_outline) in outline.items():
            # reset vertical test for each row
            vert_test = {up: False, down: False}
            prev_col = -1

            for (col, pipe) in row_outline:
                if vert_test == {up: True, down: True}:
                    # inside the loop; count tiles since previous pipe
                    total += col - prev_col - 1
                # update vertical test
                for dir in vert_pipes[pipe]:
                    vert_test[dir] = not vert_test[dir]
                prev_col = col
        return total

    def __repr__(self):
        return f"{self.pipe} at [{self.row},{self.col}], {self.moves} moves, from={self.last}"

def parse_input(input):
    lines = input.splitlines()
    # add 1 for the newline character
    row_len = len(lines[0]) + 1
    start_idx = input.find("S")
    start_col = start_idx % row_len
    start_row = int((start_idx - start_col) / row_len)
    return (lines, start_row, start_col)

def get_direction(a, b):
    (a_row, a_col) = a
    (b_row, b_col) = b
    (row_move, col_move) = (b_row - a_row, b_col - a_col)
    for (dir, (t_row_move, t_col_move)) in travels.items():
        if row_move == t_row_move and col_move == t_col_move:
            return dir
    
def process_input(input):
    (maze, start_row, start_col) = parse_input(input)
    looper = Looper(maze, start_row, start_col)
    while not looper.is_looped():
        looper.move_next()
    return (int(looper.moves / 2), looper.count_enclosed_tiles())

def ascii(line):
    res = line.replace("L", "┕").replace("J", "┙").replace("7", "┑").replace("F", "┍").replace("|", "┆").replace("-", "─")
    return res

def print_maze(lines):
    print("\n".join([ascii(line) for line in lines]))

# process_input(get_input(10, file="test_1"))
# process_input(get_input(10, file="test_2"))
process_input(get_input(10))