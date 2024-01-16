# day 23: hiking slopes (no pruning, arrives at correct answer after 1.5m nodes, completes around 7.75m nodes)
from collections import deque
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from itertools import pairwise
from math import floor, log2
from typing import NamedTuple

from modules.parse import get_input
from modules.types import Counter, Loc, Dir, KeyedPQ
from modules.utils import filter_none, rev


valid_dirs: dict[str, set[Dir]] = {
    ".": [Dir.up, Dir.down, Dir.left, Dir.right],
    "^": [Dir.up],
    "v": [Dir.down],
    "<": [Dir.left],
    ">": [Dir.right],
}

type NodeId = int
type Steps = int            # number of steps in path, or number of steps taken
type EncodedNodes = int     # binary representation of one or more node ids (0 => b001, 1 => b010, 2 => b100, set(1,2) => b110, etc)

class TrailMove(NamedTuple):
    loc: Loc
    dir: Dir
    steps: Steps

    def __repr__(self):
        return f"({self.loc}, {self.dir.name}, {self.steps})"

class MapperPathToNode(NamedTuple):
    start: TrailMove
    end: TrailMove

class MapperNode(NamedTuple):
    id: NodeId
    loc: Loc
    paths: dict["MapperNode", "MapperPath"]

    def __hash__(self):
        return self.id
        
    def __str__(self):
        return f"""Node {self.id}{f" -> {', '.join([f'{node.id} ({path.steps})' for (node, path) in self.paths.items()])}" if len(self.paths) > 0 else ''}"""

    def __repr__(self):
        return f"""{self.id} at {self.loc}{f" -> {', '.join([f'{node.id} ({path.steps})' for (node, path) in self.paths.items()])}" if len(self.paths) > 0 else ''}"""

class MapperPath(NamedTuple):
    steps: Steps
    start: Dir
    end: Dir

class ViewerJustify(Enum):
    left = 1
    center = 2
    right = 3

@dataclass(frozen=True)
class WalkerNode:
    id: NodeId
    nodes: EncodedNodes
    paths: dict[NodeId, Steps]

    @cached_property
    def enc_id(self) -> EncodedNodes:
        return encode_id(self.id)

class WalkerStateKey(NamedTuple):
    node_id: NodeId
    remaining: EncodedNodes

class WalkerState(NamedTuple):
    node_id: NodeId
    steps: Steps
    remaining: EncodedNodes

    def key(self) -> "WalkerStateKey":
        return WalkerStateKey(self.node_id, self.remaining)

    def __lt__(self, other: "WalkerState"):
        return self.steps < other.steps

    def __str__(self):
        return f"{self.steps} steps, Node {self.node_id}: done {self.remaining}"

    def __repr__(self):
        return f"{self.steps} steps, Node {self.node_id}: done {self.remaining}"


def encode_id(node_id: NodeId) -> EncodedNodes:
    return 1 << node_id

def convert(node: MapperNode) -> WalkerNode:
    return WalkerNode(node.id, sum([encode_id(node.id) for node in node.paths]), {node.id: path.steps for (node, path) in node.paths.items()})


class Trail:
    def __init__(self, lines: list[str], is_slippery: bool):
        self.lines: list[str] = lines
        self.is_slippery = is_slippery
        self.rows = len(lines)
        self.cols = len(lines[0])
        self.start: Loc = self.get_exit(0)
        self.end: Loc = self.get_exit(self.rows - 1)

    def get_exit(self, line_num: int) -> Loc:
        return Loc(line_num, self.lines[line_num].index("."))

    def get(self, loc: Loc) -> str:
        return self.lines[loc.row][loc.col]

    def get_valid_dirs(self, tile: str):
        return valid_dirs[tile] if self.is_slippery else valid_dirs["."]

    def is_valid_move(self, move: TrailMove) -> bool:
        if not((0 <= move.loc.row < self.rows) and (0 <= move.loc.col < self.cols) and (tile := self.get(move.loc)) != "#"):
            return False
        return not(len((dirs := self.get_valid_dirs(tile))) == 1 and dirs[0].opposite == move.dir)
        
    def get_valid_moves(self, move: TrailMove) -> list[TrailMove]:
        dirs = self.get_valid_dirs(self.get(move.loc))
        moves = [TrailMove(dir.from_loc(move.loc), dir, move.steps + 1) for dir in dirs if (move.dir is None or dir is not move.dir.opposite)]
        return [next_move for next_move in moves if self.is_valid_move(next_move)]


# simplify the trail into nodes
class TrailMapper:
    def __init__(self, lines, is_slippery):
        self.trail = Trail(lines, is_slippery)
        self.next_id = Counter(next = 0)
        self.nodes: dict[Loc, MapperNode] = {}
        self.to_process: deque[MapperNode] = deque()
        self.start = self.create_node(self.trail.start)
        self.end: MapperNode = None

    def create_node(self, loc) -> MapperNode:
        id = self.next_id.next()
        node = MapperNode(id, loc, {})
        self.nodes[loc] = node
        self.to_process.append(node)
        return node

    def get_node(self, loc) -> MapperNode:
        return self.create_node(loc) if loc not in self.nodes else self.nodes[loc]

    def map_trail(self):
        while self.to_process:
            self.process_node(self.to_process.popleft())
        self.clean_up_nodes()
        return self

    def process_node(self, node: MapperNode):
        if node.loc == self.trail.end:
            self.end = node
        base_move = TrailMove(node.loc, None, 0)
        next_steps = self.trail.get_valid_moves(base_move)
        next_moves = [self.walk_to_node(next_move) for next_move in next_steps]
        for next_move in filter_none(next_moves):
            next_node = self.get_node(next_move.end.loc)
            node.paths[next_node] = MapperPath(next_move.end.steps, next_move.start.dir, next_move.end.dir)
        
    def walk_to_node(self, move: TrailMove) -> MapperPathToNode:
        cur_move = move
        while len(next_moves := self.trail.get_valid_moves(cur_move)) == 1:
            cur_move = next_moves[0]
        if len(next_moves) == 0 and cur_move.loc != self.trail.end:
            return None
        return MapperPathToNode(move, cur_move)

    def clean_up_nodes(self):
        if len((end_nodes := self.end.paths)) == 1:
            # since next-to-last node is mandatory, can only go to the end node from here (any other move results in a dead end)
            second_last = next(iter(end_nodes))
            for node in list(second_last.paths):
                if node != self.end:
                    second_last.paths.pop(node)
        # end node is the end, no more moves
        self.end.paths.clear()


# prints the mapped trail; can print the entire trail, or just a specific path
class TrailViewer:
    def __init__(self, mapper: TrailMapper, path_to_view: list[NodeId] = None, row_scale: int=3):
        self.mapper = mapper
        self.trail = mapper.trail
        self.row_scale = row_scale
        self.path_to_view = path_to_view
        self.nodes = self.mapper.nodes.values()
        self.node_dict: dict[int, MapperNode] = {node.id : node for node in self.nodes}
        self.lines = self.get_lines()

    def get_lines(self):
        return [[" "] * self.trail.cols for row in range(self.trail.rows // self.row_scale + 1)]

    def mark(self, loc: Loc, char: str):
        self.lines[loc.row // self.row_scale][loc.col] = char

    def draw_row(self, start: Loc, end: Loc):
        if start.col > end.col:
            (start, end) = (end, start)
        self.lines[start.row // self.row_scale][start.col : end.col + 1] = "." * ((end.col - start.col) + 1)

    def draw_col(self, start: Loc, end: Loc):
        if start.row > end.row:
            (start, end) = (end, start)
        for row in range(start.row, end.row+1):
            self.lines[row // self.row_scale][start.col] = "."

    def draw_steps(self, steps: Steps, loc: Loc, justify: ViewerJustify):
        steps_str = f"({steps})"
        start_loc = loc if justify == ViewerJustify.right else Loc(loc.row, loc.col - len(steps_str) + 1) if justify == ViewerJustify.left else Loc(loc.row, loc.col - len(steps_str) // 2)
        self.lines[start_loc.row // self.row_scale][start_loc.col : start_loc.col + len(steps_str)] = steps_str            

    def draw_path(self, path: MapperPath, start: Loc, end: Loc):
        (start, end) = (path.start.from_loc(start), path.end.opposite.from_loc(end))
        
        if path.start == Dir.right and path.end == Dir.down:
            self.draw_row(start, Loc(start.row, end.col))
            self.draw_col(Loc(start.row, end.col), end)
            self.draw_steps(path.steps, Loc(start.row, end.col - 2), ViewerJustify.left)
            
        if path.start == Dir.down and path.end == Dir.right:
            self.draw_col(start, Loc(end.row, start.col))
            self.draw_row(Loc(end.row, start.col), end)
            self.draw_steps(path.steps, Loc(end.row - (self.row_scale * 2), start.col), ViewerJustify.center)

        if path.start == path.end == Dir.right:
            mid_col = (start.col + end.col) // 2
            (start_mid, end_mid) = (Loc(start.row, mid_col), Loc(end.row, mid_col))
            self.draw_row(start, start_mid)
            self.draw_col(start_mid, end_mid)
            self.draw_row(end_mid, end)
            self.draw_steps(path.steps, Loc(start.row, mid_col), ViewerJustify.center)

        if path.start == path.end == Dir.down or path.start == path.end == Dir.up:
            (mid_row, mid_col) = ((start.row + end.row) // 2, (start.col + end.col) // 2)
            (start_mid, end_mid) = (Loc(mid_row, start.col), Loc(mid_row, end.col))
            self.draw_col(start, start_mid)
            self.draw_row(start_mid, end_mid)
            self.draw_col(end_mid, end)
            self.draw_steps(path.steps, Loc(mid_row, mid_col), ViewerJustify.center)
        
    def view_trail(self):
        if self.path_to_view:
            for (src_id, dst_id) in pairwise(self.path_to_view):
                if (src_id > dst_id):
                    (src_id, dst_id) = (dst_id, src_id)
                (id, loc, paths) = self.node_dict[src_id]
                for (end_node, path) in paths.items():
                    if end_node.id == dst_id:
                        self.draw_path(path, loc, end_node.loc)
        else:
            for (id, loc, paths) in self.nodes:
                for (end_node, path) in paths.items():
                    self.draw_path(path, loc, end_node.loc)
        for (id, loc, _) in self.nodes:
            self.mark(loc, str(id % 10))
            if id >= 10:
                self.mark(Dir.left.from_loc(loc), str(id // 10))
        return "\n".join([''.join(line) for line in self.lines])
        
    def __str__(self):
        return "\n".join([''.join(line) for line in self.lines])


class TrailWalker:
    def __init__(self, mapper: TrailMapper):
        self.trail = mapper
        self.nodes = {node.id: convert(node) for node in self.trail.nodes.values()}
        self.nodes_to_walk: KeyedPQ[WalkerState, WalkerStateKey] = KeyedPQ(
            init_items=[self.get_start_state()],
            key=lambda s: s.key() if s.node_id != self.trail.end.id else self.end_key,
            replace_if=lambda a,b: b.steps < a.steps,
        )

    @cached_property
    def end_key(self) -> WalkerStateKey:
        return WalkerStateKey(self.trail.end.id, 0)

    def get_start_state(self) -> WalkerState:
        # this creates a state where all nodes are still remaining
        # e.g. if the highest node id is 4, this results in set(0,1,2,3,4) => b11111
        start_node = self.nodes[self.trail.start.id]
        highest_node = self.nodes[len(self.nodes) - 1]
        return WalkerState(start_node.id, 0, highest_node.enc_id * 2 - 1)

    def walk_trail(self, max_nodes=None) -> Steps:
        n = 0
        for node in self.nodes_to_walk.iter():
            self.process_node(node)
            n += 1
            if max_nodes and n >= max_nodes:
                break
        end_state = self.nodes_to_walk.items.get(self.end_key, None)
        # since we've been subtracting the number of steps, negate the result
        return -end_state.steps if end_state else None

    def process_node(self, state: WalkerState):
        cur_node = self.nodes[state.node_id]
        # "remaining nodes" of the state after crossing off the node we're about to walk away from
        next_remaining = state.remaining - cur_node.enc_id
        # remaining nodes which have paths from the current node
        next_nodes = state.remaining & cur_node.nodes
        while next_nodes > 0:
            # if next_nodes is b10000, b10100, b11111, etc., floor(log2) results in b10000
            next_id = floor(log2(next_nodes))
            next_state = self.walk_path(state, next_id, cur_node.paths[next_id], next_remaining)
            self.nodes_to_walk.add(next_state)
            next_nodes -= self.nodes[next_id].enc_id
        
    def walk_path(self, state: WalkerState, next_node: NodeId, path_steps: Steps, remaining: EncodedNodes) -> WalkerState:
        # subtracting the number of steps means the longest path has the lowest number - thus allowing Dijkstra to work
        return WalkerState(next_node, state.steps - path_steps, remaining)

    def get_backtrack(self) -> list[NodeId]:
        end_id = self.trail.end.id
        end_state = self.nodes_to_walk.items.get(self.end_key, None)
        if not end_state:
            return None
        backtrack_node_ids = [end_id]
        (node_id, steps, remaining) = end_state
    
        while steps < 0:
            prev_nodes = [n for n in self.nodes.values() if node_id in n.paths]
            found = False
            for prev_node in prev_nodes:
                # construct the previous key we expect to find if prev_node is part of the longest path
                # ("un-cross off" the node we're about to walk towards)
                prev_remaining = remaining | prev_node.enc_id
                prev_key = WalkerStateKey(prev_node.id, prev_remaining)
                prev_state = self.nodes_to_walk.items.get(prev_key, None)
                # if the number of steps is exactly the current steps plus the path length, prev_node is part of the longest path
                prev_steps = prev_node.paths[node_id] + steps
                if prev_state and prev_state.steps == prev_steps:
                    (node_id, steps, remaining) = prev_state
                    backtrack_node_ids.append(node_id)
                    found = True
                    break
            if not found:
                return None
        return rev(backtrack_node_ids)

def parse_input(input: str) -> list[str]:
    return input.splitlines()

def process_input(input: str, is_slippery=True, max_nodes=None, view_trail=False):
    lines = parse_input(input)
    mapper = TrailMapper(lines, is_slippery).map_trail()
    walker = TrailWalker(mapper)
    res = walker.walk_trail(max_nodes)
    if not view_trail:
        return res
    path = walker.get_backtrack()
    viewer = TrailViewer(walker.trail, path)
    print(viewer.view_trail())


# assert process_input(get_input(23, test=True)) == 94
# process_input(get_input(23))
# assert process_input(get_input(23, test=True), is_slippery=False) == 154
process_input(get_input(23), is_slippery=False, max_nodes=1_500_000)   # stops after 1.5m nodes, but arrives at correct answer (~9s)

# process_input(get_input(23), is_slippery=False)   # runs to completion (7.75m nodes, ~56s)
# process_input(get_input(23), is_slippery=False, max_nodes=1_500_000, view_trail=True)   # prints the longest trail (~9s)
