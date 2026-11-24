"""Find phonon band gaps from each material's total DOS and add them to data/raw/phonon_materials.json.

    python3 scripts/find_gaps.py      # run from anywhere; re-running overwrites the columns it adds

A gap is a run of bins where the total DOS is zero, with real modes on both sides. "Zero" means below
ZERO x the maximum DOS. The DOS is smeared (Gaussian, sigma about 0.09 THz), and we take it as it is: if
smearing closes a gap, there is no gap.

Imaginary modes were removed from the DOS files, so they play no part in finding gaps, but they are
counted: the DOS should integrate to 3 modes per atom, and what is missing is imaginary.

Columns added (frequencies in THz):
    has_gap                 there is at least one gap
    has_ao_gap              there is a gap with exactly 3 modes below it (acoustic-optical). Depends on the
                            cell: e.g. wurtzite GaN has 6 modes below its gap, so is False
    has_formula_unit_gap    there is a gap with exactly 3 modes per formula unit below it. Does not depend on
                            the cell: wurtzite GaN has 2 formula units, so is True. Formula units follow the
                            Materials Project formula, so peroxides keep their O2 pairs (Rb2O2, not RbO)
    max_gap                 width of the widest gap (0 if none)
    max_gap_rel             max_gap / the highest frequency
    gaps                    every gap: lower and upper edge, width, and modes_below (imaginary ones included)
    n_modes                 3 x number of atoms in the cell used for the DOS
    missing_modes           n_modes minus the integral of the DOS
    significant_imaginary   missing_modes is more than IMAGINARY x n_modes
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "data" / "raw" / "phonon_materials.json"
DOS = ROOT / "data" / "raw" / "dos"

ZERO = 1e-3  # DOS below this fraction of its maximum counts as zero
IMAGINARY = 0.01  # fraction of modes missing above which imaginary modes are significant
THZ = 1e12


def atoms_in(formula):
    """number of atoms in a formula, e.g. 5 for Ca(HO)2 (brackets are never nested)"""
    total = 0
    for group, group_n, n in re.findall(r"\(([^()]*)\)(\d*)|[A-Z][a-z]?(\d*)", formula):
        total += atoms_in(group) * int(group_n or 1) if group else int(n or 1)
    return total


def analyse(dos, formula):
    """the gap columns for one material, from its DOS file's contents and formula"""
    projection = dos["projection"]
    freqs = [f / THZ for f in projection["total"]["frequencies"]]
    dens = projection["total"]["densities"]  # modes per THz
    step = dos["metadata"]["bin_width"] / THZ
    n_atoms = len(projection) - 1  # every projection but "total" is one atom
    n_modes = 3 * n_atoms

    total = sum(dens) * step
    below = []  # modes below each bin, counted down from the top so missing (imaginary) modes are included
    running = n_modes - total
    for d in dens:
        running += d * step
        below.append(running)

    threshold = ZERO * max(dens)
    nonzero = [i for i, d in enumerate(dens) if d > threshold]
    gaps = []
    for lo, hi in zip(nonzero, nonzero[1:]):
        if hi - lo < 2:
            continue
        emptiest = min(range(lo, hi + 1), key=dens.__getitem__)
        modes = round(below[emptiest])
        if modes < 3:  # the acoustic modes lie below any gap: this is the DOS tailing off towards 0 THz
            continue
        gaps.append({"lower": round(freqs[lo], 4), "upper": round(freqs[hi], 4),
                     "width": round(freqs[hi] - freqs[lo], 4), "modes_below": modes})

    unit_modes = 3 * n_atoms / atoms_in(formula)  # 3 x formula units in the cell
    max_gap = max((g["width"] for g in gaps), default=0)
    missing = n_modes - total
    return {
        "has_gap": bool(gaps),
        "has_ao_gap": any(g["modes_below"] == 3 for g in gaps),
        "has_formula_unit_gap": any(g["modes_below"] == unit_modes for g in gaps),
        "max_gap": max_gap,
        "max_gap_rel": round(max_gap / freqs[nonzero[-1]], 4),
        "gaps": gaps,
        "n_modes": n_modes,
        "missing_modes": abs(round(missing, 4)),  # abs: no "-0.0"; the DOS never integrates to more than n_modes
        "significant_imaginary": missing > IMAGINARY * n_modes,
    }


def main():
    entries = json.loads(INDEX.read_text(encoding="utf-8"))
    for i, e in enumerate(entries):
        with open(DOS / f"{e['id']}_dos.json", encoding="utf-8") as f:
            new = analyse(json.load(f), e["formula"])
        entries[i] = {k: v for k, v in e.items() if k not in new} | new
    INDEX.write_text("[\n" + ",\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n]\n",
                     encoding="utf-8")
    for column in ("has_gap", "has_ao_gap", "has_formula_unit_gap", "significant_imaginary"):
        print(f"{column}: {sum(e[column] for e in entries)} of {len(entries)}")


if __name__ == "__main__":
    main()
