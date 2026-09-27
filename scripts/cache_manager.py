#!/usr/bin/env python3
"""Cache à identité forte pour la chaîne DATA-AUDIT-002.

Un cache n'est valide que si son fichier, son manifeste et l'identité attendue
concordent. Toute ambiguïté est une erreur (fail closed).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable


class CacheValidationError(RuntimeError):
    """Le cache ne prouve pas son identité ou son intégrité."""


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cache_identity(
    *, source_sha256: str, generator_files: list[Path], parameters: dict[str, Any],
    schema_version: str,
) -> dict[str, Any]:
    generators = {
        str(Path(path).resolve()): sha256_file(Path(path))
        for path in sorted(generator_files, key=lambda p: str(Path(p).resolve()))
    }
    body = {
        "source_sha256": source_sha256,
        "generator_sha256": generators,
        "parameters": parameters,
        "schema_version": schema_version,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    body["identity_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def validate_cache(cache_path: Path, manifest_path: Path,
                   expected_identity: dict[str, Any]) -> dict[str, Any]:
    cache_path, manifest_path = Path(cache_path), Path(manifest_path)
    if not cache_path.is_file():
        raise CacheValidationError(f"cache absent: {cache_path}")
    if not manifest_path.is_file():
        raise CacheValidationError(f"manifeste absent: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CacheValidationError(f"manifeste illisible: {exc}") from exc
    if manifest.get("identity") != expected_identity:
        raise CacheValidationError("identité du cache divergente")
    actual_hash = sha256_file(cache_path)
    if manifest.get("cache_sha256") != actual_hash:
        raise CacheValidationError("empreinte du cache divergente")
    return manifest


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def ensure_cache(
    cache_path: Path, manifest_path: Path, identity: dict[str, Any],
    builder: Callable[[Path], None],
) -> tuple[dict[str, Any], str]:
    """Valide le cache ou le régénère explicitement dans un fichier temporaire."""
    try:
        return validate_cache(cache_path, manifest_path, identity), "accepted"
    except CacheValidationError as reason:
        cache_path = Path(cache_path)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache_path.with_suffix(cache_path.suffix + ".tmp")
        if tmp.exists():
            tmp.unlink()
        builder(tmp)
        if not tmp.is_file():
            raise RuntimeError("le générateur n'a pas produit le cache attendu")
        os.replace(tmp, cache_path)
        manifest = {
            "cache_path": str(cache_path),
            "cache_sha256": sha256_file(cache_path),
            "identity": identity,
            "regeneration_reason": str(reason),
        }
        write_json_atomic(manifest_path, manifest)
        return manifest, "regenerated"
