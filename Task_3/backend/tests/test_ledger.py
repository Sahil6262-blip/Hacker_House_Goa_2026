from app.services.ledger import LocalLedger


def test_record_and_verify(tmp_path):
    ledger = LocalLedger(tmp_path / "ledger.json")
    fingerprint = "a" * 64
    recorded = ledger.record(fingerprint, "https://example.com/article")
    verified, _, found = ledger.verify(fingerprint, "https://example.com/article")
    assert recorded.fingerprint == fingerprint
    assert verified is True
    assert found is not None


def test_tampered_record_fails_integrity(tmp_path):
    ledger = LocalLedger(tmp_path / "ledger.json")
    fingerprint = "b" * 64
    ledger.record(fingerprint, "https://example.com/article")
    assert ledger.tamper_for_demo(fingerprint)
    verified, _, _ = ledger.verify(fingerprint, "https://example.com/article#tampered-demo")
    assert verified is False

