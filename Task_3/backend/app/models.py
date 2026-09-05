from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class FaceAnalysis(BaseModel):
    faces_detected: int
    primary_face_box: list[int] | None = None
    image_sha256: str
    provider: str
    warning: str | None = None


class SearchCandidate(BaseModel):
    id: str
    title: str
    page_url: str
    image_url: str | None = None
    source: str
    similarity: float | None = None
    match_status: str
    published_at: str | None = None


class SearchResponse(BaseModel):
    search_id: str
    mode: str
    provider: str
    results: list[SearchCandidate]
    message: str | None = None


class CandidateSelection(BaseModel):
    candidate_id: str


class FingerprintRequest(BaseModel):
    search_id: str
    candidate_id: str


class FingerprintResponse(BaseModel):
    fingerprint: str
    canonical_payload: dict[str, Any]
    image_sha256: str
    source_url: str
    created_at: datetime


class RecordRequest(BaseModel):
    fingerprint: str = Field(min_length=64, max_length=64)
    source_url: HttpUrl


class LedgerRecord(BaseModel):
    fingerprint: str
    source_url: str
    recorded_at: str
    tx_hash: str
    block_number: int
    block_hash: str
    previous_block_hash: str
    chain: str


class VerifyRequest(BaseModel):
    fingerprint: str
    source_url: HttpUrl


class VerifyResponse(BaseModel):
    valid: bool
    reason: str
    record: LedgerRecord | None = None

