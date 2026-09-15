from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .models import ProkronError


def read_json(path: Path) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ProkronError(f"{path.name}: duplicate JSON key {key}")
            result[key] = value
        return result

    try:
        if path.is_symlink():
            raise ProkronError(f"{path}: symlink state files are not supported")
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (OSError, UnicodeError, ValueError) as error:
        raise ProkronError(f"{path.name}: {error}") from error


def write_json(path: Path, value: Any) -> None:
    if path.is_symlink() or path.parent.is_symlink():
        raise ProkronError(f"{path}: symlink state paths are not supported")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
            temporary = output.name
            output.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
