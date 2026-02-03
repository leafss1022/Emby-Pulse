"""
媒体相关路由模块
处理内容排行和海报等 API 端点
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List

from database import get_playback_db, get_count_expr, local_date, local_datetime, get_duration_filter
from services.emby import emby_service
from services.servers import server_service
from services.users import user_service
from name_mappings import name_mapping_service
from utils.query_parser import build_filter_conditions

router = APIRouter(prefix="/api", tags=["media"])


@router.get("/top-content")
async def get_top_content(
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
    item_type: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    users: Optional[str] = Query(default=None),
    clients: Optional[str] = Query(default=None),
    devices: Optional[str] = Query(default=None),
    playback_methods: Optional[str] = Query(default=None),
):
    """获取热门内容排行（剧集按剧名聚合，电影等按ItemId）"""
    server_config = None
    if server_id:
        server_config = await server_service.get_server(server_id)
        if not server_config:
            raise HTTPException(status_code=404, detail="服务器不存在")

    user_list = [u.strip() for u in users.split(",")] if users else None
    client_list = [c.strip() for c in clients.split(",")] if clients else None
    device_list = [d.strip() for d in devices.split(",")] if devices else None
    method_list = [m.strip() for m in playback_methods.split(",")] if playback_methods else None
    type_list = [item_type] if item_type else None

    where_clause, params = build_filter_conditions(
        days=days if not (start_date or end_date) else None,
        start_date=start_date,
        end_date=end_date,
        users=user_list,
        clients=client_list,
        devices=device_list,
        item_types=type_list,
        playback_methods=method_list,
        local_date_func=local_date,
        name_mapping_service=name_mapping_service,
    )

    count_expr = get_count_expr()

    async with get_playback_db(server_config) as db:
        query = f"""
            SELECT
                ItemId,
                ItemName,
                ItemType,
                {count_expr} as play_count,
                COALESCE(SUM(PlayDuration), 0) as total_duration
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY ItemId
        """

        async with db.execute(query, params) as cursor:
            # 按剧名/内容聚合
            content_map = defaultdict(lambda: {
                "play_count": 0,
                "duration": 0,
                "item_id": None,
                "item_type": None,
                "full_name": None
            })

            async for row in cursor:
                item_id = row[0]
                item_name = row[1] or "Unknown"
                item_type_val = row[2]
                play_count = int(row[3] or 0)
                duration = row[4]

                # 对于剧集，提取剧名作为聚合key；其他类型用完整名称
                if item_type_val == "Episode" and " - " in item_name:
                    key = item_name.split(" - ")[0]  # 剧名
                else:
                    key = item_name

                content_map[key]["play_count"] += play_count
                content_map[key]["duration"] += duration

                # 保存一个item_id用于获取海报
                if not content_map[key]["item_id"]:
                    content_map[key]["item_id"] = item_id
                    content_map[key]["item_type"] = item_type_val
                    content_map[key]["full_name"] = item_name

        # 排序并限制数量
        sorted_content = sorted(
            content_map.items(),
            key=lambda x: x[1]["play_count"],
            reverse=True
        )[:limit]

        data = []
        for name, info in sorted_content:
            item_id = info["item_id"]
            item_type_val = info["item_type"]

            # 获取海报 URL 和剧集介绍
            item_info = await emby_service.get_item_info(str(item_id), server_config)

            # 如果第一个item_id的信息获取失败（空字典），尝试从数据库查找其他item_id
            if not item_info:
                # 对于剧集，按剧名查找；对于其他类型，按完整名称查找
                if item_type_val == "Episode":
                    search_field = "ItemName LIKE ?"
                    search_value = f"{name} - %"
                else:
                    search_field = "ItemName = ?"
                    search_value = name

                fallback_query = f"""
                    SELECT DISTINCT ItemId
                    FROM PlaybackActivity
                    WHERE {search_field} AND ItemType = ? AND ItemId != ?
                    LIMIT 5
                """
                # 先收集所有候选 item_id
                fallback_ids = []
                async with db.execute(fallback_query, [search_value, item_type_val, item_id]) as fallback_cursor:
                    async for fallback_row in fallback_cursor:
                        fallback_ids.append(str(fallback_row[0]))

                # 批量查询所有候选 item_id 的信息
                if fallback_ids:
                    items_info = await emby_service.get_items_info_batch(fallback_ids, server_config)
                    # 找到第一个有效的 item_info
                    for fallback_item_id in fallback_ids:
                        if items_info.get(fallback_item_id):
                            item_info = items_info[fallback_item_id]
                            item_id = fallback_item_id
                            break

            poster_url = emby_service.get_poster_url(str(item_id), item_type_val, item_info, server_id)
            backdrop_url = emby_service.get_backdrop_url(str(item_id), item_type_val, item_info, server_id)

            # 获取 overview（剧集介绍）
            overview = item_info.get("Overview", "") if item_info else ""
            # 对于剧集，转换为 Series ID（这样点击后进入整部剧详情）
            detail_item_id = item_id
            detail_item_type = item_type_val
            if item_type_val == "Episode" and item_info:
                series_id = item_info.get("SeriesId")
                if not series_id:
                    series_info_meta = item_info.get("SeriesInfo") or {}
                    if isinstance(series_info_meta, dict):
                        series_id = series_info_meta.get("Id") or series_info_meta.get("SeriesId")
                if series_id:
                    series_info = await emby_service.get_item_info(series_id, server_config)
                    if series_info:
                        overview = series_info.get("Overview", overview)
                        # 热门内容展示优先使用整部剧的海报，避免单集/季条目缺图
                        series_poster_url = emby_service.get_poster_url(series_id, "Series", series_info, server_id)
                        if series_poster_url:
                            poster_url = series_poster_url
                        # 也尝试从剧集获取 backdrop
                        if not backdrop_url and series_info.get("BackdropImageTags"):
                            server_param = f"?server_id={server_id}" if server_id else ""
                            backdrop_url = f"/api/backdrop/{series_id}{server_param}"
                        # 返回 Series ID，这样前端跳转时会进入整部剧详情
                        detail_item_id = series_id
                        detail_item_type = "Series"

            data.append({
                "item_id": detail_item_id,
                "name": info["full_name"] or name,
                "show_name": name,
                "type": detail_item_type,
                "play_count": info["play_count"],
                "duration_hours": round(info["duration"] / 3600, 2),
                "poster_url": poster_url,
                "backdrop_url": backdrop_url,
                "overview": overview
            })

    return {"top_content": data}


@router.get("/top-shows")
async def get_top_shows(
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    users: Optional[str] = Query(default=None),
    clients: Optional[str] = Query(default=None),
    devices: Optional[str] = Query(default=None),
    playback_methods: Optional[str] = Query(default=None),
):
    """获取热门剧集（按剧名聚合）"""
    server_config = None
    if server_id:
        server_config = await server_service.get_server(server_id)
        if not server_config:
            raise HTTPException(status_code=404, detail="服务器不存在")

    user_list = [u.strip() for u in users.split(",")] if users else None
    client_list = [c.strip() for c in clients.split(",")] if clients else None
    device_list = [d.strip() for d in devices.split(",")] if devices else None
    method_list = [m.strip() for m in playback_methods.split(",")] if playback_methods else None

    where_clause, params = build_filter_conditions(
        days=days if not (start_date or end_date) else None,
        start_date=start_date,
        end_date=end_date,
        users=user_list,
        clients=client_list,
        devices=device_list,
        item_types=["Episode"],  # 只查剧集
        playback_methods=method_list,
        local_date_func=local_date,
        name_mapping_service=name_mapping_service,
    )

    count_expr = get_count_expr()

    async with get_playback_db(server_config) as db:
        async with db.execute(f"""
            SELECT
                ItemId,
                ItemName,
                ItemType,
                {count_expr} as play_count,
                COALESCE(SUM(PlayDuration), 0) as total_duration
            FROM PlaybackActivity
            WHERE {where_clause}
            GROUP BY ItemId
        """, params) as cursor:
            shows = defaultdict(lambda: {
                "play_count": 0,
                "duration": 0,
                "episodes": set(),
                "series_id": None,
                "item_id": None
            })
            async for row in cursor:
                item_id = row[0]
                item_name = row[1] or "Unknown"
                show_name = item_name.split(" - ")[0] if " - " in item_name else item_name
                shows[show_name]["play_count"] += int(row[3] or 0)
                shows[show_name]["duration"] += row[4]
                shows[show_name]["episodes"].add(item_name)
                # 保存一个 item_id 用于获取 series_id
                if not shows[show_name]["item_id"]:
                    shows[show_name]["item_id"] = item_id

    # 排序并限制数量
    sorted_shows = sorted(shows.items(), key=lambda x: x[1]["play_count"], reverse=True)[:limit]

    result = []
    for show_name, show_data in sorted_shows:
        # 获取海报和剧集介绍
        poster_url = None
        backdrop_url = None
        overview = ""
        series_id = None
        item_id = show_data["item_id"]

        if item_id:
            info = await emby_service.get_item_info(str(item_id), server_config)

            # 如果第一个item_id的信息获取失败（空字典），尝试从数据库查找其他集数
            if not info:
                fallback_query = f"""
                    SELECT DISTINCT ItemId
                    FROM PlaybackActivity
                    WHERE ItemName LIKE ? AND ItemType = 'Episode' AND ItemId != ?
                    LIMIT 5
                """
                # 先收集所有候选 item_id
                fallback_ids = []
                async with get_playback_db(server_config) as fallback_db:
                    async with fallback_db.execute(fallback_query, [f"{show_name} - %", item_id]) as fallback_cursor:
                        async for fallback_row in fallback_cursor:
                            fallback_ids.append(str(fallback_row[0]))

                # 批量查询所有候选 item_id 的信息
                if fallback_ids:
                    items_info = await emby_service.get_items_info_batch(fallback_ids, server_config)
                    # 找到第一个有效的 item_info
                    for fallback_item_id in fallback_ids:
                        if items_info.get(fallback_item_id):
                            info = items_info[fallback_item_id]
                            item_id = fallback_item_id
                            break

            if info and info.get("SeriesId"):
                series_id = info["SeriesId"]
                server_param = f"?server_id={server_id}" if server_id else ""
                poster_url = f"/api/poster/{series_id}{server_param}"
                # 获取剧集总介绍
                series_info = await emby_service.get_item_info(series_id, server_config)
                if series_info:
                    overview = series_info.get("Overview", "")
                    if series_info.get("BackdropImageTags"):
                        backdrop_url = f"/api/backdrop/{series_id}{server_param}"

        result.append({
            "show_name": show_name,
            "play_count": show_data["play_count"],
            "duration_hours": round(show_data["duration"] / 3600, 2),
            "episode_count": len(show_data["episodes"]),
            "poster_url": poster_url,
            "backdrop_url": backdrop_url,
            "overview": overview
        })

    return {"top_shows": result}


@router.get("/poster/{item_id}")
async def get_poster(
    item_id: str,
    server_id: Optional[str] = Query(default=None),
    maxHeight: int = Query(default=300),
    maxWidth: int = Query(default=200)
):
    """代理获取 Emby 海报图片"""
    server_config = None
    if server_id:
        server_config = await server_service.get_server(server_id)

    content, content_type = await emby_service.get_poster(item_id, maxHeight, maxWidth, server_config)
    if not content:
        raise HTTPException(status_code=404, detail="Poster not found")

    return StreamingResponse(
        iter([content]),
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"}
    )


@router.get("/backdrop/{item_id}")
async def get_backdrop(
    item_id: str,
    server_id: Optional[str] = Query(default=None),
    maxHeight: int = Query(default=720),
    maxWidth: int = Query(default=1280)
):
    """代理获取 Emby 背景图(横版)"""
    server_config = None
    if server_id:
        server_config = await server_service.get_server(server_id)

    content, content_type = await emby_service.get_backdrop(item_id, maxHeight, maxWidth, server_config)
    if not content:
        raise HTTPException(status_code=404, detail="Backdrop not found")

    return StreamingResponse(
        iter([content]),
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"}
    )


@router.get("/content-detail")
async def get_content_detail(
    item_id: str = Query(..., description="内容ID"),
    server_id: Optional[str] = Query(default=None, description="服务器ID"),
):
    """获取内容详情（包括基本信息、统计数据和播放记录）"""
    server_config = None
    if server_id:
        server_config = await server_service.get_server(server_id)

    user_map = await user_service.get_user_map(server_config)
    count_expr = get_count_expr()
    datetime_col = local_datetime("DateCreated")
    duration_filter = get_duration_filter()

    # 先从 Emby API 获取基本信息
    item_info = await emby_service.get_item_info(item_id, server_config)

    # 从播放数据库获取基本信息作为回退（如果 Emby API 失败）
    db_item_name = None
    db_item_type = None
    async with get_playback_db(server_config) as db:
        async with db.execute("""
            SELECT ItemName, ItemType FROM PlaybackActivity WHERE ItemId = ? LIMIT 1
        """, [item_id]) as cursor:
            row = await cursor.fetchone()
            if row:
                db_item_name = row[0]
                db_item_type = row[1]

    # 优先使用 Emby API 的信息，失败时使用数据库的信息
    item_name = item_info.get("Name") if item_info else (db_item_name or "未知内容")
    item_type = item_info.get("Type") if item_info else (db_item_type or "Unknown")
    overview = item_info.get("Overview", "") if item_info else ""

    # 获取海报和背景图
    poster_url = emby_service.get_poster_url(item_id, item_type, item_info, server_id)
    backdrop_url = emby_service.get_backdrop_url(item_id, item_type, item_info, server_id)

    # 如果是剧集，尝试获取剧集信息
    if item_type == "Episode" and item_info:
        series_id = item_info.get("SeriesId")
        if series_id:
            series_info = await emby_service.get_item_info(series_id, server_config)
            if series_info:
                overview = series_info.get("Overview", overview)
                if not backdrop_url and series_info.get("BackdropImageTags"):
                    backdrop_url = f"/api/backdrop/{series_id}"
                if not poster_url:
                    server_param = f"?server_id={server_id}" if server_id else ""
                    poster_url = f"/api/poster/{series_id}{server_param}"

    # 提取剧名
    show_name = item_name.split(" - ")[0] if " - " in item_name else item_name

    # 从播放数据库查询统计数据和播放记录
    async with get_playback_db(server_config) as db:
        # 根据类型构建统计查询条件
        if item_type == "Series":
            # Series 类型：用剧名匹配所有集数
            stats_condition = "ItemName LIKE ?"
            stats_params = [f"{item_name} - %"]
        else:
            # Episode/Movie 等：直接用 ItemId
            stats_condition = "ItemId = ?"
            stats_params = [item_id]

        # 获取统计数据
        async with db.execute(f"""
            SELECT
                {count_expr} as total_plays,
                COALESCE(SUM(PlayDuration), 0) as total_duration,
                COUNT(DISTINCT UserId) as unique_users,
                MAX({datetime_col}) as last_play
            FROM PlaybackActivity
            WHERE {stats_condition}
        """, stats_params) as cursor:
            row = await cursor.fetchone()
            if row:
                total_plays = int(row[0] or 0)
                total_duration = row[1] or 0
                unique_users = row[2] or 0
                last_play = row[3]
            else:
                total_plays = 0
                total_duration = 0
                unique_users = 0
                last_play = None

        # 获取播放记录
        # 对于Series类型，查询以"剧名 - "开头的所有集数（精确匹配剧名）
        # 对于Episode/Movie等，直接用ItemId查询
        if item_type == "Series":
            # 系列剧：用 "剧名 - " 开头精确匹配，避免匹配到同名剧
            query_condition = "ItemName LIKE ?"
            query_params = [f"{item_name} - %"]
        else:
            # Episode/Movie 等：直接用 ItemId 查询
            query_condition = "ItemId = ?"
            query_params = [item_id]

        async with db.execute(f"""
            SELECT
                {datetime_col} as LocalTime,
                UserId,
                ItemName,
                ClientName,
                DeviceName,
                PlayDuration,
                PlaybackMethod
            FROM PlaybackActivity
            WHERE {query_condition}{duration_filter}
            ORDER BY DateCreated DESC
            LIMIT 100
        """, query_params) as cursor:
            play_records = []
            async for row in cursor:
                user_id = row[1] or ""
                username = user_service.match_username(user_id, user_map)

                play_records.append({
                    "time": row[0],
                    "username": username,
                    "item_name": row[2],
                    "client": name_mapping_service.map_client_name(row[3]),
                    "device": name_mapping_service.map_device_name(row[4]),
                    "duration_minutes": round((row[5] or 0) / 60, 1),
                    "method": row[6]
                })

    return {
        "item_name": item_name,
        "show_name": show_name,
        "item_type": item_type,
        "poster_url": poster_url,
        "backdrop_url": backdrop_url,
        "overview": overview,
        "stats": {
            "total_plays": total_plays,
            "total_duration_hours": round(total_duration / 3600, 2),
            "unique_users": unique_users,
            "last_play": last_play
        },
        "play_records": play_records
    }
