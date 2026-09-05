from dataclasses import dataclass

from app.models import SearchCandidate
from app.services.face import FaceEncoding


@dataclass
class SearchSession:
    image_bytes: bytes
    face: FaceEncoding
    candidates: list[SearchCandidate]
    provider: str


class SessionStore:
    def __init__(self) -> None:
        self.sessions: dict[str, SearchSession] = {}

    def put(self, search_id: str, session: SearchSession) -> None:
        self.sessions[search_id] = session

    def get(self, search_id: str) -> SearchSession | None:
        return self.sessions.get(search_id)

