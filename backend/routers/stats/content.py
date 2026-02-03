"""
Content statistics router
内容统计路由模块（客户端、设备、播放方式）
"""
from fastapi import APIRouter, Query
from typing import Optional

from database import (
    get_playback_db,
    get_count_expr,
    local_date,
)
from utils.query_parser import FilterParams, build_filter_conditions
from name_mappings import name_mapping_service
from .helpers import get_server_config_from_id

router = APIRouter(prefix="/api", tags=["stats-content"])


@router.get("/clients")
async def get_client_stats(
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
    days: int = Query(default=30, ge=1, le=365),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    users: Optional[str] = Query(default=None),
    clients: Optional[str] = Query(default=None),
    devices: Optional[str] = Query(default=None),
    item_types: Optional[str] = Query(default=None),
    playback_methods: Optional[str] = Query(default=None),
):
    """获取客户端统计"""
    server_config = await get_server_config_from_id(server_id)

    # 解析参数
    filter_params = FilterParams(users, clients, devices, item_types, playback_methods)

    where_clause, params = build_filter_conditions(
        days=days if not (start_date or end_date) else None,
        start_date=start_date,
        end_date=end_date,
        local_date_func=local_date,
        name_mapping_service=name_mapping_service,
        **filter_params.to_dict(),
    )

    count_expr = get_count_expr()

    async with get_playback_db(server_config) as db:
        async with db.execute(f"""
            SELECT
                ClientName,
                {count_expr} as play_count,
                COALESCE(SUM(PlayDuration), 0) as total_duration
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY ClientName
            ORDER BY play_count DESC
        """, params) as cursor:
            # 使用字典合并同名映射后的客户端
            merged_data = {}
            async for row in cursor:
                original_name = row[0] or "Unknown"
                mapped_name = name_mapping_service.map_client_name(original_name)
                play_count = int(row[1] or 0)
                duration = row[2]

                if mapped_name in merged_data:
                    merged_data[mapped_name]["play_count"] += play_count
                    merged_data[mapped_name]["duration"] += duration
                else:
                    merged_data[mapped_name] = {
                        "play_count": play_count,
                        "duration": duration
                    }

            # 转换为列表并按播放次数排序
            data = [
                {
                    "client": name,
                    "play_count": info["play_count"],
                    "duration_hours": round(info["duration"] / 3600, 2)
                }
                for name, info in sorted(
                    merged_data.items(),
                    key=lambda x: x[1]["play_count"],
                    reverse=True
                )
            ]

    return {"clients": data}


@router.get("/devices")
async def get_device_stats(
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
    days: int = Query(default=30, ge=1, le=365),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    users: Optional[str] = Query(default=None),
    clients: Optional[str] = Query(default=None),
    devices: Optional[str] = Query(default=None),
    item_types: Optional[str] = Query(default=None),
    playback_methods: Optional[str] = Query(default=None),
):
    """获取设备统计"""
    server_config = await get_server_config_from_id(server_id)

    # 解析参数
    filter_params = FilterParams(users, clients, devices, item_types, playback_methods)

    where_clause, params = build_filter_conditions(
        days=days if not (start_date or end_date) else None,
        start_date=start_date,
        end_date=end_date,
        local_date_func=local_date,
        name_mapping_service=name_mapping_service,
        **filter_params.to_dict(),
    )

    count_expr = get_count_expr()

    async with get_playback_db(server_config) as db:
        async with db.execute(f"""
            SELECT
                DeviceName,
                ClientName,
                {count_expr} as play_count,
                COALESCE(SUM(PlayDuration), 0) as total_duration
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY DeviceName
            ORDER BY play_count DESC
        """, params) as cursor:
            # 使用字典合并同名映射后的设备
            merged_data = {}
            async for row in cursor:
                original_device = row[0] or "Unknown"
                original_client = row[1] or "Unknown"
                mapped_device = name_mapping_service.map_device_name(original_device)
                mapped_client = name_mapping_service.map_client_name(original_client)
                play_count = int(row[2] or 0)
                duration = row[3]

                # 使用设备名作为 key 进行合并
                if mapped_device in merged_data:
                    merged_data[mapped_device]["play_count"] += play_count
                    merged_data[mapped_device]["duration"] += duration
                else:
                    merged_data[mapped_device] = {
                        "client": mapped_client,
                        "play_count": play_count,
                        "duration": duration
                    }

            # 转换为列表并按播放次数排序
            data = [
                {
                    "device": name,
                    "client": info["client"],
                    "play_count": info["play_count"],
                    "duration_hours": round(info["duration"] / 3600, 2)
                }
                for name, info in sorted(
                    merged_data.items(),
                    key=lambda x: x[1]["play_count"],
                    reverse=True
                )
            ]

    return {"devices": data}


@router.get("/playback-methods")
async def get_playback_methods(
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
    days: int = Query(default=30, ge=1, le=365),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    users: Optional[str] = Query(default=None),
    clients: Optional[str] = Query(default=None),
    devices: Optional[str] = Query(default=None),
    item_types: Optional[str] = Query(default=None),
    playback_methods: Optional[str] = Query(default=None),
):
    """获取播放方式统计"""
    server_config = await get_server_config_from_id(server_id)

    # 解析参数
    filter_params = FilterParams(users, clients, devices, item_types, playback_methods)

    where_clause, params = build_filter_conditions(
        days=days if not (start_date or end_date) else None,
        start_date=start_date,
        end_date=end_date,
        local_date_func=local_date,
        name_mapping_service=name_mapping_service,
        **filter_params.to_dict(),
    )

    count_expr = get_count_expr()

    async with get_playback_db(server_config) as db:
        async with db.execute(f"""
            SELECT
                PlaybackMethod,
                {count_expr} as play_count,
                COALESCE(SUM(PlayDuration), 0) as total_duration
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY PlaybackMethod
            ORDER BY play_count DESC
        """, params) as cursor:
            data = []
            async for row in cursor:
                data.append({
                    "method": row[0] or "Unknown",
                    "play_count": int(row[1] or 0),
                    "duration_hours": round(row[2] / 3600, 2)
                })

    return {"methods": data}
