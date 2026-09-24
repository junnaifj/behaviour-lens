#!/usr/bin/env python3
"""Minimal MCP stdio server exposing Behaviour Lens vault operations."""
from __future__ import annotations

import json
import sys
from typing import Any

from vault_store import get_observations_by_period, save_observation, save_pattern_review, search_observations

TOOLS = [
    {"name": "save_observation", "description": "Save one structured Behaviour Lens Markdown observation note to the configured Obsidian vault.", "inputSchema": {"type": "object", "required": ["observation", "brief", "date", "evidence_status"], "properties": {"observation": {"type": "string"}, "brief": {"type": "string"}, "date": {"type": "string"}, "observed_at": {"type": "string"}, "evidence_status": {"enum": ["supported", "partly-supported", "uncertain", "potentially-misleading"]}, "domain": {"type": "array", "items": {"type": "string"}}, "setting": {"type": "array", "items": {"type": "string"}}, "behavioural_theme": {"type": "array", "items": {"type": "string"}}, "analytical_scale": {"type": "array", "items": {"type": "string"}}, "framing": {"type": "array", "items": {"type": "string"}}, "ai_relevance": {"enum": ["none", "indirect", "direct"]}, "keywords": {"type": "array", "items": {"type": "string"}}, "pattern_ids": {"type": "array", "items": {"type": "string"}}, "sources": {"type": "array", "items": {"type": "object"}}, "slug": {"type": "string"}}}},
    {"name": "search_observations", "description": "Full-text search observation notes, optionally filtering exact metadata values.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "filters": {"type": "object"}, "limit": {"type": "integer", "minimum": 1, "maximum": 500}}}},
    {"name": "get_observations_by_period", "description": "Retrieve observation notes within an inclusive ISO date range for longitudinal review.", "inputSchema": {"type": "object", "required": ["start_date", "end_date"], "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}, "include_content": {"type": "boolean"}}}},
    {"name": "save_pattern_review", "description": "Save a weekly, monthly, or quarterly meta-pattern review as Markdown.", "inputSchema": {"type": "object", "required": ["review_type", "period_start", "period_end", "review", "observation_ids"], "properties": {"review_type": {"enum": ["weekly", "monthly", "quarterly"]}, "period_start": {"type": "string"}, "period_end": {"type": "string"}, "review": {"type": "string"}, "observation_ids": {"type": "array", "items": {"type": "string"}}, "recurring_themes": {"type": "array", "items": {"type": "string"}}, "apparent_gaps": {"type": "array", "items": {"type": "string"}}}}},
]

CALLS = {"save_observation": save_observation, "search_observations": search_observations, "get_observations_by_period": get_observations_by_period, "save_pattern_review": save_pattern_review}


def response(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id, method = message.get("id"), message.get("method")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        result = {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}}, "serverInfo": {"name": "behaviour-lens-vault", "version": "0.1.0"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = message.get("params", {})
        name, arguments = params.get("name"), params.get("arguments", {})
        if name not in CALLS:
            raise ValueError(f"Unknown tool: {name}")
        payload = CALLS[name](**arguments)
        result = {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}], "structuredContent": payload}
    else:
        raise ValueError(f"Unsupported method: {method}")
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        message = json.loads(line)
        try:
            output = response(message)
        except Exception as exc:
            output = {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32602, "message": str(exc)}}
        if output is not None:
            sys.stdout.write(json.dumps(output, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
