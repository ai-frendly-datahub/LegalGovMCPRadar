#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from typing import Any


TOOLS = [
    {
        "name": "search_laws",
        "title": "Search Laws",
        "description": "Return deterministic law search fixture results.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    },
    {
        "name": "get_law_details",
        "title": "Get Law Details",
        "description": "Return deterministic law detail fixture results.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    },
]

TOOL_RESULTS = {
    "search_laws": {
        "title": "Finalchild law search fixture",
        "url": "https://example.test/legal-gov/finalchild-law-search",
        "summary": "Fixture-only law search result for collector normalization.",
        "law_id": "fixture-search-law",
        "source": "fixture",
    },
    "get_law_details": {
        "title": "Finalchild law details fixture",
        "url": "https://example.test/legal-gov/finalchild-law-details",
        "summary": "Fixture-only law detail result for collector normalization.",
        "law_id": "fixture-detail-law",
        "source": "fixture",
    },
}


def write_message(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def response_for(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fake-finalchild-law-mcp", "version": "0.0.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params") if isinstance(message.get("params"), dict) else {}
        tool_name = params.get("name")
        result = TOOL_RESULTS.get(str(tool_name))
        if result is None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": "Unsupported tool"}],
                },
            }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "structuredContent": result,
            },
        }
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unsupported method: {method}"},
    }


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict):
            continue
        response = response_for(message)
        if response is not None:
            write_message(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
