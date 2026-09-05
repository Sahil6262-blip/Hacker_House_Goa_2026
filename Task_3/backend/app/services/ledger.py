import hashlib
import json
from pathlib import Path
from threading import Lock
from typing import Any

from app.models import LedgerRecord
from app.services.fingerprint import canonical_json, utc_now


class LocalLedger:
    """Persisted append-only hash chain for development and offline demos."""

    chain_name = "local-tamper-evident-ledger"

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = Lock()

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
        except json.JSONDecodeError:
            raise RuntimeError("Local ledger is corrupt; refuse to write a new record.")

    def _save(self, rows: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)

    def record(self, fingerprint: str, source_url: str) -> LedgerRecord:
        with self.lock:
            rows = self._load()
            existing = next((item for item in rows if item["fingerprint"] == fingerprint), None)
            if existing:
                return LedgerRecord(**existing)
            previous = rows[-1]["block_hash"] if rows else "0" * 64
            payload = {
                "fingerprint": fingerprint,
                "source_url": source_url,
                "recorded_at": utc_now(),
                "block_number": len(rows) + 1,
                "previous_block_hash": previous,
                "chain": self.chain_name,
            }
            tx_hash = hashlib.sha256(canonical_json(payload).encode()).hexdigest()
            block_hash = hashlib.sha256((previous + tx_hash).encode()).hexdigest()
            record = {**payload, "tx_hash": tx_hash, "block_hash": block_hash}
            rows.append(record)
            self._save(rows)
            return LedgerRecord(**record)

    def get(self, fingerprint: str) -> LedgerRecord | None:
        with self.lock:
            row = next((item for item in self._load() if item["fingerprint"] == fingerprint), None)
            return LedgerRecord(**row) if row else None

    def verify(self, fingerprint: str, source_url: str) -> tuple[bool, str, LedgerRecord | None]:
        record = self.get(fingerprint)
        if record is None:
            return False, "Fingerprint is not recorded in the local ledger.", None
        if record.source_url != source_url:
            return False, "Source URL differs from the recorded content proof.", record
        expected_tx = hashlib.sha256(canonical_json({
            "fingerprint": record.fingerprint, "source_url": record.source_url,
            "recorded_at": record.recorded_at, "block_number": record.block_number,
            "previous_block_hash": record.previous_block_hash, "chain": record.chain,
        }).encode()).hexdigest()
        expected_block = hashlib.sha256((record.previous_block_hash + expected_tx).encode()).hexdigest()
        if expected_tx != record.tx_hash or expected_block != record.block_hash:
            return False, "Ledger record integrity check failed.", record
        return True, "Fingerprint, source URL, and ledger record match.", record

    def tamper_for_demo(self, fingerprint: str) -> bool:
        with self.lock:
            rows = self._load()
            for row in rows:
                if row["fingerprint"] == fingerprint:
                    row["source_url"] = row["source_url"] + "#tampered-demo"
                    self._save(rows)
                    return True
        return False

