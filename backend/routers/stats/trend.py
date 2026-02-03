"""
Trend statistics router
趋势统计路由模块（包括按天趋势和按小时热力图）
"""
from fastapi import APIRouter, Query
from typing import Optional

from database import (
    get_playback_db,
    get_count_expr,
    local_date,
    local_datetime,
)
from utils.query_parser import FilterParams, build_filter_conditions
from name_mappings import name_mapping_service
from .helpers import get_server_config_from_id

router = APIRouter(prefix="/api", tags=["stats-trend"])


@router.get("/trend")
async def get_trend(
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
    """获取播放趋势（按天）"""
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
    date_col = local_date("DateCreated")

    async with get_playback_db(server_config) as db:
        async with db.execute(f"""
            SELECT
                {date_col} as play_date,
                {count_expr} as plays,
                COALESCE(SUM(PlayDuration), 0) as duration
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY {date_col}
            ORDER BY play_date
        """, params) as cursor:
            data = []
            async for row in cursor:
                data.append({
                    "date": row[0],
                    "plays": int(row[1] or 0),
                    "duration_hours": round(row[2] / 3600, 2)
                })

    return {"trend": data}


@router.get("/hourly")
async def get_hourly_stats(
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
    """获取按小时统计（热力图数据）"""
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
    datetime_col = local_datetime("DateCreated")

    async with get_playback_db(server_config) as db:
        async with db.execute(f"""
            SELECT
                strftime('%w', {datetime_col}) as day_of_week,
                strftime('%H', {datetime_col}) as hour,
                {count_expr} as play_count
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY day_of_week, hour
        """, params) as cursor:
            data = []
            async for row in cursor:
                data.append({
                    "day": int(row[0]),  # 0=Sunday, 1=Monday, ...
                    "hour": int(row[1]),
                    "count": int(row[2] or 0)
                })

    return {"hourly": data}
