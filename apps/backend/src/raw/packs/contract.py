"""The pack contract — what a pack MUST provide to plug into the base.

A pack is a folder with a pack.json manifest + known subfolders. The base is moat-agnostic:
the pack supplies tools + skills + prompt + rules + theme + VALIDATOR (the moat). See
docs/BASE-VS-PACK.md for the full contract.
"""

from pathlib import Path

from pydantic import BaseModel


class PackManifest(BaseModel):
    """Parsed pack.json. Only `name` is strictly required."""

    name: str
    version: str = "0.1.0"
    description: str = ""
    # relative paths inside the pack (all optional)
    tools: str | None = "tools"
    skills: str | None = "skills"
    prompt: str | None = "prompt.md"
    rules: str | None = "rules.md"
    theme: str | None = "theme/tokens.json"
    validator: str | None = "validator.py"  # the moat


class LoadedPack(BaseModel):
    """A discovered pack, resolved to absolute paths."""

    manifest: PackManifest
    root: Path  # ${PACK_ROOT} — immutable installed files

    @property
    def namespace(self) -> str:
        return self.manifest.name
