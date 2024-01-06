# day 22: falling sand bricks
from collections import deque
from typing import Iterator, NamedTuple
from modules.parse import get_input
from modules.types import Counter, Loc as Loc2, Loc3
from modules.utils import sign


PartialDict = dict["Brick", set["Brick"]]

class SupportValue(NamedTuple):
    value: int
    partials: PartialDict

class Brick:
    _next_id = Counter()

    def __init__(self, start: Loc3, end: Loc3):
        self.id = Brick._next_id.next()
        self.height = start.z
        self.start = Loc3(start.row, start.col, 0)
        self.end = Loc3(end.row, end.col, end.z - start.z)
        self.above: set[Brick] = set()
        self.below: set[Brick] = set()
        # support levels for bricks above
        self.calc_support = False
        self.value = 0
        self.partials: PartialDict = {}

    def dim(self) -> Loc3:
        return self.end - self.start

    def top(self) -> int:
        return self.height + self.end.z

    def add_below(self, brick: "Brick"):
        self.below.add(brick)

    def add_above(self, brick: "Brick"):
        self.above.add(brick)

    def is_zappable(self) -> bool:
        return all([len(brick.below) >= 2 for brick in self.above])
    
    def get_support_value(self) -> SupportValue:
        if not self.calc_support:
            self.calc_support_value()
        return SupportValue(self.value, self.partials)        

    def calc_support_value(self):
        for brick in self.above:
            if len(brick.below) == 1:
                # brick is supported only by this brick
                self.add_support_value(brick)    
            else:
                self.partials[brick] = set([self])
        self.calc_support = True

    def add_support_value(self, brick_to_add: "Brick"):
        support = brick_to_add.get_support_value()
        self.value += 1 + support.value

        for (brick, partial) in support.partials.items():
            if brick in self.partials:
                new_partial = self.partials[brick] | partial
                if new_partial == brick.below:
                    self.partials.pop(brick)
                    self.add_support_value(brick)
                else:
                    self.partials[brick] = new_partial
            else:
                self.partials[brick] = partial
    
    def iter(self) -> Iterator[Loc2]:
        diff = self.end.loc2() - self.start.loc2()
        step = Loc2(sign(diff.row), sign(diff.col))
        loc = None
        while loc != self.end.loc2():
            loc = loc + step if loc else self.start.loc2()
            yield loc

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.height < other.height

    def __str__(self):
        return f"({self.id})"    

    def __repr__(self):
        return f"{self.start} ~ {self.end} at {self.height}"

class GridState(NamedTuple):
    current_z: int = 0
    brick: Brick = None

    def __repr__(self):
        return f"{self.current_z}{'' + str(self.brick) if self.brick else ''}"

class Grid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = self.create_grid()

    def create_grid(self) -> list[list[GridState]]:
        default = GridState()
        return [[default] * self.cols for _ in range(self.rows)]

    def get(self, loc: Loc2) -> GridState:
        return self.grid[loc.row][loc.col]

    def set(self, loc: Loc2, state: GridState):
        self.grid[loc.row][loc.col] = state

    def place_brick(self, brick: Brick):
        max_current_z = max([self.get(loc).current_z for loc in brick.iter()])
        brick.height = max_current_z + 1
        new_state = GridState(brick.top(), brick)
        for loc in brick.iter():
            state = self.get(loc)
            if (below_brick := state.brick) and below_brick.top() == max_current_z:
                brick.add_below(below_brick)
                below_brick.add_above(brick)
            self.set(loc, new_state)

    def __str__(self):
        return "\n".join(str(row) for row in self.grid)
        
class BrickRunner:
    def __init__(self, bricks: list[Brick]):
        self.bricks = bricks
        self.to_drop = deque(sorted(bricks))
        self.grid = self.generate_grid()

    def generate_grid(self) -> Grid:
        rows = max([brick.end.row for brick in self.bricks]) + 1
        cols = max([brick.end.col for brick in self.bricks]) + 1
        return Grid(rows, cols)

    def drop_bricks(self) -> "BrickRunner":
        while self.to_drop:
            self.drop_brick()
        return self

    def drop_brick(self):
        brick = self.to_drop.popleft()
        self.grid.place_brick(brick)

    def get_zappable_count(self) -> int:
        return sum([brick.is_zappable() for brick in self.bricks])

    def get_chain_reaction_count(self) -> int:
        from_top = sorted(self.bricks, key=lambda brick: brick.top(), reverse=True)
        return sum([brick.get_support_value()[0] for brick in from_top])

def parse_line(line: str) -> Brick:
    (start, end) = [[int(num) for num in part.split(",")] for part in line.split("~")]
    return Brick(Loc3(*start), Loc3(*end))

def parse_input(input: str) -> list[Brick]:
    return [parse_line(line) for line in input.splitlines()]

def process_input(input: str, chain_reaction=False):
    bricks = parse_input(input)
    runner = BrickRunner(bricks).drop_bricks()
    return runner.get_chain_reaction_count() if chain_reaction else runner.get_zappable_count()


# assert process_input(get_input(22, test=True)) == 5
# process_input(get_input(22))
# assert process_input(get_input(22, test=True), chain_reaction=True) == 7
# assert process_input(get_input(22, file="my_2d_test"), chain_reaction=True) == 25
process_input(get_input(22), chain_reaction=True)
