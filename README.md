# ML_phonon_gap

## Setup

    conda env create -f environment.yml
    conda activate ml-phonon-gap

## Data

Copied from [SingingMaterialsSite](https://github.com/lucydot/SingingMaterialsSite) on 2026-11-24.

- `data/raw/dos/`: DFPT phonon density of states for 1,512 materials, one `<mp_id>_dos.json` each. Not in git (350 MB).
  - `metadata`: `mp_id`, `formula`, `bin_width` (Hz) and `phonon_method` (always `dfpt`). Added here: `phonon_method` in 42 files (they came from SingingMaterials, which only fetches DFPT), and `formula` in `mp-22862` (NaCl)
  - `projection`: `frequencies` (Hz) and `densities` for `total` and for each atomic site (e.g. `Ba_1`)
- `data/raw/phonon_materials.json`: the same 1,512 materials, cut down from the 26,609 in SingingMaterialsSite: ID, formula, space group, number of elements and sites, DFPT phonon calculation ID (`phonon_ids`; other methods' IDs removed).
  - Added by `python3 scripts/find_gaps.py`, which explains them: `has_gap`, `has_ao_gap`, `has_formula_unit_gap`, `max_gap`, `max_gap_rel`, `gaps`, `n_modes`, `missing_modes`, `significant_imaginary`. Frequencies in THz.
- `data/raw/structures.json`: the structure used in each phonon calculation, `{mp_id: structure}`, as pymatgen dictionaries. Atoms are in the same order as in the DOS files. For 11 materials the cell is smaller than `nsites` in the index. Downloaded by `python scripts/download_structures.py` (needs `MP_API_KEY`).

To recreate `data/raw/dos/` on the same machine, from this folder (the second line removes the 37 `pheasy` files, the last two add the missing `phonon_method` and `formula`):

    mkdir -p data/raw/dos && cp ../SingingMaterialsSite/cache/*_dos.json data/raw/dos/
    grep -lE '"phonon_method": *"pheasy"' data/raw/dos/*_dos.json | xargs rm
    grep -L '"phonon_method"' data/raw/dos/*_dos.json | xargs perl -pi -e 's/("bin_width": [^,}]+)\}/$1, "phonon_method": "dfpt"}/'
    perl -pi -e 's/"mp_id": "mp-22862", "bin_width"/"mp_id": "mp-22862", "formula": "NaCl", "bin_width"/' data/raw/dos/mp-22862_dos.json

Phonon data is from the [Materials Project](https://next-gen.materialsproject.org/), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
