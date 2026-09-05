import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


@dataclass
class SearchHit:
    title: str
    page_url: str
    image_url: str | None
    source: str
    published_at: str | None = None


class SearchProvider(Protocol):
    name: str
    genuine: bool

    async def search(self, image_bytes: bytes) -> list[SearchHit]: ...


class BingVisualSearchProvider:
    """Runs a real visual search over the uploaded image when configured."""

    name = "Bing Visual Search"
    genuine = True

    def __init__(self, api_key: str, url: str, timeout_seconds: float) -> None:
        self.api_key = api_key
        self.url = url
        self.timeout_seconds = timeout_seconds

    async def search(self, image_bytes: bytes) -> list[SearchHit]:
        if not self.api_key:
            raise RuntimeError("Bing Visual Search is not configured. Set BING_VISUAL_SEARCH_KEY.")
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        files = {"image": ("query.jpg", image_bytes, "application/octet-stream")}
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = await client.post(self.url, headers=headers, files=files)
            response.raise_for_status()
        return self._parse(response.json())

    def _parse(self, payload: dict[str, Any]) -> list[SearchHit]:
        hits: list[SearchHit] = []
        seen: set[str] = set()

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                page_url = value.get("hostPageUrl") or value.get("webSearchUrl") or value.get("contentUrl")
                if isinstance(page_url, str) and page_url.startswith("http") and page_url not in seen:
                    seen.add(page_url)
                    hits.append(
                        SearchHit(
                            title=str(value.get("name") or value.get("text") or "Visual-search result"),
                            page_url=page_url,
                            image_url=value.get("thumbnailUrl") or value.get("contentUrl"),
                            source="Bing Visual Search",
                            published_at=value.get("datePublished"),
                        )
                    )
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(payload)
        return hits[:20]


class UnconfiguredSearchProvider:
    name = "No genuine provider configured"
    genuine = False

    async def search(self, image_bytes: bytes) -> list[SearchHit]:
        return []


def candidate_id(hit: SearchHit) -> str:
    canonical = json.dumps({"url": hit.page_url, "image": hit.image_url}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]

