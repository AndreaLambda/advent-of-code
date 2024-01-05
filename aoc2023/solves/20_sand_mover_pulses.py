# day 20: sand mover pulses
import re
from collections import defaultdict, deque
from enum import Enum
from functools import reduce
from typing import NamedTuple
from modules.parse import get_input


class Role(Enum):
    Button = 1
    Broadcast = 2
    FlipFlop = 3
    Conjunction = 4

    def __repr__(self):
        return self.name


class Node(NamedTuple):
    name: str
    role: Role
    targets: list[str]


class Pulse(Enum):
    Low = False
    High = True

    def flip(self) -> "Pulse":
        return Pulse.High if self == Pulse.Low else Pulse.Low

    def __bool__(self):
        return self.value

    def __str__(self):
        return "L" if self == Pulse.Low else "H"


class SentPulse(NamedTuple):
    source: str
    pulse: Pulse
    target: str


class PulseModule:
    def __init__(self, runner: "PulseRunner", name: str, targets: list[str], **kwargs):
        self.runner = runner
        self.name = name
        self.targets = targets
        self.state = None

    def send(self, pulse: Pulse):
        self.runner.queue(self.name, pulse, self.targets)

    # not all modules react to pulses
    def receive(self, source: str, pulse: Pulse):
        pass

    # only ButtonModule has a button
    def press(self):
        pass

    # only ConjunctionModule tracks cycles
    def get_cycles(self) -> list[int | None]:
        return []

    def code(self):
        return self.name
    
    def __str__(self):
        return self.code()

    def __repr__(self):
        state = f", state={self.state}" if self.state is not None else ''
        return f"{self.__class__.__name__}('{self.name}' -> {self.targets}{state})"


class ButtonModule(PulseModule):
    def press(self):
        self.send(Pulse.Low)


class BroadcastModule(PulseModule):
    def receive(self, _, pulse):
        self.send(pulse)


class FlipFlopModule(PulseModule):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = Pulse.Low

    def receive(self, _, pulse):
        if pulse == Pulse.Low:
            self.state = self.state.flip()
            self.send(self.state)

    def code(self):
        return f"%{self.name}"

    def __str__(self):
        return f"{self.code()}:{str(self.state)}"


class ConjunctionModule(PulseModule):
    def __init__(self, sources: list[str], **kwargs):
        super().__init__(sources=sources, **kwargs)
        self.state: dict[str, Pulse] = {source: Pulse.Low for source in sources}
        self.cycles: dict[str, dict[int, str]] = {source: defaultdict(str) for source in sources}

    def receive(self, source: str, pulse: Pulse):
        if self.state[source] != pulse and len(self.cycles[source]) < 10:
            self.cycles[source][self.runner.cycles] += str(pulse)
            
        self.state[source] = pulse
        self.send(Pulse.Low if all(self.state.values()) else Pulse.High)

    def code(self):
        return f"&{self.name}"

    def get_cycles(self) -> list[int | None]:
        return [cycle[0] if len(cycle) > 0 else None for cycle in [list(value.keys()) for value in self.cycles.values()]]

    def __str__(self):
        return f"{self.code()}:{''.join([str(pulse) for pulse in self.state.values()])}"


role_map = {"%": Role.FlipFlop, "&": Role.Conjunction, "": Role.Broadcast}
role_modules: dict[Role, PulseModule] = {Role.Button: ButtonModule, Role.Broadcast: BroadcastModule, Role.FlipFlop: FlipFlopModule, Role.Conjunction: ConjunctionModule}


class State(NamedTuple):
    cycles: int
    lows: int
    highs: int

class PulseRunner:
    def __init__(self, nodes: list[Node], goal_module="rx", cycles_to_debug: list[int] = []):
        self.modules: dict[str, PulseModule] = {}
        self.pulses: deque[SentPulse] = deque()
        self.cycles = 0
        self.total = {Pulse.Low: 0, Pulse.High: 0}
        self.goal_module: PulseModule = None
        self.gate_module: PulseModule = None
        # debug stuff
        self.source_map = {}
        self.cycles_to_debug = cycles_to_debug
        self.cycle_debugs: dict[int, list[tuple]] = defaultdict(list)

        self.build_modules(nodes, goal_module)


    def build_modules(self, nodes: list[Node], goal_module: str):
        nodes.append(Node("button", Role.Button, ["broadcaster"]))
        source_map = defaultdict(list)
        for node in nodes:
            for target in node.targets:
                source_map[target].append(node.name)
        self.source_map = source_map
        
        for node in nodes:
            module: PulseModule = role_modules[node.role](runner=self, name=node.name, targets=node.targets, sources=source_map[node.name])
            self.modules[node.name] = module

        # could probably use map_sources programmatically
        self.gate_module = self.get_module("nr")
        self.goal_module = self.get_module(goal_module)


    def print_source_map(self, show_depth=4):
        sand = self.get_module("rx")
        self.print_sources([sand], show_depth)

    def print_sources(self, modules: list[PulseModule], show_depth: int, at_depth=1, already: dict[str, bool]={}):
        for module in modules:
            already[module.name] = True
        sources = {module.code(): [self.get_module(source) for source in self.source_map[module.name]] for module in modules}
        print("   ".join([f"{target}: {[source.code() for source in sourcelist]}" for (target, sourcelist) in sources.items()]))
        next_row = [module for source in sources.values() for module in source if module.name not in already]
        if at_depth == show_depth or len(next_row) == 0:
            return
        self.print_sources(next_row, show_depth, at_depth + 1, already) 
    
    def get_module(self, name: str) -> PulseModule:
        if name not in self.modules:
            self.modules[name] = PulseModule(self, name, [])
        return self.modules[name]
        
    def queue(self, source: str, pulse: Pulse, targets: list[str]):
        # debug: cycle_pulses
        if self.cycles in self.cycles_to_debug:
            module = self.modules[source]
            self.cycle_debugs[self.cycles].append(("queue", module.code(), pulse.name, targets, str(module)))

        self.pulses += [SentPulse(source, pulse, target) for target in targets]
            
    def run_cycles(self, max_cycles) -> "PulseRunner":
        while self.cycles < max_cycles:
            self.run_cycle()
        return self
    
    def run_cycle(self):
        self.cycles += 1
        self.modules["button"].press()
        while self.pulses:
            pulse = self.pulses.popleft()
            target = self.get_module(pulse.target)
            # debug: cycle_pulses
            if self.cycles in self.cycles_to_debug:
                self.cycle_debugs[self.cycles].append(("receive", target.code(), pulse.source, pulse.pulse.name, str(target)))
            target.receive(pulse.source, pulse.pulse)
            self.total[pulse.pulse] += 1

    def get_pulse_product(self):
        return self.total[Pulse.High] * self.total[Pulse.Low]

    def calculate_sand_cycle(self) -> int:
        cycles = self.gate_module.get_cycles()
        if not all(cycles):
            raise Exception("not all cycles were identified", cycles)
        return reduce(lambda a,b: a*b, cycles)


def parse_line(line) -> Node:
    (role, name, targets) = re.match(r"([%&]?)([a-z]+) -> (.*)", line).groups()
    return Node(name, role_map[role], targets.split(", "))
    
def parse_input(input) -> list[Node]:
    lines = input.splitlines()
    nodes = [parse_line(line) for line in lines]
    return nodes

# formatting the output of debug_cycles
def format_output(cycle_outputs):
    return [(cycle, [f"{'':60}{format_queue(line):80}" if line[0] == "queue" else f"{format_pulse(line):140}" for line in output]) for (cycle, output) in cycle_outputs.items()]
    
def format_pulse(line):
    return f"""{f"{line[1]}{f' ({line[4]})' if line[4] else ''}":18} <- {line[3]:6} <- {line[2]}"""

def format_queue(line):
    return f"""{f"{line[1]}{f' ({line[4]})' if line[4] else ''}":14} -> {line[2]:6} -> {line[3]}"""
     
def process_input(input, calculate_sand=False, cycles_to_run=1000, cycles_to_debug=[]):
    nodes = parse_input(input)
    runner = PulseRunner(nodes, cycles_to_debug=cycles_to_debug).run_cycles(cycles_to_run)
    if calculate_sand:
        return runner.calculate_sand_cycle()
    else:
        return runner.get_pulse_product()


# process_input(get_input(20, file="test_1"))
# process_input(get_input(20, file="test_2"))
# process_input(get_input(20))
process_input(get_input(20), calculate_sand=True, cycles_to_run=10000)
