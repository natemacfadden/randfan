"""
Generate integer vectors from the boundary lattice points of an
n x n x n integer cube.
"""

from __future__ import annotations


def cube_vectors(n: int) -> list[list[int]]:
    """Return the boundary lattice points of an n x n x n integer cube.

    The cube is centered at the origin. Boundary points are those with at
    least one coordinate equal to ±(n-1)/2. The origin (interior center)
    is excluded.

    Parameters
    ----------
    n : int
        Grid size. Must be odd and >= 3.

    Returns
    -------
    list[list[int]]
        A list of integer 3-vectors.
    """
    if n % 2 == 0 or n < 3:
        raise ValueError(f"n must be odd and >= 3, got {n}")
    half = (n - 1) // 2
    return [
        [x - half, y - half, z - half]
        for x in range(n)
        for y in range(n)
        for z in range(n)
        if x == 0 or x == n-1 or y == 0 or y == n-1 or z == 0 or z == n-1
    ]
