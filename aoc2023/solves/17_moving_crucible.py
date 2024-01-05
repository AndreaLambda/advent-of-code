# day 17: moving crucible (slow, but works)
from heapq import heappop, heappush
from typing import NamedTuple, Union
from modules.parse import get_input
from modules.types import Dir, Loc
from modules.utils import rev

class Moved(NamedTuple):
    dir: Union[Dir, None]
    blocks: int

    def __repr__(self):
        return f"({self.dir.name if self.dir else None}, {self.blocks})"

class State(NamedTuple):
    cost: int
    moved: Moved = Moved(None, 0)

    def __repr__(self):
        return f"State({self.cost}, {self.moved})"

class Move(NamedTuple):
    cost: int
    loc: Loc
    
class Block:
    def __init__(self, loc: Loc, move_cost: int, is_ultra: bool = False):
        self.loc = loc
        self.move_cost = move_cost
        self.states: list[State] = []
        self.new_states: list[State] = []
        self.is_ultra = is_ultra

    # add the new state unless it is objectively worse than an existing one in the same direction
    # return the next cost of this Block if it changes as a result of adding
    def try_add(self, new_state: State):
        remove = []
        for state in self.states:
            # special case - the state for the starting location is always objectively best
            if state.moved.dir is None:
                return None
            if self.is_ultra:
                # because of the "ultra" turning rules, fewer/more blocks doesn't make it obsolete - only compare cost
                if state.moved.dir == new_state.moved.dir and new_state.moved.blocks == state.moved.blocks:
                    if new_state.cost >= state.cost:
                        # the new state is obsolete - don't add it
                        return None
                    else:
                        # this old state is obsolete
                        remove.append(state)
            else:
                # only objectively worse if another state has same or fewer blocks and cost
                if state.moved.dir == new_state.moved.dir:
                    if new_state.moved.blocks >= state.moved.blocks and new_state.cost >= state.cost:
                        # the new state is obsolete - don't add it
                        return None
                    if new_state.moved.blocks <= state.moved.blocks and new_state.cost <= state.cost:
                        # this old state is obsolete
                        remove.append(state)

        old_cost = self.get_next_state_cost()
        for state in remove:
            self.states.remove(state)
            if state in self.new_states:
                self.new_states.remove(state)
        heappush(self.states, new_state)
        heappush(self.new_states, new_state)
        new_cost = self.get_next_state_cost()
        return (old_cost, new_cost) if (new_cost != old_cost) else None

    def get_next_state(self):
        return heappop(self.new_states)

    def get_next_state_cost(self):
        return None if not self.new_states else self.new_states[0].cost

    def get_cost_to_reach(self):
        return None if not self.states else self.states[0].cost

    def __repr__(self):
        return f"Block({self.new_states}; {self.states})"
    

class City:
    def __init__(self, lines: list[str], is_ultra=False):
        self.lines = lines
        self.is_ultra = is_ultra
        self.rows = len(lines)
        self.cols = len(lines[0])
        self.finished = False
        self.moves: list[Move] = []
        self.blocks: dict[Loc, Block] = {}
        self.start = Loc(0, 0)
        self.goal = Loc(self.rows - 1, self.cols - 1)
        self.add_starting_block()

    def add_starting_block(self, init_move_cost=0):
        block = self.get_block(self.start)
        block.try_add(State(init_move_cost))
        heappush(self.moves, Move(init_move_cost, self.start))

    def get_block(self, loc: Loc):
        if loc in self.blocks:
            return self.blocks[loc]
        new_block = Block(loc, int(self.lines[loc.row][loc.col]), self.is_ultra)
        self.blocks[loc] = new_block
        return new_block

    def is_valid_loc(self, loc: Loc):
        return (0 <= loc.row < self.rows) and (0 <= loc.col < self.cols)

    # 1. inside city limits
    # 2. can't move opposite direction
    # 3. can't move more than 3 blocks in same direction
    def get_valid_dirs(self, loc: Loc, state: State):
        (cur_dir, cur_blocks) = state.moved
        if self.is_ultra:
            return [dir for dir in Dir
                    if self.is_valid_loc(dir.from_loc(loc))
                    and (cur_dir is None or ((cur_dir.opposite is not dir) and ((cur_dir == dir and cur_blocks < 4) or (4 <= cur_blocks <= 9) or (cur_dir != dir and cur_blocks >= 10))))]
        else:
            return [dir for dir in Dir
                    if self.is_valid_loc(dir.from_loc(loc))
                    and (cur_dir is None or ((cur_dir.opposite is not dir) and (cur_dir is not dir or cur_blocks < 3)))]

    def process_n_moves(self, num: int):
        for x in range(num):
            self.process_next_move()
            if self.finished:
                return

    def find_shortest_path(self):
        while not self.finished:
            self.process_next_move()
        return self.blocks[self.goal].get_cost_to_reach()
    
    def process_next_move(self):
        if not self.moves:
            raise Exception("no more moves!")
        move = heappop(self.moves)
        if move.loc == self.goal:
            self.finished = True
            return
        block = self.blocks[move.loc]
        state = block.get_next_state()

        valid_dirs = self.get_valid_dirs(move.loc, state)
        for dir in valid_dirs:
            new_loc = dir.from_loc(move.loc)
            new_blocks = 1 if dir != state.moved.dir else state.moved.blocks + 1
            new_block = self.get_block(new_loc)
            res = new_block.try_add(State(state.cost + new_block.move_cost, Moved(dir, new_blocks)))
            if res is not None:
                (old_cost, new_cost) = res
                if old_cost is not None:
                    self.moves.remove(Move(old_cost, new_loc))
                heappush(self.moves, Move(new_cost, new_loc))
        if (next := block.get_next_state_cost()) is not None:
            heappush(self.moves, Move(next, block.loc))

    def get_previous_state(self, block: Block, state: State):
        (dir, blocks) = state.moved
        prev_loc = dir.retrace_from(block.loc)
        prev_block = self.blocks[prev_loc]
        prev_cost = state.cost - block.move_cost
        for prev_state in prev_block.states:
            (prev_dir, prev_blocks) = prev_state.moved
            if prev_state.cost == prev_cost and ((blocks > 1 and blocks == prev_blocks + 1 and prev_dir == dir) or (blocks == 1 and prev_dir != dir)):
                return (prev_block, prev_state)
        raise Exception("noph!", block, state)
        
    def get_shortest_path(self):
        path = []
        block = self.blocks[self.goal]
        state = block.states[0]
        path.append((self.goal, state))
        while block.loc is not self.start:
            (block, state) = self.get_previous_state(block, state)
            path.append((block.loc, state))
        return rev(path)

def parse_input(input: str) -> list[str]:
    return input.splitlines()

def process_input(input: str, is_ultra=False):
    lines = parse_input(input)
    city = City(lines, is_ultra)
    return city.find_shortest_path()


# process_input(get_input(17, test=True))
# process_input(get_input(17))
# process_input(get_input(17, test=True), is_ultra=True)
process_input(get_input(17), is_ultra=True)
