"""Shape/vector-configuration generation."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from regfans import VectorConfiguration

from .cube import cube_vectors
from .random import random_vectors
from .reflexive import reflexive_vectors
from .trunc_oct import trunc_oct_vectors

if TYPE_CHECKING:
    from regfans import Fan


_REGISTRY: dict[str, object] = {
    "cube":      lambda **kw: cube_vectors(kw["n"]),
    "random":    lambda **kw: random_vectors(seed=kw["seed"]),
    "reflexive": lambda **kw: reflexive_vectors(polytope_id=kw["polytope_id"]),
    "trunc_oct": lambda **kw: trunc_oct_vectors(),
}
_SHAPES = tuple(_REGISTRY)


def get_vectors(
    name: str,
    *,
    seed: int = 1102,
    polytope_id: int = 0,
    n: int = 3,
) -> list[list[int]]:
    """Return integer vectors for the named shape.

    Parameters
    ----------
    name : str
        One of ``"cube"``, ``"random"``, ``"reflexive"``, ``"trunc_oct"``.
    seed : int, optional
        RNG seed for ``"random"`` shapes.
    polytope_id : int, optional
        Polytope index for ``"reflexive"`` shapes (0–4318).
    n : int, optional
        Cube size for ``"cube"`` shapes.

    Returns
    -------
    list[list[int]]
        Integer 3-vectors on the polytope boundary.

    Raises
    ------
    ValueError
        If ``name`` is not a recognised shape.
    """
    if name not in _REGISTRY:
        raise ValueError(
            f"Unknown shape {name!r}. Choose from: {', '.join(_SHAPES)}"
        )
    return _REGISTRY[name](n=n, seed=seed, polytope_id=polytope_id)


def vectors_to_fan(vectors: list[list[int]]) -> Fan:
    """Triangulate a list of integer vectors into a fan.

    Parameters
    ----------
    vectors : list[list[int]]
        Integer 3-vectors.

    Returns
    -------
    Fan
        A triangulated fan of the vectors.
    """
    return VectorConfiguration(vectors).triangulate()


def load_shape(
    name: str,
    *,
    seed: int = 1102,
    polytope_id: int = 0,
    n: int = 3,
) -> Fan:
    """Generate vectors and triangulate into a fan in one step.

    Parameters
    ----------
    name : str
        One of ``"cube"``, ``"random"``, ``"reflexive"``, ``"trunc_oct"``.
    seed : int, optional
        RNG seed for ``"random"`` shapes.
    polytope_id : int, optional
        Polytope index for ``"reflexive"`` shapes (0–4318).
    n : int, optional
        Cube size for ``"cube"`` shapes.

    Returns
    -------
    Fan
        A triangulated fan.
    """
    return vectors_to_fan(
        get_vectors(name, seed=seed, polytope_id=polytope_id, n=n)
    )
