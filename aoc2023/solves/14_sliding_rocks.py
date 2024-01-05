# day 14: sliding rocks
from math import floor
from modules.parse import get_input
from modules.utils import rev

up = ("rows", -1)
down = ("rows", +1)
left = ("cols", -1)
right = ("cols", +1)

other_axis = {"rows": "cols", "cols": "rows"}
spin_cycle = [up, left, down, right]

class RockTilter:
    def __init__(self, lines: list[str]):
        if len(lines) != len(lines[0]):
            raise("noph!")
        self.size = len(lines)
        self.lines = lines
        self.rocks = self.init_map("O")
        self.blocks = self.init_map("#")

    def init_map(self, block_type: str) -> dict[str, dict[int, list[int]]]:
        row_map = {row_idx: [] for row_idx in range(self.size)}
        col_map = {col_idx: [] for col_idx in range(self.size)}
        for (row, line) in enumerate(self.lines):
            for (col, spot) in enumerate(line):
                if spot == block_type:
                    row_map[row].append(col)
                    col_map[col].append(row)
        return {"rows": row_map, "cols": col_map}

    def get_load(self) -> int:
        return sum([(self.size - row_idx) * len(row) for (row_idx, row) in self.rocks["rows"].items()])
        
    def tilt_rocks(self, tilt: tuple[str, int]):
        (tilt_axis, tilt_dir) = tilt

        # here, "axis" refers to the tilt axis, "other" is the non-tilt axis
        new_axis = {idx: [] for idx in range(self.size)}
        new_other = {idx: [] for idx in range(self.size)}

        # the next index along the tilt axis a rock will move to (0 if left/up, size-1 if right/down)
        next_idx = 0 if tilt_dir == -1 else self.size - 1
        next_idxs = [next_idx] * self.size

        # iterate in reverse order for right/down
        iter_idxs = range(self.size) if tilt_dir == -1 else rev(range(self.size))
        for iter_idx in iter_idxs:
            axis_rocks = self.rocks[tilt_axis][iter_idx]
            axis_blocks = self.blocks[tilt_axis][iter_idx]
            for block_other in axis_blocks:
                # the next rock along the tilt axis will stop next to this block
                next_idxs[block_other] = iter_idx - tilt_dir
            for rock_other in axis_rocks:
                new_idx = next_idxs[rock_other]
                new_axis[new_idx].append(rock_other)
                new_other[rock_other].append(new_idx)
                # the next rock along the tilt axis will stop next to this rock
                next_idxs[rock_other] -= tilt_dir

        self.rocks = {tilt_axis: new_axis, other_axis[tilt_axis]: new_other}

    def run_spin_cycles(self, cycles_to_run: int):
        rocks_to_cycle: dict[str, int] = {}
        cycle = 0
        found_repeat = False
        while cycle < cycles_to_run:
            cycle += 1
            self.run_spin_cycle()
            if not found_repeat:
                cycle_str = self.get_rocks_as_str()
                if cycle_str in rocks_to_cycle:
                    prev = rocks_to_cycle[cycle_str]
                    cycle = advance(prev, cycle, cycles_to_run)
                    found_repeat = True
                else:
                    rocks_to_cycle[cycle_str] = cycle
    
    def run_spin_cycle(self):
        for tilt in spin_cycle:
            self.tilt_rocks(tilt)

    def get_rocks_as_str(self) -> str:
        res = [f"{row_idx}:{','.join([str(idx) for idx in sorted(row)])}" for (row_idx, row) in self.rocks["rows"].items() if len(row) > 0]
        return "_".join(res)

def advance(prev: int, now: int, max: int) -> int:
    cycle = now - prev
    remain = max - now
    skip = floor(remain / cycle) * cycle
    return now + skip

def parse_input(input: str) -> RockTilter:
    return RockTilter(input.splitlines())

def process_input(input: str, cycles_to_run: int = None):
    tilter = parse_input(input)
    if cycles_to_run:
        tilter.run_spin_cycles(1_000_000_000)
    else:
        tilter.tilt_rocks(up)
    return tilter.get_load()

# process_input(get_input(14, test=True))
# process_input(get_input(14))
# process_input(get_input(14, test=True), cycles_to_run=1_000_000_000)
process_input(get_input(14), cycles_to_run=1_000_000_000)
