# Data lifecycle

Uploads are read into memory for analysis and session-scoped search; raw uploads are not stored by the application. The persisted local ledger contains only fingerprint metadata and source URL. Clear `data/local_chain.json` to reset local demo records; it is ignored by Git.

