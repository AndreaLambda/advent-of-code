# common types
from enum import Enum
from functools import cached_property
from typing import NamedTuple


class Loc(NamedTuple):
    """ (row, col) location tuple for simplifying 2d tasks. """
    row: int
    col: int

    def __add__(self, other: "Loc"):
        return Loc(self.row + other.row, self.col + other.col)

    def __sub__(self, other: "Loc"):
        return Loc(self.row - other.row, self.col - other.col)

    def __repr__(self):
        return f"(r{self.row}, c{self.col})"


class Loc3(NamedTuple):
    """ (row, col, z) location tuple for simplifying 3d tasks. """
    row: int
    col: int
    z: int

    def loc2(self):
        """ (row, col) as a 2d Loc. """
        return Loc(self.row, self.col)

    def __sub__(self, other):
        return Loc3(self.row - other.row, self.col - other.col, self.z - other.z)

    def __repr__(self):
        return f"(r{self.row}, c{self.col}, z{self.z})"


class Dir(Enum):
    """ Simplifies handling of cardinal directions. """
    left = Loc(0, -1)
    right = Loc(0, 1)
    up = Loc(-1, 0)
    down = Loc(1, 0)

    @cached_property
    def opposite(self):
        return {Dir.left: Dir.right, Dir.right: Dir.left, Dir.up: Dir.down, Dir.down: Dir.up}[self]

    def from_loc(self, loc: Loc) -> Loc:
        """ Gets the new location when moving from the Loc. """
        return loc + self.value

    def retrace_from(self, loc: Loc):
        """ Retraces (moves in the opposite direction) from the Loc. """
        return loc - self.value

    # might need a different sort order depending on the problem?
    def __lt__(self, other: "Dir"):
        return self.value > other.value

    def __mul__(self, num: int):
        return Loc(self.value.row * num, self.value.col * num)
        
    def __repr__(self):
        return self.name


class Counter:
    """ Counter for assigning unique object ids. """
    def __init__(self, next=1):
        self._next = next
        self._iter = self.iter()

    def next(self):
        return next(self._iter)

    def iter(self):
        while True:
            yield self._next
            self._next += 1
