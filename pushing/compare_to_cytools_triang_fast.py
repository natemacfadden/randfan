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
Compare rfp with CYTools ``random_triangulations_fast`` on [0,c]^2.

Produces
--------
docs/compare_timing.png
    Time vs c for both methods (``N_TRIANGS`` triangulations each).
docs/compare_grid.png
    Grid of ``N_SHOW`` sample triangulations per method per c value.
"""

import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time

import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# Configuration
# =============================================================================

C_TIMING  = list(range(1, 51, 2))   # c values for timing plot
C_GRID    = [2, 5, 7, 10, 13]       # c values for triangulation grid
N_TRIANGS = 100                     # triangulations requested per (c, method)
N_SHOW    = 5                       # triangulations shown in grid plot
TIMEOUT   = 10.0                    # per-(c, method) timeout in seconds;
                                    # stops that method for all larger c

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RFP_BIN     = os.path.join(_SCRIPT_DIR, "rfp")
DOCS_DIR    = os.path.join(_SCRIPT_DIR, "docs")

if not os.path.isfile(RFP_BIN):
    sys.exit(
        f"rfp binary not found at {RFP_BIN}.\n"
        f"Compile with: clang -o {RFP_BIN} {_SCRIPT_DIR}/src/demo.c"
    )

# =============================================================================
# Helpers
# =============================================================================

def lattice_square(c):
    """Return all integer lattice points in [0, c]^2.

    Parameters
    ----------
    c : int
        Side length.

    Returns
    -------
    list of [int, int]
    """
    return [[x, y] for x in range(c + 1) for y in range(c + 1)]


def homogenize(pts):
    """Prepend a homogenizing coordinate 1 to each point.

    Parameters
    ----------
    pts : list of list of int

    Returns
    -------
    list of list of int
    """
    return [[1] + p for p in pts]


def canonicalize(simps):
    """Return a hashable canonical form of a triangulation.

    Parameters
    ----------
    simps : array-like of shape (n, 3)

    Returns
    -------
    frozenset of tuple of int
    """
    return frozenset(tuple(sorted(s)) for s in simps)


def deduplicate(triangulations):
    """Remove duplicate triangulations, preserving order.

    Parameters
    ----------
    triangulations : list of ndarray

    Returns
    -------
    list of ndarray
    """
    seen   = set()
    result = []
    for simps in triangulations:
        key = canonicalize(simps)
        if key not in seen:
            seen.add(key)
            result.append(simps)
    return result

# =============================================================================
# Runners
# =============================================================================

def run_rfp(hpts, n=N_TRIANGS):
    """Run rfp and return deduplicated triangulations.

    Parameters
    ----------
    hpts : list of list of int
        Homogenized point configuration.
    n : int
        Number of triangulations to request.

    Returns
    -------
    triangulations : list of ndarray or None
        ``None`` on timeout.
    elapsed : float
        Wall time in seconds (``TIMEOUT`` on timeout).
    """
    raw = json.dumps(hpts)
    cmd = [RFP_BIN, "-r", "-f", "-n", str(n), raw]
    t0  = time.perf_counter()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, TIMEOUT
    elapsed = time.perf_counter() - t0

    triangulations = []
    for line in result.stdout.strip().splitlines():
        simps = []
        for m in re.finditer(r'\[([^\]]+)\]', line):
            verts = [int(x) for x in m.group(1).split(',') if x.strip()]
            if len(verts) == 3:
                simps.append(verts)
        if simps:
            triangulations.append(np.array(simps))
    return deduplicate(triangulations), elapsed


def _cytools_worker(hpts, n):
    """Worker function for ``run_cytools``; must be top-level for pickling.

    Parameters
    ----------
    hpts : list of list of int
        Homogenized point configuration.
    n : int
        Number of triangulations to request.

    Returns
    -------
    result : list of (list, list)
        Each entry is ``(pts, simps)`` as plain Python lists.
    elapsed : float
    """
    from cytools import Polytope
    p       = Polytope(hpts)
    t0      = time.perf_counter()
    triangs = list(p.random_triangulations_fast(N=n))
    elapsed = time.perf_counter() - t0

    seen   = set()
    result = []
    for t in triangs:
        simps = np.array(t.simplices())
        key   = canonicalize(simps)
        if key not in seen:
            seen.add(key)
            pts = np.array(t.points())[:, 1:]   # drop homogenizing coordinate
            result.append((pts.tolist(), simps.tolist()))
    return result, elapsed


def run_cytools(hpts, n=N_TRIANGS):
    """Run CYTools ``random_triangulations_fast`` with a timeout.

    Parameters
    ----------
    hpts : list of list of int
        Homogenized point configuration.
    n : int
        Number of triangulations to request.

    Returns
    -------
    triangulations : list of (ndarray, ndarray) or None
        Each entry is ``(pts_2d, simps)``. ``None`` on timeout.
    elapsed : float
        Wall time in seconds (``TIMEOUT`` on timeout).
    """
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_cytools_worker, hpts, n)
        try:
            raw_result, elapsed = future.result(timeout=TIMEOUT)
        except concurrent.futures.TimeoutError:
            return None, TIMEOUT
    result = [(np.array(pts), np.array(simps)) for pts, simps in raw_result]
    return result, elapsed

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    rfp_times   = {}   # c -> elapsed seconds
    cyt_times   = {}   # c -> elapsed seconds
    rfp_counts  = {}   # c -> number of unique triangulations found
    cyt_counts  = {}   # c -> number of unique triangulations found
    rfp_samples = {}   # c -> list of simplex arrays (N_SHOW entries)
    cyt_samples = {}   # c -> list of (pts_2d, simps) pairs (N_SHOW entries)

    rfp_done = False
    cyt_done = False

    for c in sorted(set(C_TIMING) | set(C_GRID)):
        if rfp_done and cyt_done:
            break

        pts_2d = lattice_square(c)
        hpts   = homogenize(pts_2d)
        print(f"c={c}  ({len(pts_2d)} points)")

        if not rfp_done:
            triangs, elapsed = run_rfp(hpts)
            if triangs is None:
                print(f"  rfp:     timed out (>{TIMEOUT:.0f}s)")
                rfp_done = True
            else:
                rfp_times[c]   = elapsed
                rfp_counts[c]  = len(triangs)
                rfp_samples[c] = triangs[:N_SHOW]
                print(f"  rfp:     {elapsed:.3f}s  ({len(triangs)} triangulations)")

        if not cyt_done:
            triangs, elapsed = run_cytools(hpts)
            if triangs is None:
                print(f"  cytools: timed out (>{TIMEOUT:.0f}s)")
                cyt_done = True
            else:
                cyt_times[c]   = elapsed
                cyt_counts[c]  = len(triangs)
                cyt_samples[c] = triangs[:N_SHOW]
                print(f"  cytools: {elapsed:.3f}s  ({len(triangs)} triangulations)")

    # -------------------------------------------------------------------------
    # Plot 1: timing
    # -------------------------------------------------------------------------

    rfp_c = [c for c in C_TIMING if c in rfp_times]
    cyt_c = [c for c in C_TIMING if c in cyt_times]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(rfp_c, [rfp_times[c] for c in rfp_c], "o-", color="steelblue", label="rfp  (-r -f)")
    ax.plot(cyt_c, [cyt_times[c] for c in cyt_c], "s-", color="tomato",    label="random_triangulations_fast")

    for c in rfp_c:
        if rfp_counts.get(c, N_TRIANGS) < N_TRIANGS:
            ax.annotate(f"{rfp_counts[c]}", (c, rfp_times[c]),
                        textcoords="offset points", xytext=(4, -7),
                        fontsize=7, color="steelblue")
    for c in cyt_c:
        if cyt_counts.get(c, N_TRIANGS) < N_TRIANGS:
            ax.annotate(f"{cyt_counts[c]}", (c, cyt_times[c]),
                        textcoords="offset points", xytext=(4, 4),
                        fontsize=7, color="tomato")

    all_c_plotted = sorted(set(rfp_c) | set(cyt_c))
    ax.set_xticks(all_c_plotted)
    ax.set_xticklabels(all_c_plotted, fontsize=7)
    ax.set_xlabel("c   ([0,c]^2 lattice points)")
    ax.set_ylabel(f"Time (s) for {N_TRIANGS} triangulations")
    ax.set_title(
        "rfp vs CYTools random_triangulations_fast\n"
        r"(unique count printed if $<$" + f"{N_TRIANGS} distinct triangulations found)",
        fontsize=10
    )
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "compare_timing.png"), dpi=150)
    print("Saved compare_timing.png")

    # -------------------------------------------------------------------------
    # Plot 2: triangulation grid
    # Two subfigures stacked: rfp on top, CYTools on bottom.
    # Columns: one per c in C_GRID.  Rows: N_SHOW triangulations each.
    # -------------------------------------------------------------------------

    n_cols = len(C_GRID)
    fig    = plt.figure(figsize=(2.2 * n_cols, 2.2 * N_SHOW * 2))
    subfigs = fig.subfigures(2, 1, hspace=0.04)

    for subfig, label, color, samples, use_hpts in [
        (subfigs[0], "rfp",                               "steelblue", rfp_samples, True),
        (subfigs[1], "CYTools random_triangulations_fast", "tomato",   cyt_samples, False),
    ]:
        subfig.suptitle(label, fontsize=11, fontweight="bold", color=color, y=0.98)
        axes = subfig.subplots(N_SHOW, n_cols)
        subfig.subplots_adjust(top=0.93, bottom=0.02, left=0.02, right=0.98,
                               hspace=0.1, wspace=0.1)

        for col, c in enumerate(C_GRID):
            pts_2d = np.array(lattice_square(c), dtype=float)
            for row in range(N_SHOW):
                ax = axes[row][col]
                ax.set_aspect("equal")
                ax.set_xticks([]); ax.set_yticks([])
                if row == 0:
                    ax.set_title(f"c={c}", fontsize=9, pad=4)
                if c in samples and row < len(samples[c]):
                    if use_hpts:
                        simps = samples[c][row]
                        ax.triplot(pts_2d[:, 0], pts_2d[:, 1], simps,
                                   color=color, lw=0.7)
                    else:
                        pts_cyt, simps = samples[c][row]
                        ax.triplot(pts_cyt[:, 0], pts_cyt[:, 1], simps,
                                   color=color, lw=0.7)

    plt.savefig(os.path.join(DOCS_DIR, "compare_grid.png"), dpi=150)
    print("Saved compare_grid.png")
