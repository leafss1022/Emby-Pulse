"""
Filters router
筛选选项路由模块
"""
from fastapi import APIRouter, Query
from typing import Optional

from database import get_playback_db
from services.users import user_service
from name_mappings import name_mapping_service
from .helpers import get_server_config_from_id

router = APIRouter(prefix="/api", tags=["stats-filters"])


@router.get("/filter-options")
async def get_filter_options(
    server_id: Optional[str] = Query(default=None, description="服务器ID")
):
    """获取所有可用的筛选选项"""
    server_config = await get_server_config_from_id(server_id)
    user_map = await user_service.get_user_map(server_config)

    async with get_playback_db(server_config) as db:
        # 获取所有用户
        async with db.execute("""
            SELECT DISTINCT UserId FROM PlaybackActivity WHERE UserId IS NOT NULL
        """) as cursor:
            user_ids = []
            async for row in cursor:
                user_id = row[0]
                if user_id:
                    username = user_service.match_username(user_id, user_map)
                    user_ids.append({"id": user_id, "name": username})

        # 获取所有客户端（返回原始名称和映射后名称）
        async with db.execute("""
            SELECT DISTINCT ClientName FROM PlaybackActivity WHERE ClientName IS NOT NULL ORDER BY ClientName
        """) as cursor:
            clients = []
            seen_mapped = set()
            for row in await cursor.fetchall():
                if row[0]:
                    original = row[0]
                    mapped = name_mapping_service.map_client_name(original)
                    # 去重：如果映射后名称已存在则跳过
                    if mapped not in seen_mapped:
                        clients.append({
                            "original": original,
                            "display": mapped
                        })
                        seen_mapped.add(mapped)

        # 获取所有设备（返回原始名称和映射后名称）
        async with db.execute("""
            SELECT DISTINCT DeviceName FROM PlaybackActivity WHERE DeviceName IS NOT NULL ORDER BY DeviceName
        """) as cursor:
            devices = []
            seen_mapped = set()
            for row in await cursor.fetchall():
                if row[0]:
                    original = row[0]
                    mapped = name_mapping_service.map_device_name(original)
                    # 去重：如果映射后名称已存在则跳过
                    if mapped not in seen_mapped:
                        devices.append({
                            "original": original,
                            "display": mapped
                        })
                        seen_mapped.add(mapped)

        # 获取所有媒体类型
        async with db.execute("""
            SELECT DISTINCT ItemType FROM PlaybackActivity WHERE ItemType IS NOT NULL ORDER BY ItemType
        """) as cursor:
            item_types = [row[0] for row in await cursor.fetchall() if row[0]]

        # 获取所有播放方式
        async with db.execute("""
            SELECT DISTINCT PlaybackMethod FROM PlaybackActivity WHERE PlaybackMethod IS NOT NULL ORDER BY PlaybackMethod
        """) as cursor:
            playback_methods = [row[0] for row in await cursor.fetchall() if row[0]]

        # 获取日期范围
        async with db.execute("""
            SELECT MIN(date(DateCreated)), MAX(date(DateCreated)) FROM PlaybackActivity
        """) as cursor:
            row = await cursor.fetchone()
            date_range = {
                "min": row[0] if row else None,
                "max": row[1] if row else None
            }

    return {
        "users": user_ids,
        "clients": clients,
        "devices": devices,
        "item_types": item_types,
        "playback_methods": playback_methods,
        "date_range": date_range
    }
