# day 21: hedge maze stepcounts
from math import ceil
from modules.array_math import shifted_diff, addwise, mult
from modules.parse import find_in_input, get_input
from modules.types import Loc, Dir
from modules.utils import batched

class MazeWalker:
    def __init__(self, maze: list[str], start: Loc):
        self.maze = maze
        self.size = max(len(self.maze), len(self.maze[0]))
        self.start = start
        self.steps = 0

        self.all_reached: set[Loc] = set()
        self.reached_at: list[list[Loc]] = []

        self.found_cycle = False
        self.cycle_diff = None
        self.cycle_counts = None


    def is_valid(self, loc: Loc) -> bool:
        arr_row = loc.row % len(self.maze)
        arr_col = loc.col % len(self.maze[0])
        return self.maze[arr_row][arr_col] != "#"
  
    def get_valid_neighbors(self, loc: Loc) -> list[Loc]:
        adjacent = [dir.from_loc(loc) for dir in Dir]
        return [x for x in adjacent if self.is_valid(x)]
        
    def walk_steps(self, steps: int):
        if steps <= 0:
            return
        
        prev_reached = [self.start] if self.steps == 0 else self.reached_at[-1]
        for _ in range(steps):
            new_reached = []
            for prev_loc in prev_reached:
                neighbors = self.get_valid_neighbors(prev_loc)
                for neighbor in neighbors:
                    if neighbor not in self.all_reached:
                        new_reached.append(neighbor)
                        self.all_reached.add(neighbor)
            self.reached_at.append(new_reached)
            prev_reached = new_reached

        self.steps += steps

    def find_cycle(self) -> bool:
        counts = [len(steps) for steps in self.reached_at]
        batched_counts = [list(batch) for batch in batched(counts, self.size)]
        batched_diffs = [list(batch) for batch in batched(shifted_diff(counts, self.size), self.size)]
        # if the diffs of the last three batches are the same, the rate of growth per cycle is stable
        if batched_diffs[-1] == batched_diffs[-2] == batched_diffs[-3]:
            self.found_cycle = True
            self.cycle_diff = batched_diffs[-1]
            self.cycle_counts = batched_counts
        return self.found_cycle
    
    def walk_until_cycle(self):
        # comparing three batches of diffs means we need at least 4x the width of the maze in steps
        # also want to have an even number of cycles so far to make the math less headachey
        min_steps = self.size * 4 - self.steps
        round_up = -self.steps % (self.size * 2)
        self.walk_steps(max(min_steps, round_up))

        cycle = self.find_cycle()        
        while not cycle:
            self.walk_steps(self.size * 2)
            cycle = self.find_cycle()
        
    def can_reach_exactly(self, goal: int) -> int:
        self.walk_until_cycle()
        odd_even_idx = (goal + 1) % 2
        if goal <= self.steps:
            return sum(len(step) for step in self.reached_at[odd_even_idx:goal:2])
        else:
            current = sum(len(step) for step in self.reached_at[odd_even_idx:self.steps:2])
            return self.calculate_reach_exactly(goal, current)

    def calculate_reach_exactly(self, goal: int, current_reached: int) -> int:
        # the step counts for the previous two cycles
        start_cycle = self.steps // self.size
        prev_two = self.cycle_counts[start_cycle -2 :start_cycle]

        # the step counts for the next two cycles
        next_cycle = addwise(prev_two[1], self.cycle_diff)
        next_next_cycle = addwise(next_cycle, self.cycle_diff)
        next_two_cycle = [x for cycle in [next_cycle, next_next_cycle] for x in cycle]
    
        # the next step (start + 1) will be element 0; start + 2 is element 1
        # since we're dealing with even numbers so far, we can safely filter out the odds or evens as appropriate
        odd_even_idx = (goal + 1) % 2
        next_relevant = next_two_cycle[odd_even_idx::2]
        next_sum = sum(next_relevant)

        # do the same with cycle_diff; because we're dealing with two cycles at a time, double the cycle_diff values
        diff_repeated = self.cycle_diff * 2
        diff_relevant = diff_repeated[odd_even_idx::2]
        diff_two_cycle = mult(diff_relevant, 2)
        diff_two_cycle_sum = sum(diff_two_cycle)

        # number of full cycles to "do math" with; leave the remainder for the final step
        math_cycles = (goal - self.steps) // (self.size * 2)
        # formula for the sum of (x, x+a, x+2a, ... x+na) is the average of first and last, times the number of elements
        # so the number of elements is (n - 1), and the average is (x + (x+na)) / 2
        math_total = (math_cycles * (next_sum + (next_sum + diff_two_cycle_sum * (math_cycles - 1))) // 2)

        steps_after_math = self.steps + math_cycles * (self.size * 2)
        steps_left = goal - steps_after_math

        # the final set of step counts is the next set of step counts after the formula above, x+(n+1)a
        # if the "goal" number of steps is equal to steps_after_math, we add nothing here
        # if the "goal" is odd, the next step count is for an odd number of steps, so take the first element
        # then, add the step counts for each remaining pair of steps
        final_relevant = addwise(next_relevant, mult(diff_two_cycle, math_cycles))
        is_odd = goal % 2
        final_sum = sum(final_relevant[0:(steps_left // 2) + is_odd])

        final_total = current_reached + math_total + final_sum
        return final_total
    
    def print_maze(self):
        tiles = 1
        if self.all_reached:
            nums = ([num for loc in self.all_reached for num in loc])
            width = max(nums) - min(nums)
            tiles = ceil(width / len(self.maze))
            tiles += 1 if tiles % 2 == 0 else 0
        
        maze = [list(ex_line) for ex_line in [line * tiles for line in self.maze] * tiles]
        padding = (tiles // 2) * len(self.maze) 
        for (step, reached) in enumerate(self.reached_at):
            for loc in reached:
                maze[loc.row + padding][loc.col + padding] = str((step + 1) % 10)
        maze[self.start.row + padding][self.start.col + padding] = "S"
        print('\n'.join([''.join(row) for row in maze]))


def parse_input_and_find(input: str, char: str, replace: str) -> tuple[list[str], Loc]:
    char_loc = find_in_input(input, char)
    lines = input.splitlines()
    lines[char_loc.row] = lines[char_loc.row].replace(char, replace)
    return (lines, char_loc)

def process_input(input: str, steps: int) -> int:
    (maze, start_loc) = parse_input_and_find(input, "S", ".")
    return MazeWalker(maze, start_loc).can_reach_exactly(steps)


# assert process_input(get_input(21, test=True), steps=6) == 16
# process_input(get_input(21), steps=64)
# assert process_input(get_input(21, test=True), steps=5_000) == 16_733_044
process_input(get_input(21), steps=26_501_365)
