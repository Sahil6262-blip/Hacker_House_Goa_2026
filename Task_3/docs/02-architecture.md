# Architecture

```text
React dashboard → FastAPI → local OpenCV face provider
                         → Bing Visual Search (only with configured key)
                         → canonical JSON + SHA-256 → LocalLedger
```

The search and face implementations are provider abstractions so they can be replaced without changing API consumers.

