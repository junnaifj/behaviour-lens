"""Filesystem persistence for Behaviour Lens' Obsidian-compatible notes."""
from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

VALID_STATUS = {"supported", "partly-supported", "uncertain", "potentially-misleading"}
VALID_REVIEW = {"weekly", "monthly", "quarterly"}


def vault_root() -> Path:
    configured = os.environ.get("BEHAVIOUR_LENS_VAULT", "").strip()
    if not configured or configured == "${OBSIDIAN_VAULT_PATH}":
        return Path.home() / "Documents" / "Obsidian" / "Behaviour Lens Vault"
    return Path(configured).expanduser()


def _dirs(root: Path | None = None) -> tuple[Path, Path]:
    base = (root or vault_root()).resolve() / "Behaviour Lens"
    observations, reviews = base / "Observations", base / "Pattern Reviews"
    observations.mkdir(parents=True, exist_ok=True)
    reviews.mkdir(parents=True, exist_ok=True)
    return observations, reviews


def _date(value: str, field: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD)") from exc


def _slug(value: str) -> str:
    plain = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    clean = re.sub(r"[^a-z0-9]+", "-", plain).strip("-")[:60]
    return clean or "observation"


def _frontmatter(meta: dict[str, Any]) -> str:
    # JSON scalars and arrays are valid YAML and make lossless parsing dependency-free.
    return "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in meta.items()) + "\n---\n"


def _parse(path: Path, include_content: bool = True) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"Invalid Behaviour Lens note: {path}")
    header, body = text[4:].split("\n---\n", 1)
    meta: dict[str, Any] = {}
    for line in header.splitlines():
        key, sep, raw = line.partition(": ")
        if sep:
            meta[key] = json.loads(raw)
    meta["path"] = str(path)
    if include_content:
        meta["content"] = body.rstrip()
    return meta


def _write_once(directory: Path, filename: str, content: str) -> Path:
    target = directory / filename
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing note: {target}")
    fd, temp_name = tempfile.mkstemp(prefix=".behaviour-lens-", dir=directory, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return target


def save_observation(data: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    for field in ("observation", "brief", "date", "evidence_status"):
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")
    day = _date(data["date"], "date")
    if data["evidence_status"] not in VALID_STATUS:
        raise ValueError("Invalid evidence_status")
    note_id = str(data.get("id") or uuid.uuid4())
    slug = _slug(data.get("slug") or data["observation"][:80])
    metadata = {
        "type": "behaviour-observation", "id": note_id, "date": day,
        "observed_at": data.get("observed_at"), "created_at": datetime.now().astimezone().isoformat(),
        "evidence_status": data["evidence_status"], "domain": data.get("domain", []),
        "setting": data.get("setting", []), "behavioural_theme": data.get("behavioural_theme", []),
        "analytical_scale": data.get("analytical_scale", []), "framing": data.get("framing", []),
        "ai_relevance": data.get("ai_relevance", "none"), "keywords": data.get("keywords", []),
        "pattern_ids": data.get("pattern_ids", []), "sources": data.get("sources", []),
    }
    body = _frontmatter(metadata) + f"\n# Observation — {day}\n\n## Raw observation\n\n{data['observation'].strip()}\n\n{data['brief'].strip()}\n"
    observations, _ = _dirs(root)
    path = _write_once(observations, f"{day}-{slug}--{note_id[:8]}.md", body)
    return {"id": note_id, "path": str(path), "metadata": metadata}


def get_observations_by_period(start_date: str, end_date: str, root: Path | None = None, include_content: bool = True) -> dict[str, Any]:
    start, end = _date(start_date, "start_date"), _date(end_date, "end_date")
    if start > end:
        raise ValueError("start_date must be on or before end_date")
    observations, _ = _dirs(root)
    records = []
    for path in sorted(observations.glob("*.md")):
        record = _parse(path, include_content)
        if start <= str(record.get("date", "")) <= end:
            records.append(record)
    return {"period_start": start, "period_end": end, "count": len(records), "observations": records}


def search_observations(query: str = "", filters: dict[str, Any] | None = None, limit: int = 50, root: Path | None = None) -> dict[str, Any]:
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    filters = filters or {}
    observations, _ = _dirs(root)
    terms = query.casefold().split()
    results = []
    for path in sorted(observations.glob("*.md"), reverse=True):
        record = _parse(path, True)
        haystack = (json.dumps(record, ensure_ascii=False) + " " + record.get("content", "")).casefold()
        if terms and not all(term in haystack for term in terms):
            continue
        if any(value not in record.get(key, []) if isinstance(record.get(key), list) else record.get(key) != value for key, value in filters.items()):
            continue
        results.append(record)
        if len(results) == limit:
            break
    return {"query": query, "count": len(results), "observations": results}


def save_pattern_review(data: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    for field in ("review_type", "period_start", "period_end", "review", "observation_ids"):
        if field not in data or data[field] in (None, ""):
            raise ValueError(f"Missing required field: {field}")
    kind = data["review_type"]
    if kind not in VALID_REVIEW:
        raise ValueError("review_type must be weekly, monthly, or quarterly")
    start, end = _date(data["period_start"], "period_start"), _date(data["period_end"], "period_end")
    if start > end:
        raise ValueError("period_start must be on or before period_end")
    review_id = str(data.get("id") or uuid.uuid4())
    metadata = {
        "type": "behaviour-pattern-review", "id": review_id, "review_type": kind,
        "period_start": start, "period_end": end, "created_at": datetime.now().astimezone().isoformat(),
        "observation_ids": data["observation_ids"], "observation_count": len(data["observation_ids"]),
        "recurring_themes": data.get("recurring_themes", []), "apparent_gaps": data.get("apparent_gaps", []),
        "method_note": "Absence in recorded notes is not evidence of failure to perceive or attend outside the archive.",
    }
    body = _frontmatter(metadata) + f"\n# {kind.title()} pattern review\n\n{data['review'].strip()}\n"
    _, reviews = _dirs(root)
    path = _write_once(reviews, f"{start}--{end}-{kind}-pattern-review--{review_id[:8]}.md", body)
    return {"id": review_id, "path": str(path), "metadata": metadata}
