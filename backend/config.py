"""
配置管理模块
集中管理所有环境变量和配置项
"""
import os


class Settings:
    """应用配置"""

    # 数据库路径
    PLAYBACK_DB: str = os.getenv("PLAYBACK_DB", "/data/playback_reporting.db")
    USERS_DB: str = os.getenv("USERS_DB", "/data/users.db")
    AUTH_DB: str = os.getenv("AUTH_DB", "/data/authentication.db")

    # Emby 服务器配置
    EMBY_URL: str = os.getenv("EMBY_URL", "http://localhost:8096")
    EMBY_API_KEY: str = os.getenv("EMBY_API_KEY", "")

    # 播放过滤配置
    # 最小播放时长过滤（秒），低于此时长的记录将被忽略，0 表示不过滤
    MIN_PLAY_DURATION: int = int(os.getenv("MIN_PLAY_DURATION", "0"))

    # 时区偏移（小时），用于 SQLite 查询时间转换，上海时区为 +8
    TZ_OFFSET: int = int(os.getenv("TZ_OFFSET", "8"))

    # 缓存配置
    ITEM_CACHE_MAX_SIZE: int = 500
    ITEM_CACHE_EVICT_COUNT: int = 100


settings = Settings()
