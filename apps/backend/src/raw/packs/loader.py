"""The pack loader — discovers a pack, reads its manifest, registers its components.

TODO (Sprint 2): register tools (MCP), skills, prompt, rules, theme, validator into the base's
slots, namespaced by pack name. For now it just loads + validates the manifest (the seam exists).
"""

import json
from pathlib import Path

from raw.packs.contract import LoadedPack, PackManifest


def load_pack(pack_path: str) -> LoadedPack:
    """Load and validate a pack from a directory containing pack.json."""
    root = Path(pack_path).resolve()
    manifest_file = root / "pack.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"No pack.json found at {manifest_file}")
    data = json.loads(manifest_file.read_text())
    manifest = PackManifest(**data)
    return LoadedPack(manifest=manifest, root=root)
