# Blockchain / proof layer

The shipped default is `LocalLedger`: an append-only, disk-persisted hash chain with a transaction hash and previous-block hash. It enables a reproducible local record → read → verify → tamper-fail demo without a wallet, private key, or network access.

It is not a public blockchain. For a public EVM deployment, use `contracts/FingerprintRegistry.sol` with a reviewed wallet/key-management setup, then implement an EVM provider that writes only the content fingerprint and non-sensitive source URL. Never put face images or biometric descriptors on-chain.

