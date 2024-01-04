# day 4: scratch-off tickets
from math import pow
from modules.array_math import add
from modules.parse import get_input

# 4-1
def card_matches(card: str):
    parts = card.split(": ")[1].split(" | ")
    yours = set([num for num in parts[1].split(" ")])
    wins = [num for num in parts[0].split(" ") if num in yours]
    return len(wins)

def score_card(card: str):
    return int(pow(2, card_matches(card) - 1))

# 4-2
def total_cards(cards: list[str]):
    res = [1] * len(cards)
    for (idx, card) in enumerate(cards):
        matches = card_matches(card)
        res[idx+1:idx+matches+1] = add(res[idx+1:idx+matches+1], res[idx])
    return sum(res)

def process_input(input, total=False):
    cards = input.replace("  ", " 0").splitlines()
    if total:
        return total_cards(cards)
    else:
        return sum([score_card(card) for card in cards])

# process_input(get_input(4, test=True))
# process_input(get_input(4))
# process_input(get_input(4, test=True), total=True)
process_input(get_input(4), total=True)