import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import (
    CandidateSelection,
    FaceAnalysis,
    FingerprintRequest,
    FingerprintResponse,
    RecordRequest,
    SearchCandidate,
    SearchResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.services.face import OpenCVFaceProvider
from app.services.fingerprint import create_fingerprint, utc_now
from app.services.ledger import LocalLedger
from app.services.search import BingVisualSearchProvider, UnconfiguredSearchProvider, candidate_id
from app.state import SearchSession, SessionStore

settings = get_settings()
face_provider = OpenCVFaceProvider()
ledger = LocalLedger(settings.ledger_path)
sessions = SessionStore()


def search_provider():
    if settings.search_provider == "bing_visual_search" and settings.bing_visual_search_key:
        return BingVisualSearchProvider(
            settings.bing_visual_search_key,
            settings.bing_visual_search_url,
            settings.search_timeout_seconds,
        )
    return UnconfiguredSearchProvider()


async def image_from_upload(upload: UploadFile) -> bytes:
    if upload.content_type and not upload.content_type.startswith("image/"):
        raise HTTPException(415, "Upload an image file (JPEG, PNG, or WebP).")
    data = await upload.read()
    if not data:
        raise HTTPException(400, "The uploaded image is empty.")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Image exceeds the {settings.max_upload_mb} MB limit.")
    return data


async def similarity_for(candidate: SearchCandidate, original_descriptor):
    if not candidate.image_url:
        return None, "No candidate image was supplied by the search provider."
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(candidate.image_url)
            response.raise_for_status()
        candidate_face = face_provider.analyze(response.content)
        value = face_provider.similarity(original_descriptor, candidate_face.descriptor)
        if value is None:
            return None, "A comparable face was not detected in the candidate image."
        return value, "Similarity is a prototype aid only; it does not confirm identity."
    except (httpx.HTTPError, ValueError):
        return None, "Candidate image could not be read for similarity analysis."


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ledger_path.parent.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="FaceProof Task 3 API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "faceproof-api"}


@app.get("/api/config")
@app.get("/api/config/status")
async def config_status():
    provider = search_provider()
    return {
        "face_provider": face_provider.name,
        "search_provider": provider.name,
        "genuine_search_enabled": provider.genuine,
        "blockchain_provider": ledger.chain_name,
        "privacy": "Uploads are processed in memory for this session; do not use without consent.",
    }


@app.post("/api/face/analyze", response_model=FaceAnalysis)
async def analyze_face(image: UploadFile = File(...)):
    try:
        face = face_provider.analyze(await image_from_upload(image))
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    return FaceAnalysis(
        faces_detected=face.face_count,
        primary_face_box=face.primary_box,
        image_sha256=face.image_sha256,
        provider=face_provider.name,
        warning=("No face detected. Search may still run, but similarity cannot be calculated." if not face.face_count else None),
    )


@app.post("/api/search", response_model=SearchResponse)
async def search(image: UploadFile = File(...)):
    image_bytes = await image_from_upload(image)
    try:
        face = face_provider.analyze(image_bytes)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    provider = search_provider()
    if not provider.genuine:
        search_id = str(uuid.uuid4())
        sessions.put(search_id, SearchSession(image_bytes, face, [], provider.name))
        return SearchResponse(
            search_id=search_id,
            mode="local_unconfigured",
            provider=provider.name,
            results=[],
            message="Genuine visual search is disabled. Configure BING_VISUAL_SEARCH_KEY; no demo web results are fabricated.",
        )
    try:
        hits = await provider.search(image_bytes)
    except (RuntimeError, httpx.HTTPError) as error:
        raise HTTPException(502, f"Visual search failed: {error}") from error
    candidates = [
        SearchCandidate(
            id=candidate_id(hit), title=hit.title, page_url=hit.page_url, image_url=hit.image_url,
            source=hit.source, published_at=hit.published_at, match_status="Not compared yet",
        )
        for hit in hits
    ]
    search_id = str(uuid.uuid4())
    sessions.put(search_id, SearchSession(image_bytes, face, candidates, provider.name))
    return SearchResponse(search_id=search_id, mode="genuine", provider=provider.name, results=candidates)


@app.post("/api/search/{search_id}/select", response_model=SearchCandidate)
async def select_candidate(search_id: str, selection: CandidateSelection):
    session = sessions.get(search_id)
    if not session:
        raise HTTPException(404, "Search session not found. Run a new search.")
    candidate = next((item for item in session.candidates if item.id == selection.candidate_id), None)
    if not candidate:
        raise HTTPException(404, "Candidate not found in this search session.")
    similarity, status = await similarity_for(candidate, session.face.descriptor)
    candidate.similarity = similarity
    candidate.match_status = status
    return candidate


@app.post("/api/fingerprint/create", response_model=FingerprintResponse)
async def fingerprint(request: FingerprintRequest):
    session = sessions.get(request.search_id)
    if not session:
        raise HTTPException(404, "Search session not found. Run a new search.")
    candidate = next((item for item in session.candidates if item.id == request.candidate_id), None)
    if not candidate:
        raise HTTPException(404, "Candidate not found in this search session.")
    value, payload = create_fingerprint(
        image_sha256=session.face.image_sha256, source_url=candidate.page_url,
        title=candidate.title, search_provider=session.provider,
    )
    return FingerprintResponse(
        fingerprint=value, canonical_payload=payload, image_sha256=session.face.image_sha256,
        source_url=candidate.page_url, created_at=utc_now(),
    )


@app.post("/api/blockchain/record")
async def record(request: RecordRequest):
    return ledger.record(request.fingerprint, str(request.source_url))


@app.get("/api/blockchain/record/{fingerprint}")
async def get_record(fingerprint: str):
    record = ledger.get(fingerprint)
    if not record:
        raise HTTPException(404, "No ledger record for this fingerprint.")
    return record


@app.post("/api/blockchain/verify", response_model=VerifyResponse)
async def verify(request: VerifyRequest):
    valid, reason, record = ledger.verify(request.fingerprint, str(request.source_url))
    return VerifyResponse(valid=valid, reason=reason, record=record)


@app.post("/api/demo/tamper")
async def tamper(fingerprint: str):
    if not ledger.tamper_for_demo(fingerprint):
        raise HTTPException(404, "No ledger record for this fingerprint.")
    return {"tampered": True, "warning": "Demo-only: local ledger record was intentionally altered."}

