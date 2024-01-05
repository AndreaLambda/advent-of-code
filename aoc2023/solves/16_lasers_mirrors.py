# day 16: lasers and mirrors
from typing import NamedTuple

from modules.parse import get_input
from modules.types import Dir, Loc

# map of current to new direction(s) of travel for each mirror type
mirrors: dict[str, dict[Dir, list[Dir]]] = {
    "|": {Dir.left: [Dir.up, Dir.down], Dir.right: [Dir.up, Dir.down], Dir.up: [Dir.up], Dir.down: [Dir.down]},
    "-": {Dir.left: [Dir.left], Dir.right: [Dir.right], Dir.up: [Dir.left, Dir.right], Dir.down: [Dir.left, Dir.right]},
    "/": {Dir.left: [Dir.down], Dir.right: [Dir.up], Dir.up: [Dir.right], Dir.down: [Dir.left]},
    "\\": {Dir.left: [Dir.up], Dir.right: [Dir.down], Dir.up: [Dir.left], Dir.down: [Dir.right]},
    ".": {Dir.left: [Dir.left], Dir.right: [Dir.right], Dir.up: [Dir.up], Dir.down: [Dir.down]},
}

class Laser(NamedTuple):
    row: int
    col: int
    dir: Dir

class Grid:
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.rows = len(lines)
        self.cols = len(lines[0])
        self.lasers: list[Laser] = []
        self.marked: dict[Loc, list[Dir]] = {}
        self.results: dict[Laser, int] = {}

    def get_max_energized(self) -> int:
        return max(self.results.values())

    def get_energized(self) -> int:
        return len(self.marked)

    def is_valid_position(self, row: int, col: int) -> bool:
        return (0 <= row < self.rows) and (0 <= col < self.cols)

    def mark_valid_lasers(self, row: int, col: int, dirs: list[Dir]) -> list[Laser]:
        loc = Loc(row, col)
        valid: list[Laser] = []
        marked_dirs = self.marked.get(loc, [])
        for dir in dirs:
            # don't process any lasers which have already gone this direction from this location
            if dir not in marked_dirs:
                marked_dirs.append(dir)
                valid.append(Laser(row, col, dir))
        self.marked[loc] = marked_dirs
        return valid

    def get_initial_lasers(self) -> list[Laser]:
        all_lasers = (
            [Laser(row, -1, Dir.right) for row in range(self.rows)]
            + [Laser(row, self.cols, Dir.left) for row in range(self.rows)]
            + [Laser(-1, col, Dir.down) for col in range(self.cols)]
            + [Laser(self.rows, col, Dir.up) for col in range(self.cols)])
        return all_lasers
        
    # PEW PEW PEW! FIRE EVERYTHING!!!!!!111
    def fire_ALL_lasers(self):
        for laser in self.get_initial_lasers():
            self.fire_lasers(laser)

    def fire_lasers(self, initial_laser=Laser(0, -1, Dir.right)):
        self.lasers = [initial_laser]
        self.marked = {}
        while len(self.lasers) > 0:
            self.move_lasers()
        self.results[initial_laser] = self.get_energized()
    
    def move_lasers(self):
        next_lasers = []
        for (row, col, dir) in self.lasers:
            (new_row, new_col) = (row + dir.value[0], col + dir.value[1])
            if not self.is_valid_position(new_row, new_col):
                continue
            mirror = self.lines[new_row][new_col]
            new_dirs = mirrors[mirror][dir]
            next_lasers += self.mark_valid_lasers(new_row, new_col, new_dirs)
        self.lasers = next_lasers

def parse_input(input: str) -> list[str]:
    return input.splitlines()

def process_input(input: str, fire_ALL_lasers=False):
    lines = parse_input(input)
    grid = Grid(lines)
    if fire_ALL_lasers:
        grid.fire_ALL_lasers()
    else:
        grid.fire_lasers()
    return grid.get_max_energized()

# process_input(get_input(16, test=True))
# process_input(get_input(16))
# process_input(get_input(16, test=True), fire_ALL_lasers=True)
process_input(get_input(16), fire_ALL_lasers=True)
