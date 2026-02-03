"""
History router
历史记录路由模块（正在播放、最近播放）
"""
from fastapi import APIRouter, Query
from typing import Optional

from database import (
    get_playback_db,
    get_duration_filter,
    local_date,
    local_datetime,
)
from services.users import user_service
from services.emby import emby_service
from utils.query_parser import FilterParams, build_filter_conditions
from name_mappings import name_mapping_service
from .helpers import get_server_config_from_id

router = APIRouter(prefix="/api", tags=["stats-history"])


@router.get("/now-playing")
async def get_now_playing(
    server_id: Optional[str] = Query(default=None, description="服务器ID")
):
    """获取当前正在播放的内容"""
    server_config = await get_server_config_from_id(server_id)
    user_map = await user_service.get_user_map(server_config)
    sessions = await emby_service.get_now_playing(server_config)

    data = []
    for session in sessions:
        item = session.get("NowPlayingItem", {})
        user_name = session.get("UserName", "Unknown")
        user_id = session.get("UserId", "")

        # 尝试从 user_map 匹配用户名
        if user_id:
            matched = user_service.match_username(user_id, user_map)
            if matched != user_id[:8]:
                user_name = matched

        item_id = item.get("Id", "")
        item_name = item.get("Name", "Unknown")
        item_type = item.get("Type", "")
        series_name = item.get("SeriesName", "")

        # 获取海报
        poster_url = None
        if item_type == "Episode" and item.get("SeriesId"):
            poster_url = f"/api/poster/{item['SeriesId']}"
        elif item.get("ImageTags", {}).get("Primary"):
            poster_url = f"/api/poster/{item_id}"

        # 构建显示名称
        if series_name:
            display_name = f"{series_name} - {item_name}"
        else:
            display_name = item_name

        # 播放进度
        position_ticks = session.get("PlayState", {}).get("PositionTicks", 0)
        runtime_ticks = item.get("RunTimeTicks", 0)
        progress = 0
        if runtime_ticks > 0:
            progress = round(position_ticks / runtime_ticks * 100, 1)

        # 播放时长（已播放）
        position_seconds = position_ticks // 10000000 if position_ticks else 0
        runtime_seconds = runtime_ticks // 10000000 if runtime_ticks else 0

        data.append({
            "user_name": user_name,
            "device_name": name_mapping_service.map_device_name(session.get("DeviceName", "Unknown")),
            "client": name_mapping_service.map_client_name(session.get("Client", "Unknown")),
            "item_id": item_id,
            "item_name": display_name,
            "item_type": item_type,
            "poster_url": poster_url,
            "progress": progress,
            "position_seconds": position_seconds,
            "runtime_seconds": runtime_seconds,
            "is_paused": session.get("PlayState", {}).get("IsPaused", False),
            "play_method": session.get("PlayState", {}).get("PlayMethod", ""),
        })

    return {"now_playing": data, "count": len(data)}


@router.get("/recent")
async def get_recent_plays(
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
    limit: Optional[int] = Query(default=None, ge=1, description="返回记录数，不传则根据是否搜索自动决定"),
    offset: Optional[int] = Query(default=0, ge=0, description="偏移量"),
    days: Optional[int] = Query(default=None, ge=1, le=365, description="天数范围，不传则查询全部"),
    start_date: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD"),
    users: Optional[str] = Query(default=None, description="用户ID列表，逗号分隔"),
    clients: Optional[str] = Query(default=None, description="客户端列表，逗号分隔"),
    devices: Optional[str] = Query(default=None, description="设备列表，逗号分隔"),
    item_types: Optional[str] = Query(default=None, description="媒体类型列表，逗号分隔"),
    playback_methods: Optional[str] = Query(default=None, description="播放方式列表，逗号分隔"),
    search: Optional[str] = Query(default=None, description="搜索关键词，匹配内容名称"),
):
    """获取最近播放记录"""
    server_config = await get_server_config_from_id(server_id)
    user_map = await user_service.get_user_map(server_config)
    datetime_col = local_datetime("DateCreated")

    # 判断是否为搜索模式
    is_search_mode = bool(search and search.strip())

    # 根据模式决定 limit：搜索模式默认不限制，普通模式默认48条
    effective_limit = limit if limit is not None else (None if is_search_mode else 48)

    # 解析筛选参数
    filter_params = FilterParams(users, clients, devices, item_types, playback_methods)

    # 构建筛选条件
    where_clause, params = build_filter_conditions(
        days=days if not start_date and not end_date else None,
        start_date=start_date,
        end_date=end_date,
        local_date_func=local_date,
        name_mapping_service=name_mapping_service,
        search=search,
        **filter_params.to_dict(),
    )

    # 获取播放时长过滤条件
    duration_filter = get_duration_filter()

    # 构建基础查询 SQL (不含 LIMIT/OFFSET)
    base_where = f"WHERE {where_clause}{duration_filter}"

    async with get_playback_db(server_config) as db:
        # 1. 查询统计信息（总数和总时长）
        # 使用独立的参数列表，避免后续 LIMIT 参数干扰
        count_sql = f"SELECT COUNT(*) as cnt, COALESCE(SUM(PlayDuration), 0) as total_duration FROM PlaybackActivity {base_where}"
        async with db.execute(count_sql, params) as cursor:
            row = await cursor.fetchone()
            total_count = row[0] if row else 0
            total_duration_seconds = row[1] if row else 0

        # 2. 构建分页查询 SQL
        query_sql = f"""
            SELECT
                {datetime_col} as LocalTime,
                UserId,
                ItemId,
                ItemName,
                ItemType,
                ClientName,
                DeviceName,
                PlayDuration,
                PlaybackMethod
            FROM PlaybackActivity
            {base_where}
            ORDER BY DateCreated DESC
        """

        # 准备分页查询参数
        query_params = list(params)
        if effective_limit is not None:
            query_sql += " LIMIT ? OFFSET ?"
            query_params.extend([effective_limit, offset])
        elif offset > 0:
            query_sql += " LIMIT -1 OFFSET ?"
            query_params.append(offset)

    # 查询播放记录
    from logger import get_logger
    log = get_logger("history")
    log.info(f"Fetching recent plays: offset={offset}, limit={effective_limit}, search={search}")

    async with db.execute(query_sql, query_params) as cursor:
        records = []
        item_ids_to_fetch = set()
        async for row in cursor:
            records.append(row)
            item_id = str(row[2])
            item_ids_to_fetch.add(item_id)
    
    log.info(f"Found {len(records)} records in DB, total_count={total_count}")

    # 第二步: 批量获取所有item信息
    items_info = await emby_service.get_items_info_batch(list(item_ids_to_fetch), server_config)

    # 第三步: 收集可能需要的series_id
    series_ids_to_fetch = set()
    for row in records:
        item_id = str(row[2])
        item_type = row[4]
        info = items_info.get(item_id, {})

        # 对于剧集,收集series_id
        if item_type == "Episode" and info:
            series_id = info.get("SeriesId")
            if series_id:
                series_ids_to_fetch.add(series_id)

    # 第四步: 批量获取所有series信息
    if series_ids_to_fetch:
        series_info_dict = await emby_service.get_items_info_batch(list(series_ids_to_fetch), server_config)
    else:
        series_info_dict = {}

    # 第五步: 构建返回数据
    data = []
    server_id_param = server_id if server_id else None

    for row in records:
        user_id = row[1] or ""
        item_id = str(row[2])
        item_name = row[3]
        item_type = row[4]

        username = user_service.match_username(user_id, user_map)

        # 提取剧名
        show_name = item_name.split(" - ")[0] if " - " in item_name else item_name

        # 从批量查询结果获取信息
        info = items_info.get(item_id, {})

        # 如果 item_id 的信息获取失败（空字典），尝试通过 Emby API 搜索新 ID（洗版后可能 ID 变化）
        if not info:
            new_item_id = await emby_service.search_item_by_name(item_name, item_type, server_config)
            if new_item_id:
                info = await emby_service.get_item_info(new_item_id, server_config)
                if info:
                    item_id = new_item_id

        poster_url = emby_service.get_poster_url(item_id, item_type, info, server_id_param)
        backdrop_url = emby_service.get_backdrop_url(item_id, item_type, info, server_id_param)

        # 获取单集简介（如果有）
        overview = info.get("Overview", "") if info else ""

        # 如果是剧集且没有 backdrop，尝试从剧集获取
        if item_type == "Episode" and not backdrop_url and info:
            series_id = info.get("SeriesId")
            if series_id:
                series_info = series_info_dict.get(series_id, {})
                if series_info and series_info.get("BackdropImageTags"):
                    backdrop_url = f"/api/backdrop/{series_id}"

        data.append({
            "time": row[0],
            "username": username,
            "item_id": item_id,
            "item_name": item_name,
            "show_name": show_name,
            "item_type": item_type,
            "client": name_mapping_service.map_client_name(row[5]),
            "device": name_mapping_service.map_device_name(row[6]),
            "duration_minutes": round((row[7] or 0) / 60, 1),
            "method": row[8],
            "poster_url": poster_url,
            "backdrop_url": backdrop_url,
            "overview": overview
        })

    # 构建返回结果
    result = {
        "recent": data,
        "total_count": total_count,
        "total_duration_seconds": total_duration_seconds
    }

    return result
