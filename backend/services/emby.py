"""
Emby API 服务模块
处理与 Emby 服务器的所有交互
"""
import httpx
import aiosqlite
from typing import Optional, Dict, List
from cachetools import TTLCache
from config import settings
from logger import get_logger

logger = get_logger("services.emby")

# 缓存配置常量
CACHE_TTL_SECONDS = 3600  # 缓存生存时间: 1小时
API_KEY_CACHE_TTL = 7200  # API Key 缓存: 2小时


class EmbyService:
    """Emby 服务类，管理与 Emby 服务器的交互"""

    def __init__(self):
        # 使用 TTLCache 替代手动管理的字典缓存
        # TTLCache 自动处理过期和大小限制
        self._api_key_cache: TTLCache = TTLCache(maxsize=50, ttl=API_KEY_CACHE_TTL)
        self._user_id_cache: TTLCache = TTLCache(maxsize=50, ttl=API_KEY_CACHE_TTL)
        self._item_info_cache: TTLCache = TTLCache(
            maxsize=settings.ITEM_CACHE_MAX_SIZE,
            ttl=CACHE_TTL_SECONDS
        )

    async def _is_admin_api_key(self, api_key: str, server_config: Optional[dict] = None) -> bool:
        """检查 api_key 对应用户是否为管理员（用于选择更稳定的 Token）"""
        if not api_key:
            return False

        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Users/Me",
                    params={"api_key": api_key},
                    timeout=10,
                )
                if resp.status_code == 200:
                    me = resp.json() or {}
                    return bool((me.get("Policy") or {}).get("IsAdministrator"))
                # 401/403是正常的（token无效或非管理员），不记录日志
                # 500是Emby服务器内部错误（可能是旧token格式问题），使用debug级别
                elif resp.status_code >= 500:
                    logger.debug(f"Emby server error when verifying token: {resp.status_code}")
                return False
        except Exception as e:
            logger.debug(f"Token verification failed: {e}")
            return False

    async def get_api_key(self, server_config: Optional[dict] = None) -> str:
        """获取 Emby API Key"""
        # 如果提供了 server_config，使用它
        if server_config:
            # 优先使用配置中的 API Key
            if server_config.get('emby_api_key'):
                return server_config['emby_api_key']

            # 从缓存获取
            server_id = server_config.get('id', 'default')
            if server_id in self._api_key_cache:
                return self._api_key_cache[server_id]

            # 从数据库获取
            try:
                auth_db = server_config.get('auth_db', settings.AUTH_DB)
                async with aiosqlite.connect(auth_db) as db:
                    # 设置 busy_timeout，避免多服务器环境下的锁死问题
                    await db.execute("PRAGMA busy_timeout = 30000")
                    async with db.execute(
                        "SELECT AccessToken FROM Tokens_2 WHERE IsActive=1 ORDER BY DateLastActivityInt DESC LIMIT 10"
                    ) as cursor:
                        tokens: list[str] = []
                        async for row in cursor:
                            if row and row[0]:
                                tokens.append(row[0])

                        # 优先选择管理员 Token，避免部分接口（如收藏统计）因权限不足返回空
                        for token in tokens:
                            if await self._is_admin_api_key(token, server_config):
                                self._api_key_cache[server_id] = token
                                return token

                        if tokens:
                            self._api_key_cache[server_id] = tokens[0]
                            return tokens[0]
            except Exception as e:
                logger.error(f"Error getting API key from {auth_db}: {e}")
        else:
            # 使用默认配置（向后兼容）
            if settings.EMBY_API_KEY:
                return settings.EMBY_API_KEY

            if 'default' in self._api_key_cache:
                return self._api_key_cache['default']

            try:
                async with aiosqlite.connect(settings.AUTH_DB) as db:
                    # 设置 busy_timeout，避免多服务器环境下的锁死问题
                    await db.execute("PRAGMA busy_timeout = 30000")
                    async with db.execute(
                        "SELECT AccessToken FROM Tokens_2 WHERE IsActive=1 ORDER BY DateLastActivityInt DESC LIMIT 10"
                    ) as cursor:
                        tokens: list[str] = []
                        async for row in cursor:
                            if row and row[0]:
                                tokens.append(row[0])

                        for token in tokens:
                            if await self._is_admin_api_key(token, None):
                                self._api_key_cache['default'] = token
                                return token

                        if tokens:
                            self._api_key_cache['default'] = tokens[0]
                            return tokens[0]
            except Exception as e:
                logger.error(f"Error getting API key: {e}")
        return ""

    async def get_user_id(self, server_config: Optional[dict] = None) -> str:
        """获取一个 Emby 用户 ID 用于 API 调用"""
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL
        server_id = server_config.get('id', 'default') if server_config else 'default'

        if server_id in self._user_id_cache:
            return self._user_id_cache[server_id]

        try:
            api_key = await self.get_api_key(server_config)
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Users",
                    params={"api_key": api_key},
                    timeout=10
                )
                if resp.status_code == 200:
                    users = resp.json()
                    if users:
                        # 优先选择管理员账号，避免因权限导致部分条目查询不到（从而出现海报缺失）
                        admin_user = next(
                            (u for u in users if u.get("Policy", {}).get("IsAdministrator")),
                            None,
                        )
                        chosen = admin_user or users[0]
                        self._user_id_cache[server_id] = chosen["Id"]
                        return self._user_id_cache[server_id]
                else:
                    logger.error(f"Failed to get Emby users: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
        return ""

    async def search_item_by_name(self, name: str, item_type: str, server_config: Optional[dict] = None) -> Optional[str]:
        """
        通过名称在 Emby 中搜索媒体项，返回最匹配的 item_id
        用于处理洗版后 ID 变化的情况
        """
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            user_id = await self.get_user_id(server_config)
            if not api_key or not user_id:
                return None

            # 对于剧集，提取剧名（去掉"剧名 - S01E01"中的集数部分）
            search_name = name.split(" - ")[0] if item_type == "Episode" and " - " in name else name

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Users/{user_id}/Items",
                    params={
                        "api_key": api_key,
                        "searchTerm": search_name,
                        "Recursive": True,
                        "IncludeItemTypes": item_type,
                        "Fields": "ProductionYear,ProviderIds",
                        "Limit": 10
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    results = resp.json().get("Items", [])
                    if results:
                        # 优先精确匹配名称
                        for item in results:
                            if item.get("Name") == search_name:
                                return item.get("Id")
                        # 如果没有精确匹配，返回第一个结果
                        return results[0].get("Id")
                else:
                    logger.warning(f"Failed to search item '{name}': {resp.status_code}")
        except Exception as e:
            logger.error(f"Error searching item by name '{name}': {e}")
        return None

    async def get_item_info(self, item_id: str, server_config: Optional[dict] = None) -> dict:
        """获取媒体项目信息（包含海报等）"""
        cache_key = f"{server_config.get('id', 'default') if server_config else 'default'}:{item_id}"
        if cache_key in self._item_info_cache:
            return self._item_info_cache[cache_key]

        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            user_id = await self.get_user_id(server_config)
            if not api_key or not user_id:
                return {}

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Users/{user_id}/Items/{item_id}",
                    params={
                        "api_key": api_key,
                        "Fields": "SeriesInfo,ImageTags,SeriesPrimaryImageTag,PrimaryImageAspectRatio,Overview,BackdropImageTags,ParentId"
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    info = resp.json()
                    self._item_info_cache[cache_key] = info
                    return info
                else:
                    logger.warning(f"Failed to get item info for {item_id}: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error getting item info for {item_id}: {e}")
        return {}

    async def get_items_info_batch(self, item_ids: List[str], server_config: Optional[dict] = None) -> Dict[str, dict]:
        """
        批量获取多个媒体项目信息,避免N+1查询问题

        Args:
            item_ids: item ID列表
            server_config: 服务器配置

        Returns:
            字典: {item_id: item_info}
        """
        if not item_ids:
            return {}

        # 过滤掉已缓存的item_id
        server_id = server_config.get('id', 'default') if server_config else 'default'
        result = {}
        uncached_ids = []

        for item_id in item_ids:
            cache_key = f"{server_id}:{item_id}"
            if cache_key in self._item_info_cache:
                result[item_id] = self._item_info_cache[cache_key]
            else:
                uncached_ids.append(item_id)

        # 如果所有都已缓存,直接返回
        if not uncached_ids:
            return result

        # 批量查询未缓存的item
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL
        api_key = await self.get_api_key(server_config)
        user_id = await self.get_user_id(server_config)

        if not api_key or not user_id:
            # 如果没有API key,返回已缓存的结果
            return result

        try:
            # Emby API支持通过Ids参数批量查询
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Users/{user_id}/Items",
                    params={
                        "api_key": api_key,
                        "Ids": ",".join(uncached_ids),
                        "Fields": "SeriesInfo,ImageTags,SeriesPrimaryImageTag,PrimaryImageAspectRatio,Overview,BackdropImageTags,ParentId,SeriesId"
                    },
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("Items", [])

                    # 更新缓存和结果
                    for item in items:
                        item_id = item.get("Id")
                        if item_id:
                            cache_key = f"{server_id}:{item_id}"
                            self._item_info_cache[cache_key] = item
                            result[item_id] = item

                    # 对于未返回的item_id,返回空字典
                    for item_id in uncached_ids:
                        if item_id not in result:
                            result[item_id] = {}
                            cache_key = f"{server_id}:{item_id}"
                            self._item_info_cache[cache_key] = {}
                else:
                    logger.warning(f"Failed to batch get items info: {resp.status_code}")
                    # 失败时,为未缓存的ID返回空字典
                    for item_id in uncached_ids:
                        result[item_id] = {}
        except Exception as e:
            logger.error(f"Error batch getting items info: {e}")
            # 异常时,为未缓存的ID返回空字典
            for item_id in uncached_ids:
                result[item_id] = {}

        return result

    async def _get_image(
        self,
        item_id: str,
        image_type: str,
        max_height: int,
        max_width: int,
        server_config: Optional[dict] = None,
    ) -> tuple[bytes, str]:
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        api_key = await self.get_api_key(server_config)
        if not api_key:
            return b"", "image/jpeg"

        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(
                f"{emby_url}/emby/Items/{item_id}/Images/{image_type}",
                params={
                    "api_key": api_key,
                    "maxHeight": max_height,
                    "maxWidth": max_width,
                    "quality": 90,
                },
                timeout=15,
            )
            if resp.status_code == 200 and resp.content:
                return resp.content, resp.headers.get("content-type", "image/jpeg")
        return b"", "image/jpeg"

    async def get_poster(self, item_id: str, max_height: int = 300, max_width: int = 200, server_config: Optional[dict] = None) -> tuple[bytes, str]:
        """获取海报图片，返回 (图片数据, content_type)"""
        try:
            # 有些条目 Emby 没有 Primary，但有 Thumb/继承图；这里做兜底
            content, content_type = await self._get_image(item_id, "Primary", max_height, max_width, server_config)
            if content:
                return content, content_type
            return await self._get_image(item_id, "Thumb", max_height, max_width, server_config)
        except Exception as e:
            logger.error(f"Error fetching poster for {item_id}: {e}")

        return b"", "image/jpeg"

    async def get_backdrop(self, item_id: str, max_height: int = 720, max_width: int = 1280, server_config: Optional[dict] = None) -> tuple[bytes, str]:
        """获取背景图(横版)，返回 (图片数据, content_type)"""
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            if not api_key:
                return b"", "image/jpeg"

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Items/{item_id}/Images/Backdrop",
                    params={
                        "api_key": api_key,
                        "maxHeight": max_height,
                        "maxWidth": max_width,
                        "quality": 90
                    },
                    timeout=15
                )
                if resp.status_code == 200:
                    return resp.content, resp.headers.get("content-type", "image/jpeg")
        except Exception as e:
            logger.error(f"Error fetching backdrop for {item_id}: {e}")

        return b"", "image/jpeg"

    def get_poster_url(self, item_id: str, item_type: str, item_info: dict, server_id: str = None) -> str | None:
        """根据媒体信息获取海报 URL"""
        if item_info is None:
            return None

        server_param = f"?server_id={server_id}" if server_id else ""
        image_tags = item_info.get("ImageTags") or {}

        # Emby 返回里 SeriesId 有时会出现在顶层，也可能嵌在 SeriesInfo 里（不同版本/字段组合）
        series_id = item_info.get("SeriesId")
        if not series_id:
            series_info = item_info.get("SeriesInfo") or {}
            if isinstance(series_info, dict):
                series_id = series_info.get("Id") or series_info.get("SeriesId")

        # 对于剧集：优先使用 SeriesId（更稳定，避免单集缺图导致热门内容海报缺失）
        if item_type == "Episode":
            poster_item_id = series_id or item_info.get("ParentId") or item_id
            return f"/api/poster/{poster_item_id}{server_param}"

        # 其他类型：如果自身没有 Primary/Thumb，但能关联到剧集/剧集条目，则回退到 SeriesId
        has_own_image = bool(image_tags.get("Primary") or image_tags.get("Thumb"))
        if not has_own_image and series_id:
            return f"/api/poster/{series_id}{server_param}"

        return f"/api/poster/{item_id}{server_param}"

    def get_backdrop_url(self, item_id: str, item_type: str, item_info: dict, server_id: str = None) -> str | None:
        """根据媒体信息获取背景图(横版) URL"""
        if item_info is None:
            return None

        server_param = f"?server_id={server_id}" if server_id else ""
        # 对于剧集，使用剧集背景图
        if item_type == "Episode" and item_info.get("SeriesId"):
            return f"/api/backdrop/{item_info['SeriesId']}{server_param}"
        # 检查是否有 Backdrop 图片
        elif item_info.get("BackdropImageTags") and len(item_info.get("BackdropImageTags", [])) > 0:
            return f"/api/backdrop/{item_id}{server_param}"

        return None

    async def get_now_playing(self, server_config: Optional[dict] = None) -> list[dict]:
        """获取当前正在播放的会话"""
        emby_url = server_config.get('emby_url', settings.EMBY_URL) if server_config else settings.EMBY_URL

        try:
            api_key = await self.get_api_key(server_config)
            if not api_key:
                return []

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{emby_url}/emby/Sessions",
                    params={"api_key": api_key},
                    timeout=10
                )
                if resp.status_code == 200:
                    sessions = resp.json()
                    playing = []
                    for session in sessions:
                        # 只返回正在播放的会话
                        if session.get("NowPlayingItem"):
                            playing.append(session)
                    return playing
                else:
                    logger.error(f"Failed to get now playing sessions: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error getting now playing: {e}")
        return []

    async def authenticate_user(self, username: str, password: str) -> dict | None:
        """
        使用 Emby API 验证用户登录
        返回用户信息 dict 或 None（验证失败）
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.EMBY_URL}/emby/Users/AuthenticateByName",
                    headers={
                        "X-Emby-Authorization": 'MediaBrowser Client="Emby Stats", Device="Web", DeviceId="emby-stats", Version="1.0.0"',
                        "Content-Type": "application/json"
                    },
                    json={
                        "Username": username,
                        "Pw": password
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "user_id": data.get("User", {}).get("Id"),
                        "username": data.get("User", {}).get("Name"),
                        "access_token": data.get("AccessToken"),
                        "is_admin": data.get("User", {}).get("Policy", {}).get("IsAdministrator", False)
                    }
                else:
                    logger.warning(f"Authentication failed for user '{username}': {resp.status_code}")
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
        return None


# 单例实例
emby_service = EmbyService()
