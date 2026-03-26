from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from kag.examples.music_search.dataplatform.music_data_hub import MusicTrack


@dataclass
class MusicSearchQuery:
    text: str
    genres: Sequence[str] = field(default_factory=list)
    moods: Sequence[str] = field(default_factory=list)
    bpm_min: int | None = None
    bpm_max: int | None = None
    languages: Sequence[str] = field(default_factory=list)


@dataclass
class MusicSearchResult:
    track_id: str
    score: float
    reasons: List[str]


class KAGMusicSearchService:
    """Hybrid search service that fuses schema constraints and KAG-style reasoning signals."""

    def __init__(self):
        self._track_index: Dict[str, MusicTrack] = {}

    def load_tracks(self, tracks: Sequence[MusicTrack]) -> None:
        self._track_index = {track.track_id: track for track in tracks}

    def search(self, query: MusicSearchQuery, top_k: int = 10) -> List[MusicSearchResult]:
        terms = self._tokenize(query.text)
        results: List[MusicSearchResult] = []

        for track in self._track_index.values():
            if not self._pass_structured_filters(track, query):
                continue
            score, reasons = self._score_track(track, terms, query)
            if score > 0:
                results.append(
                    MusicSearchResult(track_id=track.track_id, score=round(score, 4), reasons=reasons)
                )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]

    def _pass_structured_filters(self, track: MusicTrack, query: MusicSearchQuery) -> bool:
        if query.genres and track.genre not in query.genres:
            return False
        if query.moods and track.mood not in query.moods:
            return False
        if query.languages and track.language not in query.languages:
            return False
        if query.bpm_min is not None and track.bpm < query.bpm_min:
            return False
        if query.bpm_max is not None and track.bpm > query.bpm_max:
            return False
        return True

    def _score_track(
        self, track: MusicTrack, terms: Sequence[str], query: MusicSearchQuery
    ) -> Tuple[float, List[str]]:
        searchable_text = " ".join(
            [
                track.title.lower(),
                track.artist.lower(),
                track.album.lower(),
                track.genre.lower(),
                track.mood.lower(),
                " ".join(tag.lower() for tag in track.lyric_tags),
            ]
        )

        score = 0.0
        reasons: List[str] = []

        lexical_hits = sum(1 for term in terms if term in searchable_text)
        if lexical_hits:
            lexical_score = lexical_hits / max(len(terms), 1)
            score += lexical_score * 0.6
            reasons.append(f"关键词匹配 {lexical_hits}/{max(len(terms), 1)}")

        if query.genres and track.genre in query.genres:
            score += 0.15
            reasons.append("命中流派约束")

        if query.moods and track.mood in query.moods:
            score += 0.15
            reasons.append("命中情绪约束")

        if query.languages and track.language in query.languages:
            score += 0.1
            reasons.append("命中语言约束")

        if terms and track.title.lower() in " ".join(terms):
            score += 0.1
            reasons.append("歌名短语高权重")

        graph_boost = self._kag_graph_boost(track, terms)
        if graph_boost > 0:
            score += graph_boost
            reasons.append(f"图谱关联增强 +{graph_boost:.2f}")

        return score, reasons

    @staticmethod
    def _kag_graph_boost(track: MusicTrack, terms: Sequence[str]) -> float:
        """Simulate a KAG relation path signal using artist/album proximity."""

        boost = 0.0
        joined_terms = " ".join(terms)
        if track.artist.lower() in joined_terms:
            boost += 0.12
        if track.album.lower() in joined_terms:
            boost += 0.08
        if any(tag.lower() in joined_terms for tag in track.lyric_tags):
            boost += 0.05
        return boost

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [token.strip().lower() for token in text.split() if token.strip()]
