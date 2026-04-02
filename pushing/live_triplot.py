# =============================================================================
#    Copyright (C) 2026  Nate MacFadden
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================

"""
Live-updating triplot: run rfp seed-by-seed and display each triangulation.

Usage::

    python live_triplot.py --data <file> [--n <int>] [--fct <path>]
                           [--random] [--fine]

Options
-------
--data <file>
    Input data file (required).
--n <int>
    Number of seeds to run (default: 100).
--fct <path>
    Path to rfp binary (default: ./rfp).
--random
    Pass ``--random`` to the binary.
--fine
    Pass ``--fine`` to the binary (implies ``--random``).
"""

import re
import subprocess
import sys

import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# Argument parsing
# =============================================================================

def parse_args():
    """Parse command-line arguments.

    Returns
    -------
    data_file : str
    n_seeds : int
    fct_bin : str
    do_random : bool
    do_fine : bool
    """
    data      = None
    n         = 100
    fct       = "./rfp"
    do_random = False
    do_fine   = False

    args = sys.argv[1:]
    while args:
        if args[0] == "--data" and len(args) > 1:
            data = args[1]; args = args[2:]
        elif args[0] == "--n" and len(args) > 1:
            n = int(args[1]); args = args[2:]
        elif args[0] == "--fct" and len(args) > 1:
            fct = args[1]; args = args[2:]
        elif args[0] == "--random":
            do_random = True; args = args[1:]
        elif args[0] == "--fine":
            do_fine = True; args = args[1:]
        else:
            sys.exit(f"Unknown argument: {args[0]}\n{__doc__.strip()}")

    if data is None:
        sys.exit(f"--data is required\n{__doc__.strip()}")
    if do_fine:
        do_random = True   # fine implies random

    return data, n, fct, do_random, do_fine

# =============================================================================
# Main
# =============================================================================

data_file, n_seeds, fct_bin, do_random, do_fine = parse_args()

with open(data_file) as f:
    raw = f.read().strip()

# Parse points from the data file; drop the homogenizing coordinate.
all_pts = []
for m in re.finditer(r'\[(-?\d+(?:,\s*-?\d+)*)\]', raw):
    coords = [int(x) for x in m.group(1).split(',')]
    all_pts.append(coords[1:])
pts = np.array(all_pts, dtype=float)

if pts.ndim != 2 or pts.shape[1] < 2:
    sys.exit(f"Expected 2D points, got shape {pts.shape}")

plt.ion()
fig, ax = plt.subplots()

for seed in range(n_seeds):
    cmd = [fct_bin, "--seed", str(seed)]
    if do_random: cmd.append("--random")
    if do_fine:   cmd.append("--fine")
    cmd.append(raw)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        sys.exit(f"Binary not found: {fct_bin}")
    except subprocess.TimeoutExpired:
        print(f"seed={seed}: timed out, skipping")
        continue

    if result.returncode != 0:
        print(f"seed={seed}: non-zero return code {result.returncode}, skipping")
        continue

    line = result.stdout.strip()
    if not line:
        continue

    simps = []
    for m in re.finditer(r'\[([^\]]+)\]', line):
        verts = [int(x) for x in m.group(1).split(',') if x.strip()]
        if len(verts) == 3:
            simps.append(verts)
    if not simps:
        continue
    simps = np.array(simps)

    mode = "rfp" if do_fine else ("rp" if do_random else "p")
    ax.cla()
    ax.set_aspect("auto")
    ax.set_title(f"{mode} seed={seed}")
    ax.triplot(pts[:, 0], pts[:, 1], simps, color="steelblue", linewidth=0.6)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    plt.pause(0.05)

plt.ioff()
plt.show()
