from app.services.fingerprint import create_fingerprint


def test_fingerprint_is_stable_for_same_content():
    first = create_fingerprint(image_sha256="a" * 64, source_url="https://example.com/a", title="A", search_provider="Bing")
    second = create_fingerprint(image_sha256="a" * 64, source_url="https://example.com/a", title="A", search_provider="Bing")
    assert first == second


def test_fingerprint_changes_when_source_changes():
    first = create_fingerprint(image_sha256="a" * 64, source_url="https://example.com/a", title="A", search_provider="Bing")
    second = create_fingerprint(image_sha256="a" * 64, source_url="https://example.com/b", title="A", search_provider="Bing")
    assert first[0] != second[0]

