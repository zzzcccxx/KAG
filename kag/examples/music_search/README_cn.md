# 音乐搜索与 KAG 深度融合示例

该示例提供了“前端页面 + 数据中台 + 后端算法”三层联动的最小实现，用于将音乐搜索业务与 KAG 的 Schema/图检索能力融合。

## 目录说明

- `schema/MusicSearch.schema`：音乐领域 schema 建模（歌手/专辑/歌曲/关系）。
- `dataplatform/music_data_hub.py`：数据中台，负责原始数据归一化和 SPG Record 导出。
- `backend/music_search_service.py`：后端检索算法，支持关键词召回、结构化约束、图谱增强。
- `backend/music_search_api.py`：端到端门面层，提供目录同步、检索、导出接口。

## 快速使用

```python
from kag.examples.music_search.backend.music_search_api import MusicSearchKAGFacade

facade = MusicSearchKAGFacade()
facade.sync_catalog([
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
    }
])

result = facade.search(
    {
        "text": "周杰伦 青春 回忆",
        "genres": ["pop"],
        "moods": ["healing"],
        "languages": ["zh"],
        "bpm_min": 80,
        "bpm_max": 110,
    },
    top_k=5,
)

print(result)
```

## 集成建议

1. 将在线行为日志（播放/收藏/跳过）回流到中台，丰富 `lyric_tags` 与用户偏好画像。
2. 通过 KAG Builder 将 `export_spg_records()` 输出写入图谱，支持多跳问答与解释。
3. 与推荐系统联动：将本示例的 `score + reasons` 作为召回阶段特征，进入重排模型。
