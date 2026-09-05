# FaceProof — Hacker House Goa 2026 Task 3

FaceProof is a consent-based face-evidence and content-provenance prototype. It analyzes an uploaded image locally, can send that image to a configured genuine visual-search provider, fingerprints selected source metadata with SHA-256, and writes/reads/verifies a proof using a persisted local tamper-evident ledger.

It **does not identify people**, prove ownership, or establish that two people are the same. Face similarity is only an investigation aid. Use only images that you are authorized to process.

## Quick start (Windows PowerShell)

From this folder:

```powershell
.\scripts\setup.ps1
.\scripts\start-backend.ps1
```

Open another PowerShell window:

```powershell
cd C:\Users\SAHIL\OneDrive\Desktop\Hacker_House_Goa_2026\Task_3
.\scripts\start-frontend.ps1
```

Open `http://127.0.0.1:5174`. The API health endpoint is `http://127.0.0.1:8001/api/health`.

## Genuine search setup

The app deliberately creates **no fabricated web results**. To use a real image-based web search, copy `.env.example` to `.env` and set `BING_VISUAL_SEARCH_KEY` to an Azure Bing Visual Search subscription key. Restart the backend; the dashboard will show “Genuine search enabled”.

Without that key, local face analysis and the ledger API still work, while search clearly reports that no genuine provider is configured.

## Verification flow

1. Upload an authorized image and run face analysis.
2. Run genuine visual search (requires the key above).
3. Select a result; its image is compared only when it is publicly fetchable.
4. Create a SHA-256 fingerprint from stable canonical source metadata.
5. Record it in the local ledger, then verify it.
6. Use **Demo tamper** to intentionally mutate the local record; verification then fails.

## Project layout

```text
Task_3/
├── backend/       FastAPI API, providers, fingerprinting, local ledger, tests
├── frontend/      React + TypeScript dashboard
├── blockchain/    Solidity reference contract and local-ledger notes
├── docs/          Architecture, security, test, demo and submission material
└── scripts/       Windows setup/start/check commands
```

Read [backend setup](backend/README.md), [frontend setup](frontend/README.md), [blockchain notes](blockchain/README.md), and [submission checklist](docs/20-submission-checklist.md).

