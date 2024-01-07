# day 25: network plugs
from modules.parse import get_input
from modules.types import DefaultKeydict
from modules.utils import flatten


class Node:
    def __init__(self, id: str):
        self.id = id
        self.nodes: list[Node] = []

    def add(self, other: "Node"):
        self.nodes.append(other)
        other.nodes.append(self)

    def remove(self, other: "Node"):
        self.nodes.remove(other)
        other.nodes.remove(self)

    def get_distmap(self) ->  list[list["Node"]]:
        dist = 0
        check = []
        next = [self]
        seen = set([self])
        dists = []
        while next:
            dists.append(next.copy())
            dist += 1
            (check, next) = (next, [])
            for node in check:
                for n in node.nodes:
                    if n not in seen:
                        next.append(n)
                        seen.add(n)
        return dists
    
    def __repr__(self):
        return self.id
    
    def __str__(self):
        return self.id

class Network:
    def __init__(self, lines: list[tuple[str, list[str]]]):
        self.nodes: dict[str, Node] = self.build_nodes(lines)

    def build_nodes(self, lines: list[tuple[str, list[str]]]):
        nodes: dict[str, Node] = DefaultKeydict(lambda id: Node(id))
        for (src, dsts) in lines:
            srcnode = nodes[src]
            for dst in dsts:
                srcnode.add(nodes[dst])
        return dict(nodes)

    def find_ideal_distmap(self) -> list[list[Node]]:
        best = None
        best_distmap = None
        for node in self.nodes.values():
            distmap = node.get_distmap()
            dists = [len(nodes) for nodes in distmap[1:-1]]
            if len(dists) > 0 and (best is None or min(dists) < best):
                best = min(dists)
                best_distmap = distmap
        return best_distmap

    def print_distmap(self, distmap: list[list[Node]]):
        for (idx, nodes) in enumerate(distmap):
            print(f"{idx:2} ({len(nodes):3}): {', '.join(sorted([n.id for n in nodes]))}")

    def get_cluster_values(self):
        distmap = self.find_ideal_distmap()
        inner_dist_size = [len(nodes) for nodes in distmap[1:-1]]
        bridge_size = min(inner_dist_size)
        bridge_idx = inner_dist_size.index(bridge_size) + 1

        left = set(flatten(distmap[0:bridge_idx]))
        right = set(flatten(distmap[bridge_idx+1:]))
        bridge = set(distmap[bridge_idx])

        for node in bridge:
            n_left = [n for n in node.nodes if n in left]
            n_right = [n for n in node.nodes if n in right]
            snip = n_left[0] if len(n_left) < len(n_right) else n_right[0]
            node.remove(snip)

        left_cluster = distmap[1][0].get_distmap()
        right_cluster = distmap[-1][0].get_distmap()
        left_size = sum([len(nodes) for nodes in left_cluster])
        right_size = sum([len(nodes) for nodes in right_cluster])

        return left_size * right_size

def parse_line(line: list[str]) -> tuple[str, list[str]]:
    (src, dsts) = line.split(r": ")
    return (src, dsts.split(" "))

def parse_input(input: str):
    parsed = [parse_line(line) for line in input.splitlines()]
    return Network(parsed).get_cluster_values()

# assert parse_input(get_input(25, test=True)) == 54
parse_input(get_input(25))
