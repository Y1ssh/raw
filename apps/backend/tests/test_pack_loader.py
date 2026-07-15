"""The pack loader is the seam — prove a pack's manifest loads."""

from pathlib import Path

from raw.packs.loader import load_pack


def test_loads_example_pack() -> None:
    # example-pack lives at the repo root
    repo_root = Path(__file__).resolve().parents[3]
    pack = load_pack(str(repo_root / "example-pack"))
    assert pack.manifest.name == "example"
