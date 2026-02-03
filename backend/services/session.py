"""
会话管理服务
提供会话的创建、验证、删除和持久化存储
"""
import secrets
import time
import aiosqlite
from typing import Optional
from pathlib import Path
from logger import get_logger

logger = get_logger("services.session")


class SessionService:
    """会话管理服务类"""

    def __init__(self, db_path: str = "/config/sessions.db"):
        """初始化会话服务

        Args:
            db_path: 会话数据库路径
        """
        self.db_path = db_path
        # 会话有效期（秒）- 30 天
        self.session_expire = 30 * 24 * 60 * 60

    async def init_db(self):
        """初始化数据库表"""
        # 确保目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            # 检查表是否已存在
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            table_exists = await cursor.fetchone()

            if table_exists:
                # 表已存在，检查是否有 expires_at 列（新版字段）
                cursor = await db.execute("PRAGMA table_info(sessions)")
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]

                # 如果没有 expires_at 列，说明是旧表，需要删除重建
                if 'expires_at' not in column_names:
                    logger.info("检测到旧版会话表，正在迁移...")
                    await db.execute("DROP TABLE IF EXISTS sessions")
                    await db.commit()

            # 创建新表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    is_admin INTEGER NOT NULL DEFAULT 0,
                    server_id TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    last_activity INTEGER NOT NULL
                )
            """)
            await db.commit()

            # 创建索引以提高查询性能
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON sessions(expires_at)
            """)
            await db.commit()

    async def create_session(
        self,
        user_id: str,
        username: str,
        is_admin: bool,
        server_id: str
    ) -> str:
        """创建新会话

        Args:
            user_id: 用户ID
            username: 用户名
            is_admin: 是否是管理员
            server_id: 服务器ID

        Returns:
            session_id: 会话ID
        """
        session_id = secrets.token_urlsafe(32)
        now = int(time.time())
        expires_at = now + self.session_expire

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            await db.execute("""
                INSERT INTO sessions
                (session_id, user_id, username, is_admin, server_id,
                 created_at, expires_at, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, user_id, username,
                1 if is_admin else 0, server_id,
                now, expires_at, now
            ))
            await db.commit()

        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息字典，如果会话不存在或已过期则返回 None
        """
        if not session_id:
            return None

        now = int(time.time())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT session_id, user_id, username, is_admin,
                       server_id, created_at, expires_at, last_activity
                FROM sessions
                WHERE session_id = ? AND expires_at > ?
            """, (session_id, now))

            row = await cursor.fetchone()

            if not row:
                return None

            # 更新最后活动时间
            await db.execute("""
                UPDATE sessions
                SET last_activity = ?
                WHERE session_id = ?
            """, (now, session_id))
            await db.commit()

            return {
                "session_id": row["session_id"],
                "user_id": row["user_id"],
                "username": row["username"],
                "is_admin": bool(row["is_admin"]),
                "server_id": row["server_id"],
                "created_at": row["created_at"],
                "expires_at": row["expires_at"],
                "last_activity": row["last_activity"]
            }

    async def delete_session(self, session_id: str) -> bool:
        """删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功删除
        """
        if not session_id:
            return False

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            cursor = await db.execute("""
                DELETE FROM sessions WHERE session_id = ?
            """, (session_id,))
            await db.commit()

            return cursor.rowcount > 0

    async def clean_expired_sessions(self) -> int:
        """清理过期会话

        Returns:
            清理的会话数量
        """
        now = int(time.time())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            cursor = await db.execute("""
                DELETE FROM sessions WHERE expires_at <= ?
            """, (now,))
            await db.commit()

            return cursor.rowcount

    async def extend_session(self, session_id: str) -> bool:
        """延长会话有效期（续期）

        Args:
            session_id: 会话ID

        Returns:
            是否成功延期
        """
        if not session_id:
            return False

        now = int(time.time())
        new_expires = now + self.session_expire

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            cursor = await db.execute("""
                UPDATE sessions
                SET expires_at = ?, last_activity = ?
                WHERE session_id = ? AND expires_at > ?
            """, (new_expires, now, session_id, now))
            await db.commit()

            return cursor.rowcount > 0

    async def get_all_sessions(self, user_id: Optional[str] = None) -> list[dict]:
        """获取所有活跃会话

        Args:
            user_id: 可选，只获取指定用户的会话

        Returns:
            会话列表
        """
        now = int(time.time())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            db.row_factory = aiosqlite.Row

            if user_id:
                cursor = await db.execute("""
                    SELECT session_id, user_id, username, is_admin,
                           server_id, created_at, expires_at, last_activity
                    FROM sessions
                    WHERE user_id = ? AND expires_at > ?
                    ORDER BY last_activity DESC
                """, (user_id, now))
            else:
                cursor = await db.execute("""
                    SELECT session_id, user_id, username, is_admin,
                           server_id, created_at, expires_at, last_activity
                    FROM sessions
                    WHERE expires_at > ?
                    ORDER BY last_activity DESC
                """, (now,))

            rows = await cursor.fetchall()

            return [
                {
                    "session_id": row["session_id"],
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "is_admin": bool(row["is_admin"]),
                    "server_id": row["server_id"],
                    "created_at": row["created_at"],
                    "expires_at": row["expires_at"],
                    "last_activity": row["last_activity"]
                }
                for row in rows
            ]


# 创建全局实例
session_service = SessionService()
