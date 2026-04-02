# src

Source code for the pushing triangulation library.

## pushing.h

The core library. A single-header C implementation that generates (optionally random, optionally random & fine) pushing triangulations of point/vector configurations. If you want better determinant performance for moderate-dimensional configurations, run `hardcode_leibniz.py`, which writes a `det.h` file with hardcoded Laplace expansions. This gives significant speedups in some cases. If no `det.h` exists, the code defaults to cofactor expansion.

## demo.c

A minimal application that reads a vector configuration and uses `pushing.h` to construct pushing triangulations. For example configurations, see `../data/`. For a live interactive demo, see `../live_triplot.py`.

## ncube.c

Utility that prints the vertices of the $n$-dimensional unit cube $[0,1]^n$ as a vector configuration, for use as input to `rfp`.
