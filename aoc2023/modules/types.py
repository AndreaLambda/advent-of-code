# common types
from enum import Enum
from heapq import heappop, heappush
from functools import cached_property
from typing import Callable, Generic, Iterator, NamedTuple, TypeVar


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


T = TypeVar("T")
TKey = TypeVar("TKey")

class KeyedPQ(Generic[T, TKey]):
    """
    Priority Queue which tracks the keys of items. When trying to add a new item with the same key as
    another, uses replace_if to determine whether to replace the old item or reject the new item.
    Uses replace_if even when a new item has the same key as an already-popped item.
    """
    use_item_as_key: Callable[[T], T] = lambda t: t             # default: use the item itself as the key
    bool_replace: Callable[[T, T], bool] = lambda a, b: True    # default: always replace old items

    def __init__(
            self,
            init_items: list[T]=[],
            key: Callable[[T], TKey]=use_item_as_key,
            replace_if: Callable[[T, T], bool]=bool_replace,
        ):
        self.key = key
        self.replace_if = replace_if
        self.pq: list[T] = []
        self.items: dict[TKey, T] = {}
        self.add_all(init_items)

    def add_all(self, items: list[T]):
        for item in items:
            self.add(item)

    def add(self, item: T):
        item_key = self.key(item)
        do_add = True
        # replace old item in the queue if replace_if is True and the old item is not already popped
        if item_key in self.items and (do_add := self.replace_if((existing := self.items[item_key]), item)) and existing in self.pq:
            self.pq.remove(existing)
        # if replace_if was False, reject the new item
        if do_add:
            heappush(self.pq, item)
            self.items[item_key] = item

    def pop(self) -> T:
        item = heappop(self.pq)
        return item

    def iter(self) -> Iterator[T]:
        while self.pq:
            yield self.pop()

    def __repr__(self):
        return str(self.pq)
