"""
Overview statistics router
总览统计路由模块
"""
from fastapi import APIRouter, Query
from typing import Optional

from database import (
    get_playback_db,
    get_count_expr,
    local_date,
)
from services.users import user_service
from utils.query_parser import FilterParams, build_filter_conditions
from name_mappings import name_mapping_service
from .helpers import get_server_config_from_id

router = APIRouter(prefix="/api", tags=["stats-overview"])


@router.get("/overview")
async def get_overview(
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
    days: int = Query(default=30, ge=1, le=365),
    start_date: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD"),
    users: Optional[str] = Query(default=None, description="用户ID列表，逗号分隔"),
    clients: Optional[str] = Query(default=None, description="客户端列表，逗号分隔"),
    devices: Optional[str] = Query(default=None, description="设备列表，逗号分隔"),
    item_types: Optional[str] = Query(default=None, description="媒体类型列表，逗号分隔"),
    playback_methods: Optional[str] = Query(default=None, description="播放方式列表，逗号分隔"),
):
    """获取总览统计"""
    server_config = await get_server_config_from_id(server_id)
    user_map = await user_service.get_user_map(server_config)

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

    async with get_playback_db(server_config) as db:
        count_expr = get_count_expr()

        # 总播放次数（只计满足时长的）和时长（统计所有）
        async with db.execute(f"""
            SELECT
                {count_expr} as total_plays,
                COALESCE(SUM(PlayDuration), 0) as total_duration,
                COUNT(DISTINCT UserId) as unique_users,
                COUNT(DISTINCT ItemId) as unique_items
            FROM PlaybackActivity
            WHERE {where_clause}
        """, params) as cursor:
            row = await cursor.fetchone()
            total_plays = int(row[0] or 0)
            total_duration = row[1]
            unique_users = row[2]
            unique_items = row[3]

        # 按类型统计
        async with db.execute(f"""
            SELECT ItemType, {count_expr} as count, COALESCE(SUM(PlayDuration), 0) as duration
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY ItemType
        """, params) as cursor:
            by_type = {}
            async for row in cursor:
                by_type[row[0] or "Unknown"] = {"count": int(row[1] or 0), "duration": row[2]}

    return {
        "total_plays": total_plays,
        "total_duration_seconds": total_duration,
        "total_duration_hours": round(total_duration / 3600, 2),
        "unique_users": unique_users,
        "unique_items": unique_items,
        "by_type": by_type,
        "days": days
    }
