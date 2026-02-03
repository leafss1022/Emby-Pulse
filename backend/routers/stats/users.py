"""
Users statistics router
用户统计路由模块
"""
from fastapi import APIRouter, Query
from typing import Optional

from database import (
    get_playback_db,
    get_count_expr,
    local_date,
    local_datetime,
)
from services.users import user_service
from utils.query_parser import FilterParams, build_filter_conditions
from name_mappings import name_mapping_service
from .helpers import get_server_config_from_id

router = APIRouter(prefix="/api", tags=["stats-users"])


@router.get("/users")
async def get_user_stats(
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
    """获取用户统计"""
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

    count_expr = get_count_expr()
    datetime_col = local_datetime("DateCreated")

    async with get_playback_db(server_config) as db:
        async with db.execute(f"""
            SELECT
                UserId,
                {count_expr} as play_count,
                COALESCE(SUM(PlayDuration), 0) as total_duration,
                MAX({datetime_col}) as last_play
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY UserId
            ORDER BY total_duration DESC
        """, params) as cursor:
            data = []
            async for row in cursor:
                user_id = row[0] or ""
                username = user_service.match_username(user_id, user_map)

                data.append({
                    "user_id": user_id,
                    "username": username,
                    "play_count": int(row[1] or 0),
                    "duration_hours": round(row[2] / 3600, 2),
                    "last_play": row[3]
                })

    return {"users": data}
