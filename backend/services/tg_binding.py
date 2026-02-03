"""
Telegram 用户绑定服务
管理 Telegram 用户与 Emby 账户的绑定关系
"""
import aiosqlite
from datetime import datetime
from typing import Optional
from logger import get_logger

logger = get_logger("services.tg_binding")

# 绑定数据库路径
TG_BINDINGS_DB = "/config/tg_bindings.db"


class TgBindingService:
    """Telegram 绑定服务"""

    async def init_db(self):
        """初始化绑定数据库"""
        async with aiosqlite.connect(TG_BINDINGS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            # 检查是否需要迁移旧表
            await self._migrate_if_needed(db)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS tg_bindings (
                    tg_user_id TEXT NOT NULL,
                    tg_username TEXT,
                    tg_first_name TEXT,
                    server_id TEXT NOT NULL,
                    emby_user_id TEXT NOT NULL,
                    emby_username TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    PRIMARY KEY (tg_user_id, server_id)
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tg_bindings_server
                ON tg_bindings(server_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tg_bindings_emby_user
                ON tg_bindings(server_id, emby_user_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tg_bindings_tg_user
                ON tg_bindings(tg_user_id)
            """)
            await db.commit()

    async def _migrate_if_needed(self, db):
        """检查并迁移旧表结构（单主键 -> 复合主键）"""
        try:
            # 检查表是否存在
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tg_bindings'"
            ) as cursor:
                if not await cursor.fetchone():
                    return  # 表不存在，无需迁移

            # 检查表结构，看是否是旧的单主键结构
            async with db.execute("PRAGMA table_info(tg_bindings)") as cursor:
                columns = await cursor.fetchall()
                # 查找 tg_user_id 列的 pk 值
                for col in columns:
                    # col: (cid, name, type, notnull, dflt_value, pk)
                    if col[1] == 'tg_user_id' and col[5] == 1:
                        # 检查 server_id 是否也是主键
                        server_pk = False
                        for c in columns:
                            if c[1] == 'server_id' and c[5] > 0:
                                server_pk = True
                                break
                        if not server_pk:
                            # 需要迁移：旧表只有 tg_user_id 作为主键
                            await self._do_migration(db)
                        break
        except Exception as e:
            logger.error(f"Migration check error: {e}")

    async def _do_migration(self, db):
        """执行表迁移"""
        logger.info("TgBinding: Migrating to multi-server binding support...")
        try:
            # 1. 重命名旧表
            await db.execute("ALTER TABLE tg_bindings RENAME TO tg_bindings_old")

            # 2. 创建新表（复合主键）
            await db.execute("""
                CREATE TABLE tg_bindings (
                    tg_user_id TEXT NOT NULL,
                    tg_username TEXT,
                    tg_first_name TEXT,
                    server_id TEXT NOT NULL,
                    emby_user_id TEXT NOT NULL,
                    emby_username TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    PRIMARY KEY (tg_user_id, server_id)
                )
            """)

            # 3. 迁移数据
            await db.execute("""
                INSERT INTO tg_bindings
                SELECT tg_user_id, tg_username, tg_first_name, server_id,
                       emby_user_id, emby_username, created_at
                FROM tg_bindings_old
            """)

            # 4. 删除旧表
            await db.execute("DROP TABLE tg_bindings_old")

            await db.commit()
            logger.info("TgBinding: Migration completed successfully")
        except Exception as e:
            logger.error(f"TgBinding: Migration failed: {e}")
            raise

    async def get_binding(self, tg_user_id: str, server_id: Optional[str] = None) -> Optional[dict]:
        """获取用户绑定信息（指定服务器或第一个绑定）"""
        async with aiosqlite.connect(TG_BINDINGS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            db.row_factory = aiosqlite.Row
            if server_id:
                # 获取指定服务器的绑定
                async with db.execute(
                    "SELECT * FROM tg_bindings WHERE tg_user_id = ? AND server_id = ?",
                    (str(tg_user_id), server_id)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            else:
                # 获取第一个绑定（兼容旧逻辑）
                async with db.execute(
                    "SELECT * FROM tg_bindings WHERE tg_user_id = ? ORDER BY created_at ASC LIMIT 1",
                    (str(tg_user_id),)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
        return None

    async def get_user_bindings(self, tg_user_id: str) -> list[dict]:
        """获取用户的所有绑定"""
        async with aiosqlite.connect(TG_BINDINGS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tg_bindings WHERE tg_user_id = ? ORDER BY created_at ASC",
                (str(tg_user_id),)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_bound_server_ids(self, tg_user_id: str) -> list[str]:
        """获取用户已绑定的服务器ID列表"""
        async with aiosqlite.connect(TG_BINDINGS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            async with db.execute(
                "SELECT server_id FROM tg_bindings WHERE tg_user_id = ?",
                (str(tg_user_id),)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def create_binding(
        self,
        tg_user_id: str,
        tg_username: str,
        tg_first_name: str,
        server_id: str,
        emby_user_id: str,
        emby_username: str
    ) -> bool:
        """创建绑定关系"""
        try:
            async with aiosqlite.connect(TG_BINDINGS_DB) as db:
                await db.execute("PRAGMA busy_timeout = 30000")
                await db.execute("""
                    INSERT OR REPLACE INTO tg_bindings
                    (tg_user_id, tg_username, tg_first_name, server_id, emby_user_id, emby_username, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(tg_user_id),
                    tg_username or "",
                    tg_first_name or "",
                    server_id,
                    emby_user_id,
                    emby_username,
                    datetime.now().isoformat()
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating binding: {e}")
            return False

    async def delete_binding(self, tg_user_id: str, server_id: Optional[str] = None) -> bool:
        """删除绑定关系（指定服务器或全部）"""
        try:
            async with aiosqlite.connect(TG_BINDINGS_DB) as db:
                await db.execute("PRAGMA busy_timeout = 30000")
                if server_id:
                    # 删除指定服务器的绑定
                    await db.execute(
                        "DELETE FROM tg_bindings WHERE tg_user_id = ? AND server_id = ?",
                        (str(tg_user_id), server_id)
                    )
                else:
                    # 删除所有绑定
                    await db.execute(
                        "DELETE FROM tg_bindings WHERE tg_user_id = ?",
                        (str(tg_user_id),)
                    )
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting binding: {e}")
            return False

    async def get_all_bindings(self, server_id: Optional[str] = None) -> list[dict]:
        """获取所有绑定关系"""
        async with aiosqlite.connect(TG_BINDINGS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            db.row_factory = aiosqlite.Row
            if server_id:
                query = "SELECT * FROM tg_bindings WHERE server_id = ? ORDER BY created_at DESC"
                params = (server_id,)
            else:
                query = "SELECT * FROM tg_bindings ORDER BY created_at DESC"
                params = ()

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def delete_binding_by_admin(self, tg_user_id: str) -> bool:
        """管理员删除绑定"""
        return await self.delete_binding(tg_user_id)

    async def get_binding_count(self, server_id: Optional[str] = None) -> int:
        """获取绑定数量"""
        async with aiosqlite.connect(TG_BINDINGS_DB) as db:
            await db.execute("PRAGMA busy_timeout = 30000")
            if server_id:
                query = "SELECT COUNT(*) FROM tg_bindings WHERE server_id = ?"
                params = (server_id,)
            else:
                query = "SELECT COUNT(*) FROM tg_bindings"
                params = ()

            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0


# 单例实例
tg_binding_service = TgBindingService()
