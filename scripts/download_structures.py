"""Download the structure used in each material's DFPT phonon calculation from the Materials Project.

    python scripts/download_structures.py

Writes data/raw/structures.json: {mp_id: structure}, each a pymatgen Structure as a dictionary. Read one with
Structure.from_dict(...). Needs MP_API_KEY in a .env file here or in ../SingingMaterialsSite.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from mp_api.client import MPRester

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "data" / "raw" / "phonon_materials.json"
OUT = ROOT / "data" / "raw" / "structures.json"
BATCH = 100


def main():
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT.parent / "SingingMaterialsSite" / ".env")
    mp_ids = {e["phonon_ids"]["dfpt"]: e["id"] for e in json.loads(INDEX.read_text(encoding="utf-8"))}
    phonon_ids = list(mp_ids)

    structures = {}
    with MPRester(os.environ["MP_API_KEY"], mute_progress_bars=True) as mpr:
        for start in range(0, len(phonon_ids), BATCH):
            docs = mpr.materials.phonon.search(
                identifiers=phonon_ids[start:start + BATCH], phonon_method="dfpt",
                all_fields=False, fields=["identifier", "structure"])
            for d in docs:
                if d.structure:
                    structures[mp_ids[str(d.identifier)]] = d.structure.as_dict()
            print(f"{min(start + BATCH, len(phonon_ids))}/{len(phonon_ids)}")

    missing = set(mp_ids.values()) - set(structures)
    print(f"{len(structures)} structures, {len(missing)} missing {sorted(missing)}")
    ordered = {m: structures[m] for m in mp_ids.values() if m in structures}  # same order as the index
    OUT.write_text("{\n" + ",\n".join(f'"{m}": {json.dumps(s)}' for m, s in ordered.items()) + "\n}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
