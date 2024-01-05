# day 18: trench volume
import re
from typing import NamedTuple
from bisect import bisect_left, bisect_right
from modules.parse import get_input
from modules.types import Dir, Loc

class Plan(NamedTuple):
    dir: Dir
    length: int

class Dig(NamedTuple):
    start: Loc
    end: Loc
    dir: Dir
        
    def __repr__(self):
        return f"({self.dir.name:5} {self.start} -> {self.end})"

plan_dirs = {"R": Dir.right, "L": Dir.left, "U": Dir.up, "D": Dir.down}
hex_plan_dirs = {"0": Dir.right, "1": Dir.down, "2": Dir.left, "3": Dir.up}

class DigFinder:
    def __init__(self, digs: list[Dig]):
        self.digs: list[Dig] = sorted(digs, key=lambda dig: (dig.start.row, dig.end.row))
        self.corner_rows: list[int] = self.get_corner_rows()
        self.skip = 0

    def get_start_row(self):
        return self.digs[0].start.row

    def get_end_row(self):
        return self.digs[-1].end.row

    def get_corner_rows(self) -> list[int]:
        return sorted(list(set([dig.start.row for dig in self.digs])))

    def get_digs_for_row(self, row: int) -> tuple[list[Dig], int]:
        while self.digs[self.skip].end.row < row:
            self.skip += 1
        max = bisect_right(self.digs, row, lo=self.skip, key=lambda dig: dig.start.row)
        digs = sorted([dig for dig in self.digs[self.skip:max] if dig.end.row >= row], key=lambda dig: (dig.start.col, dig.end.col))

        next_corner = self.corner_rows[bisect_left(self.corner_rows, row)]    
        n_identical_rows = 1 if row == next_corner else next_corner - row
        return (digs, n_identical_rows)

class Digger:
    def __init__(self, plans: list[Plan]):
        self.plans = plans
        self.loc = Loc(0, 0)
        self.digs: list[Dig] = []
        self.finder: DigFinder = None

    def dig_lagoon(self) -> "Digger":
        for plan in self.plans:
            self.dig_plan(plan)
        self.finder = DigFinder(self.digs)
        return self

    def dig_plan(self, plan: Plan):
        new_loc = self.loc + plan.dir * plan.length
        (start, end) = (self.loc, new_loc) if plan.dir in [Dir.down, Dir.right] else (new_loc, self.loc)
        self.digs.append(Dig(start, end, plan.dir))
        self.loc = new_loc

    def get_total_area(self) -> int:
        total = 0
        row = self.finder.get_start_row()
        end = self.finder.get_end_row()
        while row <= end:
            (digs, n_rows) = self.finder.get_digs_for_row(row)
            total += self.get_row_area(digs) * n_rows
            row += n_rows
        return total
        
    def get_row_area(self, digs: list[Dig]) -> int:
        dig_groups: list[list[Dig]] = []
        dig_group: list[Dig] = []
        for dig in digs:
            if dig_group and dig_group[-1].dir in [Dir.up, Dir.down] and dig.dir in [Dir.up, Dir.down]:
                dig_groups.append(dig_group)
                dig_group = []
            dig_group.append(dig)
        dig_groups.append(dig_group)
        total: int = 0
        crossing: list[int] = []
        for group in dig_groups:
            # [col] is always a crossing
            if len(group) == 1:
                crossing.append(group[0].start.col)
            else:
                # [col, row, col] -> test whether a crossing
                if group[0].dir == group[-1].dir:
                    # if crossing in, use the start col; otherwise, end col
                    crossing.append(group[0].start.col if not crossing else group[-1].end.col)
                else:
                    # if already crossed in, can safely ignore this
                    if not crossing:
                        crossing = [group[0].start.col, group[-1].end.col]

            if len(crossing) == 2:
                total += crossing[1] - crossing[0] + 1
                crossing = []

        return total


def parse_line(line: str, decode_color: bool) -> Plan:
    (dir, length, hex_length, hex_dir) = re.match(r"([RDLU]) ([0-9]*) \(#([0-9a-f]{5})([0-9a-f])\)", line).groups()
    if decode_color:
        hex_int = int(f"0x{hex_length}", 0)
        return Plan(hex_plan_dirs[hex_dir], hex_int)
    else:
        return Plan(plan_dirs[dir], int(length))

def parse_input(input, decode_color: bool) -> list[Plan]:
    return [parse_line(line, decode_color) for line in input.splitlines()]

def process_input(input: str, decode_color=False):
    plans = parse_input(input, decode_color)
    digger = Digger(plans)
    return digger.dig_lagoon().get_total_area()


# process_input(get_input(18, test=True))
# process_input(get_input(18))
# process_input(get_input(18, test=True), decode_color=True)
process_input(get_input(18), decode_color=True)
