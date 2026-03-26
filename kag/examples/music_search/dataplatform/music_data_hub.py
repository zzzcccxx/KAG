from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from kag.builder.model.spg_record import SPGRecord


@dataclass
class MusicTrack:
    """Normalized track object for middle-platform ingestion."""

    track_id: str
    title: str
    artist: str
    album: str
    genre: str
    mood: str
    bpm: int
    language: str = "zh"
    lyric_tags: List[str] = field(default_factory=list)


class MusicDataHub:
    """Data middle-platform: normalize raw rows and materialize SPG records."""

    def __init__(self):
        self._tracks: Dict[str, MusicTrack] = {}

    def ingest_rows(self, rows: Iterable[dict]) -> List[MusicTrack]:
        normalized_tracks: List[MusicTrack] = []
        for row in rows:
            track = MusicTrack(
                track_id=str(row["track_id"]),
                title=str(row["title"]),
                artist=str(row["artist"]),
                album=str(row.get("album", "Unknown Album")),
                genre=str(row.get("genre", "unknown")),
                mood=str(row.get("mood", "neutral")),
                bpm=int(row.get("bpm", 90)),
                language=str(row.get("language", "zh")),
                lyric_tags=[str(tag) for tag in row.get("lyric_tags", [])],
            )
            self._tracks[track.track_id] = track
            normalized_tracks.append(track)
        return normalized_tracks

    def get_track(self, track_id: str) -> Optional[MusicTrack]:
        return self._tracks.get(track_id)

    def all_tracks(self) -> List[MusicTrack]:
        return list(self._tracks.values())

    def to_spg_records(self) -> List[SPGRecord]:
        """Convert normalized tracks into SPG records for KAG builders."""

        records: List[SPGRecord] = []
        for track in self._tracks.values():
            record = SPGRecord("Track")
            record.upsert_properties(
                {
                    "id": track.track_id,
                    "title": track.title,
                    "name": track.title,
                    "genre": track.genre,
                    "mood": track.mood,
                    "bpm": str(track.bpm),
                    "language": track.language,
                    "lyric_tags": ",".join(track.lyric_tags),
                }
            )
            record.upsert_relation("Artist_publish_Track", "Artist", track.artist)
            record.upsert_relation("Album_include_Track", "Album", track.album)
            records.append(record)
        return records
