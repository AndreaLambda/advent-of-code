# day 19: parts workflows
import re
from enum import Enum
from typing import Literal, NamedTuple
from modules.parse import get_input

class Result(Enum):
    Accept = 1
    Reject = 2

NextStep = Result | str
Stat = Literal["x", "m", "a", "s"]

class Step(NamedTuple):
    stat: Stat
    oper: callable
    num: int
    next: NextStep

class Flow(NamedTuple):
    name: str
    steps: list[Step]
    default: NextStep

class Part(NamedTuple):
    x: int
    m: int
    a: int
    s: int

    def get_score(self) -> int:
        return self.x + self.m + self.a + self.s

class MinMax(NamedTuple):
    min: int
    max: int

    def total(self):
        return self.max - self.min + 1

    def __repr__(self):
        return f"{self.min:4} ~ {self.max:4}"

class SuperPart(NamedTuple):
    x: MinMax
    m: MinMax
    a: MinMax
    s: MinMax

    def get_total(self) -> int:
        return self.x.total() * self.m.total() * self.a.total() * self.s.total()

class SuperPartSplitter:
    def __init__(self, part: SuperPart, stat: Stat):
        self.x = part.x
        self.m = part.m
        self.a = part.a
        self.s = part.s
        self.stat: Stat = stat

    def create_split(self, minmax: MinMax):
        setattr(self, self.stat, minmax)
        return SuperPart(self.x, self.m, self.a, self.s)

def oper_lt(stat: int, num: int) -> bool:
    return stat < num

def oper_gt(stat: int, num: int) -> bool:
    return stat > num

def super_lt(minmax: MinMax, num: int) -> tuple[MinMax, MinMax] | bool:
    (min, max) = minmax
    if max < num:
        return True
    if min >= num:
        return False
    return (MinMax(min, num - 1), MinMax(num, max))

def super_gt(minmax: MinMax, num: int) -> tuple[MinMax, MinMax] | bool:
    (min, max) = minmax
    if min > num:
        return True
    if max <= num:
        return False
    return (MinMax(num + 1, max), MinMax(min, num))

opers = {"<": oper_lt, ">": oper_gt}
super_opers = {"<": super_lt, ">": super_gt}
results = {"A": Result.Accept, "R": Result.Reject}


class FlowRunner:
    def __init__(self, flows: list[Flow], parts: list[Part]):
        self.flows: dict[str, Flow] = {flow.name: flow for flow in flows}
        self.parts = parts

    def get_score(self) -> int:
        return sum([self.rate_part(part) for part in self.parts])

    def rate_part(self, part: Part) -> int:
        next_step = "in"
        while next_step not in [Result.Accept, Result.Reject]:
            next_step = self.run_flow(self.flows[next_step], part)
        return part.get_score() if next_step == Result.Accept else 0
            
    def run_flow(self, flow: Flow, part: Part) -> NextStep:
        for step in flow.steps:
            if (next_step := self.run_step(step, part)) is not None:
                return next_step
        return flow.default
        
    def run_step(self, step: Step, part: Part) -> NextStep:
        return step.next if step.oper(getattr(part, step.stat), step.num) else None


class SuperFlowRunner:
    def __init__(self, flows: list[Flow]):
        self.flows = {flow.name: flow for flow in flows}

    def get_score(self) -> int:
        minmax = MinMax(1, 4000)
        part = SuperPart(minmax, minmax, minmax, minmax)
        return self.score_flow(self.flows["in"], part)

    def score_flow(self, flow: Flow, superpart: SuperPart) -> int:
        total = 0
        for (part, next_step) in self.run_flow(flow, superpart):
            if next_step == Result.Reject:
                continue
            if next_step == Result.Accept:
                total += part.get_total()
            else:
                total += self.score_flow(self.flows[next_step], part)
            
        return total
        
    def run_flow(self, flow: Flow, part: SuperPart) -> list[tuple[SuperPart, NextStep]]:
        next_steps: list[tuple[SuperPart, NextStep]] = []
        remain_part = part
        for step in flow.steps:
            (next_part, remain_part) = self.run_step(step, remain_part)
            if next_part is not None:
                next_steps.append(next_part)
            if remain_part is None:
                break
        if remain_part is not None:
            next_steps.append((remain_part, flow.default))
        return next_steps
        
    def run_step(self, step: Step, part: SuperPart) -> tuple[tuple[SuperPart, NextStep] | None, SuperPart | None]:
        res = step.oper(getattr(part, step.stat), step.num)
        if res is True:
            return ((part, step.next), None)
        if res is False:
            return (None, part)
        (next_part, remain_part) = res
        splitter = SuperPartSplitter(part, step.stat)
        return ((splitter.create_split(next_part), step.next), splitter.create_split(remain_part))

def parse_flow(line, use_opers):
    (name, steps_str, default) = re.match(r"(.+){(.+,)(.+)}", line).groups()
    steps = [Step(stat, use_opers[oper], int(num), results.get(next, next)) for (stat, oper, num, next) in re.findall(r"([xmas])(.)([0-9]+):([ARa-z]+)", steps_str)]
    return Flow(name, steps, results.get(default, default))
    
def parse_part(line):
    (x, m, a, s) = re.match(r"{x=([0-9]+),m=([0-9]+),a=([0-9]+),s=([0-9]+)}", line).groups()
    return Part(int(x), int(m), int(a), int(s))
    
def parse_input(input, is_super):
    opers_dict = super_opers if is_super else opers
    (flows, parts) = [section.splitlines() for section in input.split("\n\n")]
    flows = [parse_flow(flow, opers_dict) for flow in flows]
    parts = [parse_part(part) for part in parts]
    return (flows, parts)

def process_input(input, is_super=False):
    (flows, parts) = parse_input(input, is_super)
    runner = SuperFlowRunner(flows) if is_super else FlowRunner(flows, parts)
    return runner.get_score()

# process_input(get_input(19, test=True))
# process_input(get_input(19))
# process_input(get_input(19, test=True), is_super=True)
process_input(get_input(19), is_super=True)
