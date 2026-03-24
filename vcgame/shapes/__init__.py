"""Shape/vector-configuration generation."""
from .cube import cube_fan, cube_vc
from .random import random_fan, random_vc
from .reflexive import reflexive_fan, reflexive_vc
from .trunc_oct import trunc_oct_fan, trunc_oct_vc


def load_shape(
    name: str,
    *,
    seed: int = 1102,
    polytope_id: int = 0,
    n: int = 3,
):
    """Load a fan and vector configuration by name.

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
    tuple
        ``(fan, vc)`` pair.

    Raises
    ------
    ValueError
        If ``name`` is not a recognised shape.
    """
    if name == "cube":
        return cube_fan(n), cube_vc(n)
    if name == "random":
        return random_fan(seed=seed), random_vc(seed=seed)
    if name == "reflexive":
        return reflexive_fan(polytope_id=polytope_id), reflexive_vc(polytope_id=polytope_id)
    if name == "trunc_oct":
        return trunc_oct_fan(), trunc_oct_vc()
    raise ValueError(
        f"Unknown shape {name!r}. Choose from: cube, random, reflexive, trunc_oct"
    )
