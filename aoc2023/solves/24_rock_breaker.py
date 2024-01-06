# day 24: hail asteroids
from functools import reduce
from itertools import combinations
from math import ceil, inf, log2, pow, sqrt
from typing import NamedTuple

from modules.array_math import addwise, mult
from modules.parse import get_input

def sq(x):
    return x*x

class Pos(NamedTuple):
    x: float
    y: float

    def __repr__(self):
        return f"({self.x:.4}, {self.y:.4})"

class Scale(NamedTuple):
    pos: int
    vel: int

Vector3 = tuple[float, float, float]
Vector6 = list[float] | tuple[float, float, float, float, float, float]

class Rock(NamedTuple):
    x: float
    y: float
    z: float
    dx: float
    dy: float
    dz: float

    def scaled_down(self, scale: Scale) -> "Rock":
        return Rock(
            self.x / scale.pos, self.y / scale.pos, self.z / scale.pos,
            self.dx / scale.vel, self.dy / scale.vel, self.dz / scale.vel,
        )

class Bounds(NamedTuple):
    min: int
    max: int

"""
    y = r.y + m * (x - r.x) , m = (r.dy/r.dx)
    y = (m * x) + r.y - (m * r.x)
    y = (r.m * x) + r.y - (r.m * r.x)
    when y is the same for r1 and r2,
    (r1.m * x) + r1.y - (r1.m * r1.x) = (r2.m * x) + r2.y - (r2.m * r2.x)
              (r1.m * x) - (r2.m * x) =  r2.y - r1.y - (r2.m * r2.x) + (r1.m * r1.x)
                    x * (r1.m - r2.m) =  r2.y - r1.y - (r2.m * r2.x) + (r1.m * r1.x)
                                    x = (r2.y - r1.y - (r2.m * r2.x) + (r1.m * r1.x)) / (r1.m - r2.m)
"""
def find_intersect(r1: Rock, r2: Rock) -> tuple[Pos | None, str | None]:
    if r1.dx == 0 or r2.dx == 0:
        return (None, "vertical line")
    (m1, m2) = (r1.dy/r1.dx, r2.dy/r2.dx)
    if m1 == m2:
        return (None, "same slope")
    x = (r2.y - r1.y - m2*r2.x + m1*r1.x) / (m1 - m2)
    # plug it back in to find the y
    y = r1.y +m1 * (x - r1.x)
    return (Pos(x, y), None)

"""
    x = r.x + (t * r.dx)
    (t * r.dx) = x - r.x
    t = (x - r.x) / r.dx
"""
def check_paths(r1: Rock, r2: Rock, b: Bounds) -> tuple[bool, Pos | None, str]:
    (pos, why) = find_intersect(r1, r2)
    if pos is None:
        return (False, pos, why)
    if not (b.min <= pos.x <= b.max and b.min <= pos.y <= b.max):
        return (False, pos, "out of bounds")
    t1 = (pos.x - r1.x) / r1.dx
    t2 = (pos.x - r2.x) / r2.dx
    if t1 < 0 or t2 < 0:
        return (False, pos, f"negative time: {t1:.2}, {t2:.2}")
    return (True, pos, f"positive time: {t1:.2}, {t2:.2}")


class Breaker(Rock):

    def get_adjusted(self, vector: Vector6) -> "Breaker":
        return Breaker(
            self.x + vector[0], self.y + vector[1], self.z + vector[2],
            self.dx + vector[3], self.dy + vector[4], self.dz + vector[5],
        )

    def scaled_up(self, scale: Scale) -> "Breaker":
        return Breaker(
            round(self.x * scale.pos),
            round(self.y * scale.pos),
            round(self.z * scale.pos),
            round(self.dx * scale.vel),
            round(self.dy * scale.vel),
            round(self.dz * scale.vel),
        )

    """
    expanding the distance formula:
    f(self, r, t)      = dist(x-r.x + t*(dx-r.dx), y-r.y + t*(dy-r.dy), z-r.z + t*(dz-r.dz))
                       = sqrt((x-r.x + t*(dx-r.dx))^2 + (y-r.y + t*(dy-r.dy))^2 + (z-r.z + t*(dz-r.dz))^2)
                       = sqrt((t^2*(dx-r.dx)^2 + 2t*(dx-r.dx)(x-r.x) + (x-r.x)^2) + ...)
    the minimum distance occurs when the derivative of the dist function w.r.t. time is zero
    d/dt f(self, r, t) = ((2t*(dx-r.dx)^2 + 2*(dx-r.dx)(x-r.x)) + 0 + ...)
                     0 = 2t*((dx-r.dx)^2 + (dy-r.dy)^2 + (dz-r.dz)^2) + 2*(dx-r.dx)(x-r.x) + 2*(dy-r.dy)(y-r.y) + 2*(dz-r.dz)(z-r.z)
    2t*((dx-r.dx)^2 + (dy-r.dy)^2 + (dz-r.dz)^2) = -2*((dx-r.dx)(x-r.x) + (dy-r.dy)(y-r.y) + (dz-r.dz)(z-r.z))
    t = -((dx-r.dx)(x-r.x) + (dy-r.dy)(y-r.y) + (dz-r.dz)(z-r.z)) / ((dx-r.dx)^2 + (dy-r.dy)^2 + (dz-r.dz)^2)
    """
    def closest_t(self, r: Rock) -> float:
        t = -((self.dx-r.dx)*(self.x-r.x) + (self.dy-r.dy)*(self.y-r.y) + (self.dz-r.dz)*(self.z-r.z)) / (sq(self.dx-r.dx) + sq(self.dy-r.dy) + sq(self.dz-r.dz))
        # if they were closest in the past, the closest non-negative time is t==0
        return max(t, 0)

    """
    use Euclidean distance to allow for gradient descent
    f(self, r, t) = dist(x-r.x + t*(dx-r.dx), y-r.y + t*(dy-r.dy), z-r.z + t*(dz-r.dz))
                  = sqrt((x-r.x + t*(dx-r.dx))^2 + (y-r.y + t*(dy-r.dy))^2 + (z-r.z + t*(dz-r.dz))^2)
    """
    def dist(self, r: Rock, t: float) -> float:
        res = (sq(self.x - r.x + t*(self.dx - r.dx)) + sq(self.y - r.y + t*(self.dy - r.dy)) + sq(self.z - r.z + t*(self.dz - r.dz)))
        return sqrt(res)

    """
    starting with expanded distance formula again:
    f(self, r, t)        = sqrt(t^2*(dx-r.dx)^2                   + 2t*(dx-r.dx)(x-r.x)                       + (x-r.x)^2)            + ...)    
                         = sqrt(t^2*(dx^2 - 2* dx* r.dx + r.dx^2) + 2t*(x* dx - dx* r.x - x* r.dx + r.x*r.dx) + x^2 - 2x* r.x + r.x^2 + ...)
    d/d(x) f(self, r, t) =     (0                                 + 2t*(dx    - 0       - r.dx    + 0)        + 2x  - 2 * r.x + 0     + 0)  / 2* f(self, r, t)
                         = (2t*(dx-r.dx) + 2x  -2r.x) / 2* f(self, r, t)
                         = (t*(dx-r.dx) + x - r.x) / f(self, r, t)
                         
    """
    def deriv_pos(self, r: Rock, t: float) -> Vector3:
        dist = self.dist(r, t)
        return (0, 0, 0) if dist == 0 else ((t*(self.dx-r.dx) + self.x - r.x) / dist, (t*(self.dy-r.dy) + self.y - r.y) / dist, (t*(self.dz-r.dz) + self.z - r.z) / dist)

    """
    starting with expanded distance formula again:
    f(self, r, t)         = sqrt(t^2*(dx^2 - 2* dx* r.dx + r.dx^2) + 2t*(x* dx - dx* r.x - x* r.dx + r.x*r.dx) + x^2 - 2x* r.x + r.x^2 + ...)
    d/d(dx) f(self, r, t) =     (t^2*(2dx  - 2*r.dx      + 0     ) + 2t*(x     - r.x     - 0       + 0       ) + 0                     + 0)  / 2* f(self, r, t)
                          =     (t^2*(2*dx - 2*r.dx) + 2t*(x - r.x)) / 2* f(self, r, t)
                          =     (t^2*(dx - r.dx) + t*(x - r.x)) / f(self, r, t)
    """
    def deriv_vel(self, r: Rock, t: float) -> Vector3:
        dist = self.dist(r, t)
        return (0, 0, 0) if dist == 0 else ((sq(t)*(self.dx - r.dx) + t*(self.x - r.x)) / dist, (sq(t)*(self.dy - r.dy) + t*(self.y - r.y)) / dist, (sq(t)*(self.dz - r.dz) + t*(self.z - r.z)) / dist)

    def get_derivs(self, r: Rock) -> Vector6:
        t = self.closest_t(r)
        return (*self.deriv_pos(r, t), *self.deriv_vel(r, t))

    def cost(self, r: Rock) -> float:
        t = self.closest_t(r)
        return self.dist(r, t)

    def total_cost(self, rocks: list[Rock]) -> float:
        return sum([self.cost(r) for r in rocks])

class BreakerFinder:
    def __init__(self, rocks: list[Rock]):
        self.orig_rocks = rocks
        (self.rocks, self.scale) = self.normalize_rocks(rocks)
        self.orig_vector = self.get_start_vector()
        self.breaker = Breaker(*self.orig_vector)

    def normalize_rocks(self, rocks: list[Rock]) -> tuple[list[Rock], Scale]:
        max_pos = max([val for vals in [r[:3] for r in rocks] for val in vals])
        max_vel = max([abs(val) for vals in [r[3:] for r in rocks] for val in vals])
        scale_pos: int = pow(2, ceil(log2(max_pos)))
        scale_vel: int = pow(2, ceil(log2(max_vel)))
        scale = Scale(scale_pos, scale_vel)
        scaled_rocks = [r.scaled_down(scale) for r in rocks]
        return (scaled_rocks, scale)

    def get_start_vector(self) -> Vector6:
        v_rocks = [[*rock] for rock in self.rocks]
        v_sum = reduce(lambda r1,r2:addwise(r1,r2), v_rocks)
        return tuple([n/len(self.rocks) for n in v_sum])

    def reset(self):
        self.breaker = Breaker(*self.orig_vector)
        return self
    
    def get_total_cost(self, breaker=None, rocks=None) -> float:
        breaker = breaker or self.breaker
        rocks = rocks or self.rocks
        return breaker.total_cost(rocks)
    
    # not actually used - sanity check to make sure the derivative formulas are correct
    def get_deltas(self, delta=0.001) -> Vector6:
        base_total = self.get_total_cost()
        res = []
        for idx in range(6):
            vector = [0] * 6
            vector[idx] += delta
            tester = self.breaker.get_adjusted(vector)
            test_total = self.get_total_cost(tester)
            res.append((test_total - base_total) / delta)
        return tuple(res)
    
    def get_derivs(self) -> list[Vector6]:
        return [self.breaker.get_derivs(rock) for rock in self.rocks]

    def run_cycles(self, cycles: int, scale: float):
        # print(f"initial cost: {self.get_total_cost()}, scale: {scale}, breaker: {self.breaker}")
        for x in range(cycles):
            sum_derivs = reduce(addwise, self.get_derivs())
            change = mult(sum_derivs, -scale)
            self.breaker = self.breaker.get_adjusted(change)
            # if x % 100 == 99 or cycles < 100:
            #     print(f"after {x+1}, cost: {self.get_total_cost()}, breaker: {self.breaker}")

        return self

    def solve(self) -> int:
        self.run_cycles(500, 0.000020)
        cost = self.get_total_cost()
        prev_cost = inf
        scale = 0.000001
        while cost < prev_cost:
            self.run_cycles(50, scale)
            (prev_cost, cost, scale) = (cost, self.get_total_cost(), scale / 10)
        self.breaker = self.breaker.scaled_up(self.scale)

        return self.breaker.x + self.breaker.y + self.breaker.z


def parse_line(line: str) -> Rock:
    (pos, vel) = line.split(" @ ")
    (pos, vel) = (pos.split(", "), vel.split(", "))
    return Rock(*[int(value) for value in [*pos, *vel]])

def parse_input(input: str) -> list[Rock]:
    return [parse_line(line) for line in input.splitlines()]

def count_intersects(input: str, bounds: Bounds) -> int:
    rocks = parse_input(input)
    results = [res[0] for res in [check_paths(r1, r2, bounds) for (r1, r2) in combinations(rocks, 2)]]
    return sum(results)

def find_breaker(input: str) -> int:
    rocks = parse_input(input)
    breaker = BreakerFinder(rocks)
    return breaker.solve()


# assert count_intersects(get_input(24, test=True), Bounds(7, 27)) == 2
# count_intersects(get_input(24), Bounds(200_000_000_000_000, 400_000_000_000_000))
# assert find_breaker(get_input(24, test=True)) == 47   # doesn't work with the test data - it finds a non-zero posal minima
find_breaker(get_input(24))
