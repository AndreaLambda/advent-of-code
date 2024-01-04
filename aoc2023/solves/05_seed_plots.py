# day 5: seed plots
from typing import NamedTuple
from modules.parse import get_input
from modules.utils import batched

class Mapping(NamedTuple):
    dst: int
    src: int
    length: int

class Almanac(NamedTuple):
    seeds: list[int]
    mappings: list[list[Mapping]]

class Range(NamedTuple):
    start: int
    end: int

# 5-1
def map_single_plot(plot: int, mappings: list[Mapping]) -> int:
    for (dst, src, length) in mappings:
        if (src <= plot < src+length):
            return plot+dst-src
    return plot

def apply_mapping(plots: list, mappings: list[Mapping], plotter: callable):
    res = [plotter(plot, mappings) for plot in plots]
    if type(res[0]) == int:
        return res
    return [plot for subplot in res for plot in subplot]

def map_seeds(seeds: list, all_mappings: list[list[Mapping]], plotter: callable):
    mapped = seeds
    for mappings in all_mappings:
        mapped = apply_mapping(mapped, mappings, plotter)
    return min(mapped)

# 5-2
def expand_seeds(seed_map) -> list[Range]:
    return [Range(start, start+num-1) for (start, num) in batched(seed_map, 2)]

def map_plot_range(plot_range: Range, mappings: list[Mapping]) -> list[Range]:
    unmapped = [plot_range]
    mapped: list[Range] = []

    for (dst, src_start, length) in mappings:
        src_end = src_start + length - 1
        for plot in unmapped:
            if (plot.start <= src_end) and (src_start <= plot.end):
                unmapped.remove(plot)
                overlap_start = max(plot.start, src_start)
                overlap_end = min(plot.end, src_end)
                shift = dst - src_start
                mapped.append(Range(overlap_start + shift, overlap_end + shift))
                if overlap_start > plot.start:
                    unmapped.append(Range(plot.start, overlap_start - 1))
                if overlap_end < plot[1]:
                    unmapped.append(Range(overlap_end + 1, plot.end))
    return unmapped + mapped


def parse_input(input: str) -> Almanac:
    parts = input.split("\n\n")

    (seeds, mappings) = (parts[0], [map.splitlines()[1:] for map in parts[1:]])
    seeds = [int(seed) for seed in seeds.split(' ')[1:]]
    mappings = [[Mapping(*[int(num) for num in line.split(" ")]) for line in mapping] for mapping in mappings]
    return Almanac(seeds, mappings)

def process_input(input: str, expanded=False):
    almanac = parse_input(input)
    (plotter, seeder) = (map_plot_range, expand_seeds) if expanded else (map_single_plot, None)
    seeds = almanac.seeds
    if seeder:
        seeds = seeder(seeds)
    mapped = map_seeds(seeds, almanac.mappings, plotter)
    return mapped if type(mapped) == int else min(mapped)

# process_input(get_input(5, test=True))
# process_input(get_input(5))
# process_input(get_input(5, test=True), expanded=True)
process_input(get_input(5), expanded=True)
