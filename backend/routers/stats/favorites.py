"""
Favorites statistics router
收藏统计路由模块
"""
from fastapi import APIRouter, Query
from typing import Optional
import httpx

from services.users import user_service
from services.emby import emby_service
from logger import get_logger
from .helpers import get_server_config_from_id

logger = get_logger("favorites")
router = APIRouter(prefix="/api", tags=["stats-favorites"])


def normalize_user_id(uid: str) -> str:
    """标准化用户ID（去除短横线，转小写）"""
    return (uid or "").replace("-", "").lower()


def to_dashed_guid(uid: str) -> str:
    """将无短横线的 GUID 转换为标准格式（带短横线）"""
    raw = normalize_user_id(uid)
    if len(raw) != 32:
        return uid
    return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"


@router.get("/favorites")
async def get_favorites(
    server_id: Optional[str] = Query(default=None, description="服务器ID")
):
    """获取用户收藏统计（使用 Emby API）"""
    server_config = await get_server_config_from_id(server_id)
    user_map = await user_service.get_user_map(server_config)

    emby_url = server_config.get('emby_url') if server_config else None
    if not emby_url:
        return {
            "users_favorites": [],
            "items": [],
            "total_users": 0,
            "users_with_favorites": 0
        }

    api_key = await emby_service.get_api_key(server_config)
    if not api_key:
        return {
            "users_favorites": [],
            "items": [],
            "total_users": 0,
            "users_with_favorites": 0
        }

    user_favorites_dict = {}
    items_dict = {}

    # 优先从 Emby 获取真实用户列表（避免 users.db 缺失或 UserId 格式不匹配导致全空）
    users: list[tuple[str, str]] = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{emby_url}/emby/Users",
                params={"api_key": api_key},
                timeout=10,
            )
            if resp.status_code == 200:
                for u in resp.json() or []:
                    uid = u.get("Id")
                    name = u.get("Name") or "Unknown"
                    if uid:
                        users.append((uid, name))
    except Exception as e:
        logger.error(f"Error fetching users list: {e}")

    if not users:
        users = list(user_map.items())

    permission_denied = False

    async with httpx.AsyncClient() as client:
        # 遍历所有用户，获取每个用户的收藏
        for user_id_raw, username_raw in users:
            user_id = user_id_raw
            username = user_map.get(normalize_user_id(user_id_raw), username_raw)
            try:
                resp = await client.get(
                    f"{emby_url}/emby/Users/{user_id}/Items",
                    params={
                        "api_key": api_key,
                        "Filters": "IsFavorite",
                        "Recursive": "true",
                        "Fields": "ProductionYear,SeriesInfo,ImageTags,SeriesPrimaryImageTag,SeriesId,SeriesName",
                    },
                    timeout=15,
                )

                if resp.status_code in (401, 403):
                    permission_denied = True
                    continue

                # 兼容部分环境 UserId 带/不带短横线导致的 404
                if resp.status_code == 404:
                    alt_user_id = to_dashed_guid(user_id) if "-" not in (user_id or "") else normalize_user_id(user_id)
                    if alt_user_id and alt_user_id != user_id:
                        resp = await client.get(
                            f"{emby_url}/emby/Users/{alt_user_id}/Items",
                            params={
                                "api_key": api_key,
                                "Filters": "IsFavorite",
                                "Recursive": "true",
                                "Fields": "ProductionYear,SeriesInfo,ImageTags,SeriesPrimaryImageTag,SeriesId,SeriesName",
                            },
                            timeout=15,
                        )
                        if resp.status_code == 200:
                            user_id = alt_user_id

                if resp.status_code != 200:
                    continue

                data = resp.json() or {}
                items = data.get("Items", []) or []
                if not items:
                    continue

                # 添加到用户收藏字典
                user_favorites_dict[user_id] = {
                    "user_id": user_id,
                    "username": username,
                    "favorites": [],
                }

                for item in items:
                    item_id = item.get("Id", "")
                    item_name = item.get("Name", "Unknown")
                    item_type = item.get("Type", "Unknown")
                    production_year = item.get("ProductionYear")
                    series_id = item.get("SeriesId")
                    if not series_id:
                        series_info = item.get("SeriesInfo") or {}
                        if isinstance(series_info, dict):
                            series_id = series_info.get("Id") or series_info.get("SeriesId")
                    series_name = item.get("SeriesName")
                    has_poster = bool((item.get("ImageTags") or {}).get("Primary") or series_id)

                    favorite_item = {
                        "item_id": item_id,
                        "name": item_name,
                        "type": item_type,
                        "year": production_year,
                        "has_poster": has_poster,
                        "series_id": series_id,
                        "series_name": series_name,
                    }
                    user_favorites_dict[user_id]["favorites"].append(favorite_item)

                    # 统计每个内容的收藏次数
                    if item_id not in items_dict:
                        items_dict[item_id] = {
                            "item_id": item_id,
                            "name": item_name,
                            "type": item_type,
                            "favorite_count": 0,
                            "has_poster": has_poster,
                            "series_id": series_id,
                            "users": [],
                        }
                    items_dict[item_id]["favorite_count"] += 1
                    items_dict[item_id]["users"].append({
                        "user_id": user_id,
                        "username": username,
                    })

            except Exception as e:
                logger.error(f"Error fetching favorites for user {user_id_raw}: {e}")
                continue

    # 转换为列表
    users_favorites = list(user_favorites_dict.values())
    items = sorted(items_dict.values(), key=lambda x: x["favorite_count"], reverse=True)

    # 统计数据
    total_users = len(users)
    users_with_favorites = len(user_favorites_dict)

    resp_data = {
        "users_favorites": users_favorites,
        "items": items,
        "total_users": total_users,
        "users_with_favorites": users_with_favorites
    }
    if permission_denied and users_with_favorites == 0:
        resp_data["warning"] = "当前 API Key 可能没有管理员权限，无法读取其他用户收藏；请在服务器配置中填写管理员 API Key。"
    return resp_data
