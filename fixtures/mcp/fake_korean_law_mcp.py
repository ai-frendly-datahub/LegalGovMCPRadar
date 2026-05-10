#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from typing import Any


TOOLS = [
    {
        "name": "korean-law",
        "title": "Korean Law Search",
        "description": "Return deterministic Korean law fixture results.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    }
]

LAW_RESULT = {
    "title": "Korean law fixture result",
    "url": "https://example.test/legal-gov/korean-law-fixture",
    "summary": "Fixture-only Korean law MCP result for collector normalization.",
    "law_id": "fixture-law-privacy",
    "source": "fixture",
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
                "serverInfo": {"name": "fake-korean-law-mcp", "version": "0.0.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params") if isinstance(message.get("params"), dict) else {}
        if params.get("name") != "korean-law":
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
                "content": [
                    {"type": "text", "text": json.dumps(LAW_RESULT, ensure_ascii=False)}
                ],
                "structuredContent": LAW_RESULT,
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
