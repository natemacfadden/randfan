"""CLI for shape/vector generation.

Usage
-----
    python -m shapes cube
    python -m shapes cube --n 5
    python -m shapes random --seed 42
    python -m shapes reflexive --polytope_id 7
    python -m shapes trunc_oct
"""
from __future__ import annotations

import argparse
import json

from . import _SHAPES, get_vectors


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m shapes",
        description="Print integer vectors for a named shape as JSON.",
    )
    p.add_argument(
        "shape",
        choices=_SHAPES,
        help="Shape to generate.",
    )
    p.add_argument(
        "--n",
        type=int,
        default=3,
        metavar="N",
        help="Cube grid size (odd, >= 3). Only used for 'cube'. Default: 3.",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=1102,
        metavar="N",
        help="RNG seed. Only used for 'random'. Default: 1102.",
    )
    p.add_argument(
        "--polytope_id",
        type=int,
        default=0,
        metavar="ID",
        help="Reflexive polytope index 0–4318. Only used for 'reflexive'.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    vectors = get_vectors(
        args.shape,
        n=args.n,
        seed=args.seed,
        polytope_id=args.polytope_id,
    )
    print(json.dumps(vectors))


if __name__ == "__main__":
    main()
