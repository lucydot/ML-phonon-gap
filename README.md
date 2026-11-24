# ML_phonon_gap

## Setup

    conda env create -f environment.yml
    conda activate ml-phonon-gap

## Data

Copied from [SingingMaterialsSite](https://github.com/lucydot/SingingMaterialsSite) on 2026-11-24.

- `data/raw/`:
  - `metadata`: `mp_id`, `formula`, `bin_width` (Hz) and `phonon_method` (always `dfpt`). 
  - `projection`: `frequencies` (Hz) and `densities` for `total` and for each atomic site (e.g. `Ba_1`)
- `data/raw/phonon_materials.json`: the same 1,512 materials, cut down from the 26,609 in SingingMaterialsSite: ID, formula, space group, number of elements and sites, DFPT phonon calculation ID.
  - Added by `python3 scripts/find_gaps.py`, which explains them: `has_gap`, `has_ao_gap`, `has_formula_unit_gap`, `max_gap`, `max_gap_rel`, `gaps`, `n_modes`, `missing_modes`, `significant_imaginary`. 
- `data/raw/structures.json`: the structure used in each phonon calculation, `{mp_id: structure}`, as pymatgen dictionaries. Atoms are in the same order as in the DOS files.

Phonon data is from the [Materials Project](https://next-gen.materialsproject.org/), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
