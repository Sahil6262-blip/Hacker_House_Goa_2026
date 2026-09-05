import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def create_fingerprint(*, image_sha256: str, source_url: str, title: str, search_provider: str) -> tuple[str, dict[str, Any]]:
    payload = {
        "image_sha256": image_sha256,
        "search_provider": search_provider,
        "source_title": title.strip(),
        "source_url": source_url.strip(),
        "schema": "hhgoa-task3-content-proof/v1",
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest(), payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

