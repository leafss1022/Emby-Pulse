"""
数据库工具模块
提供数据库连接和 SQL 辅助函数
"""
import aiosqlite
from typing import Optional
from config import settings
from db_pool import pool_manager


def get_playback_db(server_config: Optional[dict] = None):
    """获取播放记录数据库连接（使用连接池）"""
    if server_config:
        db_path = server_config.get('playback_db', settings.PLAYBACK_DB)
    else:
        db_path = settings.PLAYBACK_DB
    return pool_manager.connection(db_path, pool_size=5)


def get_users_db(server_config: Optional[dict] = None):
    """获取用户数据库连接（使用连接池）"""
    if server_config:
        db_path = server_config.get('users_db', settings.USERS_DB)
    else:
        db_path = settings.USERS_DB
    return pool_manager.connection(db_path, pool_size=3)


def get_auth_db(server_config: Optional[dict] = None):
    """获取认证数据库连接（使用连接池）"""
    if server_config:
        db_path = server_config.get('auth_db', settings.AUTH_DB)
    else:
        db_path = settings.AUTH_DB
    return pool_manager.connection(db_path, pool_size=2)


def get_library_db(server_config: Optional[dict] = None):
    """获取媒体库数据库连接（使用连接池）"""
    # library.db 通常和 users.db 在同一目录
    if server_config:
        users_db = server_config.get('users_db', settings.USERS_DB)
        library_db = users_db.replace('users.db', 'library.db')
    else:
        library_db = settings.USERS_DB.replace('users.db', 'library.db')
    return pool_manager.connection(library_db, pool_size=3)



def get_count_expr() -> str:
    """获取播放次数统计表达式（条件计数，只统计满足时长要求的）"""
    if settings.MIN_PLAY_DURATION > 0:
        return f"SUM(CASE WHEN COALESCE(PlayDuration, 0) >= {settings.MIN_PLAY_DURATION} THEN 1 ELSE 0 END)"
    return "COUNT(*)"


def get_duration_filter() -> str:
    """获取播放时长过滤 SQL 条件（用于最近播放等需要完全过滤的场景）"""
    if settings.MIN_PLAY_DURATION > 0:
        return f" AND COALESCE(PlayDuration, 0) >= {settings.MIN_PLAY_DURATION}"
    return ""


def local_datetime(column: str) -> str:
    """将 UTC 时间列转换为本地时间的 SQL 表达式"""
    offset = settings.TZ_OFFSET
    if offset >= 0:
        return f"datetime({column}, '+{offset} hours')"
    else:
        return f"datetime({column}, '{offset} hours')"


def local_date(column: str) -> str:
    """将 UTC 时间列转换为本地日期的 SQL 表达式"""
    offset = settings.TZ_OFFSET
    if offset >= 0:
        return f"date({column}, '+{offset} hours')"
    else:
        return f"date({column}, '{offset} hours')"


def convert_guid_bytes_to_standard(guid_bytes: bytes) -> str:
    """将 SQLite 中的 GUID 字节转换为标准格式（小写无连字符）
    SQLite 存储的是 .NET GUID 的字节格式，前三部分需要反转字节序
    """
    if len(guid_bytes) != 16:
        return guid_bytes.hex().lower()
    # .NET GUID 格式: 前4字节、接下来2字节、再接下来2字节需要反转，后8字节保持不变
    part1 = guid_bytes[0:4][::-1]  # 反转前4字节
    part2 = guid_bytes[4:6][::-1]  # 反转接下来2字节
    part3 = guid_bytes[6:8][::-1]  # 反转再接下来2字节
    part4 = guid_bytes[8:16]       # 后8字节保持不变
    return (part1 + part2 + part3 + part4).hex().lower()
