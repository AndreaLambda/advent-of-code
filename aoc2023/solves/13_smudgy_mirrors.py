# day 13: smudgy mirrors
from modules.parse import get_input

def count_diffs(row_a: list, row_b: list) -> int:
    return sum(1 for (a,b) in zip(row_a, row_b) if a != b)

def check_reflection(pair: tuple[int, int], row_to_rows: dict[int, list[int]], lines: list[str], require_smudge: bool) -> tuple[int, int]:
    (l, r) = pair
    smudges = 0
    while l >= 0 and r < len(row_to_rows):
        if r not in row_to_rows[l]:
            if not require_smudge:
                return None
            smudges += count_diffs(lines[l], lines[r])
            if smudges > 1:
                return None
        l -= 1
        r += 1
    if not require_smudge:
        return pair
    return pair if smudges == 1 else None

def find_reflection(lines: list[str], require_smudge: bool):
    adjacent: list[tuple[int, int]] = []
    terrain_to_rows: dict[str, list[int]] = {}
    row_to_rows: dict[int, list[int]] = {}
    for (idx, line) in enumerate(lines):
        prev = terrain_to_rows.get(line, [])
        row_to_rows[idx] = prev
        prev.append(idx)
        if (idx - 1) in prev:
            adjacent.append((idx-1, idx))
        if require_smudge and idx > 0 and count_diffs(line, lines[idx-1]) == 1:
            adjacent.append((idx-1, idx))
        terrain_to_rows[line] = prev

    for pair in adjacent:
        res = check_reflection(pair, row_to_rows, lines, require_smudge)
        if res is not None:
            return res
    return None

def flip(lines: list[str]) -> list[str]:
    return ["".join(line[col] for line in lines) for col in range(len(lines[0]))]
    
def find_mirror(field: list[str], require_smudge: bool):
    res = ("row", find_reflection(field, require_smudge))
    if res[1] is None:
        res = ("column", find_reflection(flip(field), require_smudge))
    (dir, loc) = res
    return (loc[1] * 100 if dir == "row" else loc[1], dir, loc)

def parse_input(input: str) -> list[list[str]]:
    parts = input.split("\n\n")
    return [part.splitlines() for part in parts]

def process_input(input: str, require_smudge=False):
    fields = parse_input(input)
    res = [find_mirror(field, require_smudge) for field in fields]
    # return res
    return sum([field_res[0] for field_res in res])

# process_input(get_input(13, test=True))
# process_input(get_input(13))
# process_input(get_input(13, test=True), require_smudge=True)
process_input(get_input(13), require_smudge=True)