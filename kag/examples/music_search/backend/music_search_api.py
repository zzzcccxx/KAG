from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Iterable, List

from kag.examples.music_search.backend.music_search_service import (
    KAGMusicSearchService,
    MusicSearchQuery,
)
from kag.examples.music_search.dataplatform.music_data_hub import MusicDataHub


class MusicSearchKAGFacade:
    """End-to-end facade: frontend request -> data hub -> KAG hybrid retrieval."""

    def __init__(self):
        self._data_hub = MusicDataHub()
        self._service = KAGMusicSearchService()

    def sync_catalog(self, rows: Iterable[Dict[str, Any]]) -> int:
        tracks = self._data_hub.ingest_rows(rows)
        self._service.load_tracks(tracks)
        return len(tracks)

    def search(self, payload: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        query = MusicSearchQuery(
            text=str(payload.get("text", "")),
            genres=payload.get("genres", []),
            moods=payload.get("moods", []),
            bpm_min=payload.get("bpm_min"),
            bpm_max=payload.get("bpm_max"),
            languages=payload.get("languages", []),
        )
        results = self._service.search(query=query, top_k=top_k)
        return [asdict(item) for item in results]

    def export_spg_records(self):
        return self._data_hub.to_spg_records()
