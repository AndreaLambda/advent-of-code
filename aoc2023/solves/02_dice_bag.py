# day 2: dice bag
from typing import NamedTuple
from modules.parse import get_input

# only 12 red cubes, 13 green cubes, and 14 blue cubes
dice = {"red": 12, "green": 13, "blue": 14}

class Game(NamedTuple):
    num: int
    rounds: list[dict[str, int]]

def parse_game(line):
    (game_num, rounds) = line.split(": ")
    game_num = int(game_num.replace("Game ", ""))
    rounds = [{(cnsplit := color_num.split(" "))[1]: int(cnsplit[0]) for color_num in round.split(", ")} for round in rounds.split("; ")]
    return Game(game_num, rounds)

# 2-1
def validate_game(game: Game):
    for round in game.rounds:
        for (color, num) in round.items():
            if num > dice[color]:
                return 0
    return game.num

# 2-2
def get_power(game: Game):
    min = {"red": 0, "green": 0, "blue": 0}
    for round in game.rounds:
        for (color, num) in round.items():
            min[color] = max(num, min[color])
    return min["red"] * min["green"] * min["blue"]


def parse_input(input):
    return [parse_game(line) for line in input.splitlines()]

def process_input(input, find_power=False):
    games = parse_input(input)
    if find_power:
        return sum([get_power(game) for game in games])
    else:
        return sum([validate_game(game) for game in games])

# process_input(get_input(2, True))
# process_input(get_input(2))
# process_input(get_input(2, True), True)
process_input(get_input(2), True)