# day 23: hiking slopes (no pruning, arrives at correct answer after 2.5m nodes, completes around 13m nodes)
from collections import deque
from functools import cached_property
from itertools import pairwise
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

class Move(NamedTuple):
    loc: Loc
    dir: Dir
    steps: int

    def __repr__(self):
        return f"({self.loc}, {self.dir.name}, {self.steps})"

class Trail:
    def __init__(self, lines, is_slippery):
        self.lines: list[str] = lines
        self.is_slippery = is_slippery
        self.rows = len(lines)
        self.cols = len(lines[0])
        self.start: Loc = self.get_exit(0)
        self.end: Loc = self.get_exit(self.rows - 1)

    def get_exit(self, line_num) -> Loc:
        return Loc(line_num, self.lines[line_num].index("."))

    def get(self, loc: Loc) -> str:
        return self.lines[loc.row][loc.col]

    def get_valid_dirs(self, tile):
        return valid_dirs[tile] if self.is_slippery else valid_dirs["."]

    def is_valid_move(self, move: Move) -> bool:
        if not((0 <= move.loc.row < self.rows) and (0 <= move.loc.col < self.cols) and (tile := self.get(move.loc)) != "#"):
            return False
        return not(len((dirs := self.get_valid_dirs(tile))) == 1 and dirs[0].opposite == move.dir)
        
    def get_valid_moves(self, move: Move) -> list[Move]:
        dirs = self.get_valid_dirs(self.get(move.loc))
        moves = [Move(dir.from_loc(move.loc), dir, move.steps + 1) for dir in dirs if (move.dir is None or dir is not move.dir.opposite)]
        return [next_move for next_move in moves if self.is_valid_move(next_move)]

class Path(NamedTuple):
    node: "Node"
    steps: int
    start: Dir
    end: Dir

class NodePaths:
    def __init__(self):
        self.path_dict: dict["Node", Path] = {}
        self.nodes: frozenset["Node"] = frozenset()
        self.paths: frozenset[Path] = frozenset()
    
    def add(self, path: Path):
        self.path_dict[path.node] = path
        self.refresh()

    def get(self, node: "Node"):
        return self.path_dict[node]

    def pop(self, node: "Node"):
        if node in self.nodes:
            self.path_dict.pop(node)
            self.refresh()

    def refresh(self):
        self.nodes = frozenset(self.path_dict.keys())
        self.paths = frozenset(self.path_dict.values())

    def clear(self):
        self.path_dict = {}
        self.refresh()

    def __str__(self):
        return f" -> {self.node.id} {self.steps}"
    
class Node(NamedTuple):
    id: int
    loc: Loc
    paths: NodePaths

    def __hash__(self):
        return self.id
        
    def __str__(self):
        return f"""Node {self.id}{f" -> {', '.join([f'{path.node.id} ({path.steps})' for (path) in self.paths.paths])}" if len(self.paths.paths) > 0 else ''}"""

    def __repr__(self):
        return f"""{self.id} at {self.loc}{f" -> {', '.join([f'{path.node.id} ({path.steps})' for (path) in self.paths.paths])}" if len(self.paths.paths) > 0 else ''}"""

class Moves(NamedTuple):
    start: Move
    end: Move

# simplify the trail into nodes
class TrailMapper:
    def __init__(self, lines, is_slippery):
        self.trail = Trail(lines, is_slippery)
        self.next_id = Counter()
        self.nodes: dict[Loc, Node] = {}
        self.to_process = deque()
        self.start = self.create_node(self.trail.start)
        self.end = self.create_node(self.trail.end)

    def create_node(self, loc):
        id = 99 if loc == self.trail.end else self.next_id.next()
        node = Node(id, loc, NodePaths())
        self.nodes[loc] = node
        if loc != self.trail.end:
            self.to_process.append(node)
        return node

    def get_node(self, loc) -> Node:
        return self.create_node(loc) if loc not in self.nodes else self.nodes[loc]

    def map_trail(self):
        while self.to_process:
            self.process_node(self.to_process.popleft())
        self.clean_up_nodes()
        return self

    def clean_up_nodes(self):
        if len((start_nodes := self.start.paths.nodes)) == 1:
            # second node (first after start) can't go back to start
            second = next(iter(start_nodes))
            second.paths.pop(self.start)
            for third in second.paths.nodes:
                # since second node is mandatory, can't go back to it either
                third.paths.pop(second)

        if len((end_nodes := self.end.paths.nodes)) == 1:
            # since next-to-last node is mandatory, can only go to the end node from here (any other move results in a dead end)
            second_last = next(iter(end_nodes))
            for node in second_last.paths.nodes:
                if node != self.end:
                    second_last.paths.pop(node)
        # end node is the end, no more moves
        self.end.paths.clear()
    
    def process_node(self, node: Node):
        if node == self.end:
            return
        base_move = Move(node.loc, None, 0)
        next_steps = self.trail.get_valid_moves(base_move)
        next_moves = [self.walk_to_node(next_move) for next_move in next_steps]
        for next_move in filter_none(next_moves):
            next_node = self.get_node(next_move.end.loc)
            node.paths.add(Path(next_node, next_move.end.steps, next_move.start.dir, next_move.end.dir))
        
    def walk_to_node(self, move: Move) -> Moves:
        cur_move = move
        while len(next_moves := self.trail.get_valid_moves(cur_move)) == 1:
            cur_move = next_moves[0]
        if len(next_moves) == 0 and cur_move.loc != self.trail.end:
            return None
        return Moves(move, cur_move)

class TrailViewer:
    def __init__(self, mapper: TrailMapper, only_path: list[int] = None, row_scale: int=3):
        self.mapper = mapper
        self.trail = mapper.trail
        self.row_scale = row_scale
        self.only_path = only_path
        self.nodes = self.mapper.nodes.values()
        self.node_dict: dict[int, Node] = {node.id : node for node in self.nodes}
        self.lines = self.get_lines()

    def get_lines(self):
        return [[" "] * self.trail.cols for row in range(self.trail.rows // self.row_scale + 1)]

    def mark(self, loc, char):
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

    def draw_steps(self, steps: int, loc: Loc, justify: Dir):
        steps_str = f"({steps})"
        start_loc = loc if justify == Dir.right else Loc(loc.row, loc.col - len(steps_str) + 1) if justify == Dir.left else Loc(loc.row, loc.col - len(steps_str) // 2)
        self.lines[start_loc.row // self.row_scale][start_loc.col : start_loc.col + len(steps_str)] = steps_str            

    def draw_path(self, path: Path, start: Loc, end: Loc):
        (start, end) = (path.start.from_loc(start), path.end.opposite.from_loc(end))
        
        if path.start == Dir.right and path.end == Dir.down:
            self.draw_row(start, Loc(start.row, end.col))
            self.draw_col(Loc(start.row, end.col), end)
            self.draw_steps(path.steps, Loc(start.row, end.col - 2), Dir.left)
            
        if path.start == Dir.down and path.end == Dir.right:
            self.draw_col(start, Loc(end.row, start.col))
            self.draw_row(Loc(end.row, start.col), end)
            self.draw_steps(path.steps, Loc(end.row - (self.row_scale * 2), start.col), None)      

        if path.start == path.end == Dir.right:
            mid_col = (start.col + end.col) // 2
            (start_mid, end_mid) = (Loc(start.row, mid_col), Loc(end.row, mid_col))
            self.draw_row(start, start_mid)
            self.draw_col(start_mid, end_mid)
            self.draw_row(end_mid, end)
            self.draw_steps(path.steps, Loc(start.row, mid_col), None)

        if path.start == path.end == Dir.down or path.start == path.end == Dir.up:
            (mid_row, mid_col) = ((start.row + end.row) // 2, (start.col + end.col) // 2)
            (start_mid, end_mid) = (Loc(mid_row, start.col), Loc(mid_row, end.col))
            self.draw_col(start, start_mid)
            self.draw_row(start_mid, end_mid)
            self.draw_col(end_mid, end)
            self.draw_steps(path.steps, Loc(mid_row, mid_col), None)
        
    def view_trail(self):
        if self.only_path:
            for (src_id, dst_id) in pairwise(self.only_path):
                if (src_id > dst_id):
                    (src_id, dst_id) = (dst_id, src_id)
                (id, loc, paths) = self.node_dict[src_id]
                for (end_node, path) in paths.path_dict.items():
                    if end_node.id == dst_id:
                        self.draw_path(path, loc, end_node.loc)
        else:
            for (id, loc, paths) in self.nodes:
                for (end_node, path) in paths.path_dict.items():
                    self.draw_path(path, loc, end_node.loc)
        for (id, loc, _) in self.nodes:
            self.mark(loc, str(id % 10))
            if id >= 10:
                self.mark(Dir.left.from_loc(loc), str(id // 10))
        return "\n".join([''.join(line) for line in self.lines])
        
    def __str__(self):
        return "\n".join([''.join(line) for line in self.lines])

# Conformed Nodes
class CNodes(NamedTuple):
    id: int
    nodes: frozenset[Node]

    def __str__(self):
        return f"id {self.id}, done {[node.id for node in self.nodes]}"

    def __repr__(self):
        return f"id {self.id}, done {[node.id for node in self.nodes]}"

class Conformer:
    def __init__(self):
        self.next_id = Counter()
        self.canon: dict[frozenset[Node], CNodes] = {}

    def get(self, obj: frozenset[Node]) -> CNodes:
        if obj not in self.canon:
            self.canon[obj] = CNodes(self.next_id.next(), obj)
        return self.canon[obj]

class StateKey(NamedTuple):
    node_id: int
    done_id: int

class State(NamedTuple):
    node: Node
    steps: int
    done: CNodes

    def key(self) -> StateKey:
        return StateKey(self.node.id, self.done.id)

    def __lt__(self, other: "State"):
        return self.steps < other.steps

    def __str__(self):
        return f"{self.steps} steps, Node {self.node.id}: done {[node.id for node in self.done.nodes]}"

    def __repr__(self):
        return f"{self.steps} steps, Node {self.node.id}: done {[node.id for node in self.done.nodes]}"

class TrailWalker:
    def __init__(self, mapper: TrailMapper):
        self.trail = mapper
        self.conf = Conformer()
        self.nodes_to_walk: KeyedPQ[State, StateKey] = KeyedPQ(
            init_items=[self.get_start_state()],
            key=lambda s: s.key() if s.node != self.trail.end else self.end_key,
            replace_if=lambda a,b: b.steps < a.steps,
        )

    @cached_property
    def end_key(self) -> StateKey:
        return StateKey(self.trail.end.id, 0)

    def get_start_state(self):
        return State(self.trail.start, 0, self.conf.get(frozenset([self.trail.start])))

    def walk_trail(self, max_nodes=100000):
        n = 0
        for node in self.nodes_to_walk.iter():
            self.process_node(node)
            n += 1
            if n >= max_nodes:
                break
        end_state = self.nodes_to_walk.items.get(self.end_key, None)
        return -end_state.steps if end_state else None

    def process_node(self, state: State):
        next_nodes = state.node.paths.nodes - state.done.nodes
        next_states = [self.walk_path(state, node, state.node.paths.get(node).steps) for node in next_nodes]
        self.nodes_to_walk.add_all(next_states)
        
    def walk_path(self, state: State, node: Node, steps: int) -> State:
        return State(node, state.steps - steps, self.conf.get(state.done.nodes | frozenset([node])))

    def get_backtrack(self) -> list[int]:
        end_node = self.trail.end
        end_id = end_node.id
        end_state = self.nodes_to_walk.items.get(self.end_key, None)
        if not end_state:
            return None
        only_nodes = [end_id]
        (node, steps, (_, done)) = end_state
    
        while steps < 0:
            prev_nodes = [n for n in self.trail.nodes.values() if node in n.paths.nodes]
            sticky = node
            for prev_node in prev_nodes:
                path = prev_node.paths.get(node)
                prev_states = [
                    (key, state) for (key, state) in self.nodes_to_walk.items.items()
                    if key != self.end_key and key.node_id == prev_node.id and state.steps == steps + path.steps and (node == end_node or state.done.nodes == done)
                ]
                if len(prev_states) > 0:
                    prev_state = prev_states[0][1]
                    (node, steps, (_, done)) = prev_state
                    done -= frozenset([node])
                    only_nodes.append(node.id)
                    break
            if sticky == node:
                return None
        return rev(only_nodes)

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
process_input(get_input(23), is_slippery=False, max_nodes=2_500_000)   # stops after 2.5m nodes, but arrives at correct answer (~25s)

# process_input(get_input(23), is_slippery=False, max_nodes=13_000_000)   # runs to completion (3~4 minutes)
# process_input(get_input(23), is_slippery=False, max_nodes=2_500_000, view_trail=True)   # prints the longest trail (~40s)
