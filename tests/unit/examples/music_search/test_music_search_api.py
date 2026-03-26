from kag.examples.music_search.backend.music_search_api import MusicSearchKAGFacade


def test_music_search_facade_end_to_end():
    facade = MusicSearchKAGFacade()
    count = facade.sync_catalog(
        [
            {
                "track_id": "t1",
                "title": "晴天",
                "artist": "周杰伦",
                "album": "叶惠美",
                "genre": "pop",
                "mood": "healing",
                "bpm": 92,
                "language": "zh",
                "lyric_tags": ["青春", "回忆"],
            },
            {
                "track_id": "t2",
                "title": "夜曲",
                "artist": "周杰伦",
                "album": "十一月的萧邦",
                "genre": "pop",
                "mood": "sad",
                "bpm": 88,
                "language": "zh",
                "lyric_tags": ["钢琴", "夜晚"],
            },
        ]
    )

    assert count == 2

    results = facade.search(
        {
            "text": "周杰伦 青春 回忆",
            "genres": ["pop"],
            "moods": ["healing"],
            "languages": ["zh"],
            "bpm_min": 80,
            "bpm_max": 100,
        },
        top_k=3,
    )

    assert results
    assert results[0]["track_id"] == "t1"
    assert any("图谱关联增强" in reason for reason in results[0]["reasons"])

    records = facade.export_spg_records()
    assert len(records) == 2
    assert records[0].spg_type_name == "Track"
