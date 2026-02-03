"""
数据库连接池管理模块
为每个数据库文件维护独立的连接池，提高并发性能
"""
import asyncio
import aiosqlite
from typing import Dict, Optional
from contextlib import asynccontextmanager
from logger import get_logger

logger = get_logger("db_pool")


class DatabasePool:
    """数据库连接池类"""

    def __init__(self, db_path: str, pool_size: int = 5):
        """
        初始化连接池

        Args:
            db_path: 数据库文件路径
            pool_size: 连接池大小（默认5个连接）
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
        self._initialized = False
        self._lock = asyncio.Lock()
        logger.info(f"[DBPool] Creating pool for {db_path} (size: {pool_size})")

    async def initialize(self):
        """初始化连接池，预创建所有连接"""
        async with self._lock:
            if self._initialized:
                return

            logger.info(f"[DBPool] Initializing pool for {self.db_path}")
            for i in range(self.pool_size):
                try:
                    conn = await aiosqlite.connect(self.db_path)
                    # 设置行工厂模式，返回字典格式
                    conn.row_factory = aiosqlite.Row
                    # 设置 busy_timeout，遇到锁时等待最多 30 秒
                    await conn.execute("PRAGMA busy_timeout = 30000")
                    await self._pool.put(conn)
                    logger.debug(f"[DBPool] Created connection {i+1}/{self.pool_size} for {self.db_path}")
                except Exception as e:
                    logger.error(f"[DBPool] Failed to create connection for {self.db_path}: {e}")
                    raise

            self._initialized = True
            logger.info(f"[DBPool] Pool initialized for {self.db_path}")

    async def acquire(self, timeout: float = 10.0) -> aiosqlite.Connection:
        """
        从连接池获取一个连接

        Args:
            timeout: 获取超时时间（秒）

        Returns:
            数据库连接对象

        Raises:
            asyncio.TimeoutError: 获取连接超时
        """
        if not self._initialized:
            await self.initialize()

        try:
            conn = await asyncio.wait_for(self._pool.get(), timeout=timeout)
            logger.debug(f"[DBPool] Acquired connection for {self.db_path}")

            # 健康检查：测试连接是否有效
            try:
                await conn.execute("SELECT 1")
            except Exception as e:
                logger.warning(f"[DBPool] Connection unhealthy, recreating: {e}")
                try:
                    await conn.close()
                except:
                    pass
                conn = await aiosqlite.connect(self.db_path)
                conn.row_factory = aiosqlite.Row
                await conn.execute("PRAGMA busy_timeout = 30000")

            return conn
        except asyncio.TimeoutError:
            logger.error(f"[DBPool] Acquire timeout for {self.db_path}")
            raise

    async def release(self, conn: aiosqlite.Connection):
        """
        将连接归还到连接池

        Args:
            conn: 数据库连接对象
        """
        try:
            await self._pool.put(conn)
            logger.debug(f"[DBPool] Released connection for {self.db_path}")
        except Exception as e:
            logger.error(f"[DBPool] Failed to release connection for {self.db_path}: {e}")

    @asynccontextmanager
    async def connection(self):
        """
        上下文管理器，自动获取和释放连接

        Usage:
            async with pool.connection() as conn:
                await conn.execute("SELECT * FROM table")
        """
        conn = await self.acquire()
        try:
            yield conn
        finally:
            await self.release(conn)

    async def close_all(self):
        """关闭连接池中的所有连接"""
        logger.info(f"[DBPool] Closing pool for {self.db_path}")
        closed_count = 0

        while not self._pool.empty():
            try:
                conn = await asyncio.wait_for(self._pool.get(), timeout=1.0)
                await conn.close()
                closed_count += 1
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"[DBPool] Error closing connection: {e}")

        logger.info(f"[DBPool] Closed {closed_count} connections for {self.db_path}")
        self._initialized = False


class DatabasePoolManager:
    """数据库连接池管理器，管理多个数据库的连接池"""

    def __init__(self):
        self._pools: Dict[str, DatabasePool] = {}
        self._lock = asyncio.Lock()
        logger.info("[DBPoolManager] Initialized")

    async def get_pool(self, db_path: str, pool_size: int = 5) -> DatabasePool:
        """
        获取指定数据库的连接池，如果不存在则创建

        Args:
            db_path: 数据库文件路径
            pool_size: 连接池大小

        Returns:
            连接池对象
        """
        if db_path in self._pools:
            return self._pools[db_path]

        async with self._lock:
            # 双重检查，避免重复创建
            if db_path in self._pools:
                return self._pools[db_path]

            pool = DatabasePool(db_path, pool_size)
            await pool.initialize()
            self._pools[db_path] = pool
            logger.info(f"[DBPoolManager] Created new pool for {db_path}")
            return pool

    @asynccontextmanager
    async def connection(self, db_path: str, pool_size: int = 5):
        """
        获取数据库连接的上下文管理器

        Usage:
            async with pool_manager.connection("/path/to/db.sqlite") as conn:
                await conn.execute("SELECT * FROM table")
        """
        pool = await self.get_pool(db_path, pool_size)
        async with pool.connection() as conn:
            yield conn

    async def close_all(self):
        """关闭所有连接池"""
        logger.info("[DBPoolManager] Closing all pools")
        for db_path, pool in self._pools.items():
            await pool.close_all()
        self._pools.clear()
        logger.info("[DBPoolManager] All pools closed")


# 全局连接池管理器实例
pool_manager = DatabasePoolManager()
