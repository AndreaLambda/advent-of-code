# day 12: springcross (DP approach, works with unfold)
from modules.parse import get_input

class PuzzleLine:
    def __init__(self, puzzle: str, clues: list[int]):
        self.puzzle = puzzle
        self.clues = clues
        self.hashes = self.get_hashes()
        self.hash_total = self.get_hash_total()
        self.counts: dict[int, list[tuple[int, int]]] = {}

    def get_hashes(self) -> list[int]:
        return [1 if piece == "#" else 0 for piece in self.puzzle]

    def get_hash_total(self) -> list[int]:
        total = 0
        return [total := (total + 1 if piece == "#" else total) for piece in self.puzzle]

    def get_count(self) -> int:
        self.count_clue(len(self.clues) - 1)
        total_hashes = self.hash_total[-1]
        total = sum([total for (total, hashes) in self.count_clue(len(self.clues) - 1) if hashes == total_hashes])
        return total

    def count_clue(self, clue_num=0) -> list[tuple[int, int]]:
        if (counted := self.counts.get(clue_num)):
            return counted

        if clue_num == 0:
            return self.count_first_clue()
        
        prev = self.count_clue(clue_num - 1)
        valid = [(0, 0) for idx in range(0, len(self.puzzle))]
        clue_size = self.clues[clue_num]
        for idx in range(2, len(self.puzzle) - clue_size + 1):
            (head, tail) = (idx, idx + clue_size - 1)
            part = self.puzzle[head:tail+1]
            if "." not in part:
                hashes = sum(self.hashes[head:tail+1])
                total = 0
                for prev_valid in prev[0:head - 1]:
                    if prev_valid[1] + hashes == self.hash_total[tail]:
                        total += prev_valid[0]
                if total > 0:
                    valid[tail] = (total, self.hash_total[tail])

        self.counts[clue_num] = valid
        return valid

    def count_first_clue(self, clue_num=0) -> list[tuple[int, int]]:
        valid = [(0, 0) for idx in range(0, len(self.puzzle))]
        clue_size = self.clues[clue_num]
        for idx in range(0, len(self.puzzle) - clue_size + 1):
            (head, tail) = (idx, idx + clue_size - 1)
            part = self.puzzle[head:tail+1]
            if "." not in part:
                hashes = sum(self.hashes[head:tail+1])
                if hashes == self.hash_total[tail]:
                    valid[tail] = (1, hashes)
        self.counts[clue_num] = valid
        return valid

# parsers
def unfold_line(puzzle: str, clues: list[int]) -> tuple[str, list[int]]:
    return ("?".join([puzzle] * 5), clues * 5)
    
def parse_line(line: str, unfold=False) -> PuzzleLine:
    (puzzle, clues) = line.split(" ")
    clues = [int(clue) for clue in clues.split(",")]
    if unfold:
        (puzzle, clues) = unfold_line(puzzle, clues)
    return PuzzleLine(puzzle, clues)
    
def parse_input(input: str, unfold=False) -> list[PuzzleLine]:
    lines = input.splitlines()
    return [parse_line(line, unfold) for line in lines]  

def process_input(input: str, unfold=False):
    lines = parse_input(input, unfold)
    return sum([line.get_count() for line in lines])

# process_input(get_input(12, test=True))
# process_input(get_input(12))
# process_input(get_input(12, test=True), unfold=True)
process_input(get_input(12), unfold=True)
