# day 7: camel poker
from modules.parse import get_input

hand_rank = ["highcard", "1pair", "2pair", "3kind", "fullhouse", "4kind", "5kind"]
card_rank = "123456789VWXYZ"

# sorts by number of cards of a type, then the type's rank
def sort_hand(input_hand):
    cards = {}
    jokers = 0
    for card in input_hand:
        cards[card] = cards.get(card, 0) + 1
    if cards.get("1") and len(cards) > 1:
        jokers = cards["1"]
        cards.pop("1")
    cards = [group for group in cards.items()]
    cards = sorted(cards, key=lambda group: card_rank.index(group[0]), reverse=True)
    cards = sorted(cards, key=lambda group: group[1], reverse=True)
    res = ""
    # add jokers to the largest group
    if jokers > 0:
        res += cards[0][0] * jokers
    for group in cards:
        res += group[0] * group[1]
    return res

def hand_type(input_hand):
    hand = sort_hand(input_hand)
    if hand[0] == hand[4]:
        return "5kind"
    if hand[0] == hand[3]:
        return "4kind"
    if hand[0] == hand[2] and hand[3] == hand[4]:
        return "fullhouse"
    if hand[0] == hand[2]:
        return "3kind"
    if hand[0] == hand[1] and hand[2] == hand[3]:
        return "2pair"
    if hand[0] == hand[1]:
        return "1pair"    
    return "highcard"

def process_line(line):
    parts = line.split(" ")
    return (parts[0], int(parts[1]))

def rank_hands(all_hands):
    # lex sort, lower-ranked cards first
    res = sorted(all_hands)
    res = [(hand, hand_rank.index(hand_type(hand))) for hand in res]
    # hand-rank sort, lower-ranked hands first
    res = sorted(res, key=lambda hand: hand[1])
    # print(res)
    return [hand[0] for hand in res]

def process_input(input, jokers_wild=False):
    input = input.replace("T", "V").replace("Q", "X").replace("K", "Y").replace("A", "Z")
    input = input.replace("J", "1") if jokers_wild else input.replace("J", "W")
    all_camels = [process_line(line) for line in input.splitlines()]
    all_hands = [camel[0] for camel in all_camels]
    ranked_hands = rank_hands(all_hands)
    payouts = [camel[1] * (ranked_hands.index(camel[0]) + 1) for camel in all_camels]
    return sum(payouts)

# process_input(get_input(7, test=True))
# process_input(get_input(7))
# process_input(get_input(7, test=True), jokers_wild=True)
process_input(get_input(7), jokers_wild=True)
