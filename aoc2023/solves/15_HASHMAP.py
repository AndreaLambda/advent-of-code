# day 15: HASHMAP
import re
from modules.parse import get_input

# sod naming convention, going with "rule of cool" for this one
class HASHMAP:
    def __init__(self, seq: list[str]):
        self.seq = seq
        self.boxes: dict[int, list[str]] = {}
        self.focals: dict[str, int] = {}

    def get_operation(self, step: str) -> tuple[str, callable, str]:
        (label, oper, num) = re.match(r"(.*)([-=])([1-9])?", step).groups()
        oper = self.remove if oper == "-" else self.add_or_replace
        return (label, oper, num)

    def remove(self, box: list[str], label: str, _):
        if label in box:
            box.remove(label)

    def add_or_replace(self, box: list[str], label: str, focal: str):
        if label not in box:
            box.append(label)
        self.focals[label] = int(focal)
        
    def run_sequence(self):
        for step in self.seq:
            (label, oper_to_run, num) = self.get_operation(step)
            box_num = HASH(label)
            self.boxes[box_num] = self.boxes.get(box_num, [])
            oper_to_run(self.boxes[box_num], label, num)

    def get_focal_power(self) -> int:
        return sum([self.get_box_focal_power(box_num, box) for (box_num, box) in self.boxes.items()])

    def get_box_focal_power(self, box_num: int, box) -> int:
        return sum([(box_num + 1) * (idx + 1) * (self.focals[label]) for (idx, label) in enumerate(box)])

    def boxes_to_str(self) -> str:
        return ";  ".join([f"{box_num}: {self.box_to_str(box)}" for (box_num, box) in self.boxes.items() if len(box) > 0])

    def box_to_str(self, box: list[str]) -> str:
        return " ".join([f"[{label} {self.focals[label]}]" for label in box])


def HASH(step) -> int:
    res = 0
    for part in step:
        res += ord(part)
        res = (res * 17) % 256
    return res
    
def parse_input(input: str) -> list[str]:
    return input.split(",")

def process_input(input: str, do_lenses=False):
    seq = parse_input(input)
    if do_lenses:
        hashmap = HASHMAP(seq)
        hashmap.run_sequence()
        return hashmap.get_focal_power()
    else:
        res = [HASH(step) for step in seq]
        return sum(res)

# process_input(get_input(15, test=True))
# process_input(get_input(15))
# process_input(get_input(15, test=True), do_lenses=True)
process_input(get_input(15), do_lenses=True)
