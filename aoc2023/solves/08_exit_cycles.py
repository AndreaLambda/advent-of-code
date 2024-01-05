# 8: exit cycles (cleaned-up solution)
import re
from functools import reduce
from math import lcm
from modules.parse import get_input

class Room:
    def __init__(self, id: str, l_id: str, r_id: str):
        self.id = id
        self.l_id = l_id
        self.r_id = r_id
        # initialize cycle details for later
        self.cycle: Room = self
        self.steps = 0
        self.exits: list[int] = []
        # set these details later after all rooms are initialized
        self.l: Room = None
        self.r: Room = None
        self.start = False
        self.exit = False

    # set links to the actual rooms, and set whether this room is a start or exit
    def set_details(self, l_room: "Room", r_room: "Room", is_start: bool, is_exit: bool):
        self.l = l_room
        self.r = r_room
        self.start = is_start
        self.exit = is_exit

    # run the initial cycle using the directions
    def run_cycle(self, dirs: str):
        for (num, dir) in enumerate(dirs):
            self.cycle = self.cycle.l if dir == "L" else self.cycle.r
            if self.cycle.exit:
                self.exits.append(num+1)
            self.steps = len(dirs)

    # iterate the cycle using the cycle room's cycle details
    def iter_cycle(self):
        other = self.cycle
        self.exits = self.exits + [self.steps + exit for exit in other.exits]
        self.steps += other.steps
        self.cycle = other.cycle

    def __repr__(self):
        return f"id: {self.id}, cycle: {self.cycle.id}, steps: {self.steps}, exits: {self.exits}"

def parse_input(input) -> tuple[str, dict[str, Room]]:
    [dirs, _, *lines] = input.splitlines()
    rooms = {}
    for line in lines:
        parsed = re.match(r"([\w]{3}) = \(([\w]{3}), ([\w]{3})\)", line).groups()
        room = Room(*parsed)
        rooms[room.id] = room
    return (dirs, rooms)

# iterate the cycle of each relevant room
def iter_cycle(rooms: list[Room]):
    for room in rooms:
        room.iter_cycle()

def find_lcm(escapes_list: list[int]) -> int:
    return reduce(lcm, escapes_list)

def escape(dirs: str, rooms: list[Room]):
    start_rooms = [room for room in rooms if room.start]
    # run one full cycle for every room
    for room in rooms:
        room.run_cycle(dirs)
    # trim out any rooms that aren't starters and don't come from anywhere else
    relevant_ids = [room.cycle.id for room in rooms] + [room.id for room in start_rooms]
    rooms = [room for room in rooms if room.id in relevant_ids]
    # only need one exit for each starting room, since the exits seem to be clean multiples
    while any(len(room.exits) == 0 for room in start_rooms):
        iter_cycle(rooms)
    # lowest common multiple of each starting room's first exit
    return find_lcm([room.exits[0] for room in start_rooms])

def get_aaa_start(_) -> list[str]:
    return ["AAA"]

def get_multi_starts(rooms) -> list[str]:
    return [room for room in rooms.keys() if room.endswith('A')]

def get_zzz_end(_) -> list[str]:
    return ["ZZZ"]

def get_multi_ends(rooms) -> list[str]:
    return [room for room in rooms.keys() if room.endswith('Z')]
    
def process_input(input, multi=False):
    (dirs, rooms) = parse_input(input)
    (starts, ends) = (get_multi_starts(rooms), get_multi_ends(rooms)) if multi else (get_aaa_start(rooms), get_zzz_end(rooms))
    for room in rooms.values():
        room.set_details(rooms[room.l_id], rooms[room.r_id], room.id in starts, room.id in ends)
    return escape(dirs, rooms.values())

# process_input(get_input(8, file="test_1"))
# process_input(get_input(8))
# process_input(get_input(8, file="test_2"), multi=True)
process_input(get_input(8), multi=True)