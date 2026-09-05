# Canonical fingerprinting

The proof hash is SHA-256 over canonical JSON: schema version, uploaded image SHA-256, source URL, source title, and search provider. Keys are sorted and compactly serialized, making identical inputs reproducible. Raw image bytes and face descriptors are excluded from the record.

