"""
服务器管理服务模块
处理多服务器配置和管理
"""
import json
import os
import aiosqlite
from typing import Optional, List, Dict
from config import settings

SERVERS_DB = "/config/servers.db"


class ServerService:
    """服务器管理服务类"""

    def __init__(self):
        self._servers_cache: Optional[List[Dict]] = None

    async def init_servers_table(self):
        """初始化服务器配置表"""
        async with aiosqlite.connect(SERVERS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    emby_url TEXT NOT NULL,
                    emby_api_key TEXT,
                    playback_db TEXT NOT NULL,
                    users_db TEXT NOT NULL,
                    auth_db TEXT NOT NULL,
                    is_default INTEGER DEFAULT 0,
                    created_at REAL DEFAULT (unixepoch()),
                    updated_at REAL DEFAULT (unixepoch())
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_servers_default ON servers(is_default)
            """)
            await db.commit()

    async def get_all_servers(self) -> List[Dict]:
        """获取所有服务器配置"""
        if self._servers_cache:
            return self._servers_cache

        await self.init_servers_table()
        async with aiosqlite.connect(SERVERS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT id, name, emby_url, emby_api_key, playback_db, users_db, auth_db, is_default
                FROM servers
                ORDER BY is_default DESC, created_at ASC
            """) as cursor:
                servers = []
                async for row in cursor:
                    servers.append({
                        "id": row["id"],
                        "name": row["name"],
                        "emby_url": row["emby_url"],
                        "emby_api_key": row["emby_api_key"] or "",
                        "playback_db": row["playback_db"],
                        "users_db": row["users_db"],
                        "auth_db": row["auth_db"],
                        "is_default": bool(row["is_default"])
                    })
                self._servers_cache = servers
                return servers

    async def get_server(self, server_id: str) -> Optional[Dict]:
        """获取指定服务器配置"""
        servers = await self.get_all_servers()
        for server in servers:
            if server["id"] == server_id:
                return server
        return None

    async def get_default_server(self) -> Optional[Dict]:
        """获取默认服务器"""
        servers = await self.get_all_servers()
        for server in servers:
            if server["is_default"]:
                return server
        # 如果没有默认服务器，返回第一个
        return servers[0] if servers else None

    async def add_server(
        self,
        name: str,
        emby_url: str,
        playback_db: str,
        users_db: str,
        auth_db: str,
        emby_api_key: Optional[str] = None,
        is_default: bool = False
    ) -> str:
        """添加新服务器"""
        import uuid
        server_id = str(uuid.uuid4())

        await self.init_servers_table()

        # 如果设置为默认，先取消其他默认服务器
        if is_default:
            async with aiosqlite.connect(SERVERS_DB) as db:
                await db.execute("PRAGMA busy_timeout = 30000")
                await db.execute("UPDATE servers SET is_default = 0")
                await db.commit()

        async with aiosqlite.connect(SERVERS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            await db.execute("""
                INSERT INTO servers (id, name, emby_url, emby_api_key, playback_db, users_db, auth_db, is_default, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, unixepoch())
            """, (server_id, name, emby_url, emby_api_key, playback_db, users_db, auth_db, 1 if is_default else 0))
            await db.commit()

        # 清除缓存
        self._servers_cache = None
        return server_id

    async def update_server(
        self,
        server_id: str,
        name: Optional[str] = None,
        emby_url: Optional[str] = None,
        emby_api_key: Optional[str] = None,
        playback_db: Optional[str] = None,
        users_db: Optional[str] = None,
        auth_db: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> bool:
        """更新服务器配置"""
        await self.init_servers_table()

        # 如果设置为默认，先取消其他默认服务器
        if is_default:
            async with aiosqlite.connect(SERVERS_DB) as db:
                await db.execute("PRAGMA busy_timeout = 30000")
                await db.execute("UPDATE servers SET is_default = 0")
                await db.commit()

        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if emby_url is not None:
            updates.append("emby_url = ?")
            params.append(emby_url)
        if emby_api_key is not None:
            updates.append("emby_api_key = ?")
            params.append(emby_api_key)
        if playback_db is not None:
            updates.append("playback_db = ?")
            params.append(playback_db)
        if users_db is not None:
            updates.append("users_db = ?")
            params.append(users_db)
        if auth_db is not None:
            updates.append("auth_db = ?")
            params.append(auth_db)
        if is_default is not None:
            updates.append("is_default = ?")
            params.append(1 if is_default else 0)

        if not updates:
            return False

        updates.append("updated_at = unixepoch()")
        params.append(server_id)

        async with aiosqlite.connect(SERVERS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            await db.execute(
                f"UPDATE servers SET {', '.join(updates)} WHERE id = ?",
                params
            )
            await db.commit()

        # 清除缓存
        self._servers_cache = None
        return True

    async def delete_server(self, server_id: str) -> bool:
        """删除服务器"""
        await self.init_servers_table()
        async with aiosqlite.connect(SERVERS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            cursor = await db.execute("DELETE FROM servers WHERE id = ?", (server_id,))
            await db.commit()
            deleted = cursor.rowcount > 0

        # 清除缓存
        self._servers_cache = None
        return deleted

    async def migrate_legacy_config(self):
        """迁移旧版单服务器配置到新系统

        如果没有服务器配置，且环境变量中配置了数据库路径，
        则自动创建默认服务器
        """
        servers = await self.get_all_servers()
        if servers:
            # 已经有服务器配置，不需要迁移
            return

        # 从环境变量创建默认服务器
        # 只要配置了数据库路径就创建（EMBY_URL 可以是任何值）
        if not settings.PLAYBACK_DB or not settings.USERS_DB or not settings.AUTH_DB:
            return

        # 检查数据库文件是否存在
        import os
        if not os.path.exists(settings.PLAYBACK_DB):
            return

        # 创建默认服务器
        await self.add_server(
            name="默认服务器",
            emby_url=settings.EMBY_URL,
            emby_api_key=settings.EMBY_API_KEY or "",
            playback_db=settings.PLAYBACK_DB,
            users_db=settings.USERS_DB,
            auth_db=settings.AUTH_DB,
            is_default=True
        )

    def invalidate_cache(self):
        """清除缓存"""
        self._servers_cache = None


# 单例实例
server_service = ServerService()


