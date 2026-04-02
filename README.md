# ntt

A collection of triangulation toys for studying lattice point/vector configurations.

## pushing

A C library for constructing **pushing triangulations** of point/vector configurations,
with optional randomization and fineness.

A *pushing triangulation* assigns an order to the points/vectors, constructing a
simplex from the first points/vectors and then incrementally adding new ones by
connecting new points/vectors to the externally-visible facets. This also has
interpretation of assigning exponentially-spaced heights $h_i = c^i$ to the vectors, for
sufficiently large $c$. This latter interpretation shows that such triangulations are
regular.

A greedy randomized variant thus gives a cheap source of semi-random fine regular
triangulations — useful as an alternative to full flip-graph traversal. See
[pushing/README.md](pushing/README.md) for details and algorithm notes.

```bash
clang -o rfp pushing/src/demo.c
./data/ncube 5 | ./rfp -n 1000
```

or, more interactively

```
python pushing/live_triplot.py --n 1000
```

## vcgame

An interactive game built around **triangulations of 3D lattice vector configurations**.

The player navigates a simplicial fan by moving along geodesics on the 2-sphere. Crossing
a wall between cones performs a **bistellar flip**, modifying the triangulation in real
time. The fan can be locked for free exploration.

```bash
cd vcgame
python main.py --shape cube --n 5
python main.py --shape trunc_oct
python main.py --shape reflexive --polytope_id 7
```

Built on [regfans](https://github.com/natemacfadden/regfans). Much of this project was
developed with the assistance of [Claude Code](https://claude.ai/claude-code) (Anthropic).

## grow2d *(coming soon)*

Random triangulations of lattice polygons.
