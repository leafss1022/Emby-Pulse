"""
观影报告路由模块
处理观影报告的生成、推送和配置管理
每个服务器有独立的报告配置
"""
from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
import httpx

from services.report import report_service, ReportPeriod
from services.telegram import telegram_service
from services.users import user_service
from services.report_config import report_config_service, TelegramConfig, ScheduleItemConfig
from services.servers import server_service


async def get_server_config(server_id: Optional[str] = None):
    """获取服务器配置"""
    if server_id:
        server = await server_service.get_server(server_id)
        if server:
            return server
    return await server_service.get_default_server()


async def get_server_id_or_default(server_id: Optional[str] = None) -> str:
    """获取服务器ID，如果未指定则返回默认服务器ID"""
    if server_id:
        return server_id
    default_server = await server_service.get_default_server()
    return default_server["id"] if default_server else ""


router = APIRouter(prefix="/api/report", tags=["report"])


# ==================== 配置管理 API ====================

@router.get("/config")
async def get_config(server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """获取指定服务器的报告配置"""
    actual_server_id = await get_server_id_or_default(server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    server_config = await get_server_config(actual_server_id)
    config = report_config_service.load(actual_server_id)
    user_map = await user_service.get_user_map(server_config)
    all_users = [{"user_id": uid, "username": uname} for uid, uname in user_map.items()]

    return {
        "config": config.model_dump(),
        "all_users": all_users,
        "server_id": actual_server_id
    }


class ScheduleItemRequest(BaseModel):
    enabled: bool = False
    cron: str = ""


class ScheduleRequest(BaseModel):
    daily: Optional[ScheduleItemRequest] = None
    weekly: Optional[ScheduleItemRequest] = None
    monthly: Optional[ScheduleItemRequest] = None


class SaveConfigRequest(BaseModel):
    telegram: Optional[TelegramConfig] = None
    schedule: Optional[ScheduleRequest] = None
    users: Optional[list[str]] = None
    content_count: Optional[int] = None
    server_id: Optional[str] = None  # 必须指定要保存到哪个服务器


@router.post("/config")
async def save_config(request: SaveConfigRequest):
    """保存指定服务器的报告配置"""
    actual_server_id = await get_server_id_or_default(request.server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    # 加载该服务器的现有配置
    config = report_config_service.load(actual_server_id)

    if request.telegram is not None:
        config.telegram = request.telegram
    if request.schedule is not None:
        if request.schedule.daily is not None:
            config.schedule.daily = ScheduleItemConfig(**request.schedule.daily.model_dump())
        if request.schedule.weekly is not None:
            config.schedule.weekly = ScheduleItemConfig(**request.schedule.weekly.model_dump())
        if request.schedule.monthly is not None:
            config.schedule.monthly = ScheduleItemConfig(**request.schedule.monthly.model_dump())
    if request.users is not None:
        config.users = request.users
    if request.content_count is not None:
        config.content_count = request.content_count

    # 保存到该服务器的配置文件
    success = report_config_service.save(actual_server_id, config)

    if success:
        from scheduler import reload_scheduler
        reload_scheduler()
        return {"success": True, "config": config.model_dump(), "server_id": actual_server_id}
    else:
        return JSONResponse(status_code=500, content={"error": "保存配置失败"})


@router.post("/config/test-telegram")
async def test_telegram(server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """测试指定服务器的 Telegram 连接"""
    actual_server_id = await get_server_id_or_default(server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    config = report_config_service.load(actual_server_id)

    if not config.telegram.enabled or not config.telegram.bot_token or not config.telegram.chat_id:
        return JSONResponse(status_code=400, content={"error": "Telegram 未配置"})

    success = await telegram_service.send_message_with_config(
        "✅ Emby Stats 观影报告测试消息\n\n连接成功！",
        config.telegram.bot_token,
        config.telegram.chat_id,
        config.telegram.proxy
    )

    if success:
        return {"success": True, "message": "测试消息发送成功"}
    else:
        return JSONResponse(status_code=500, content={"error": "发送失败，请检查 Bot Token 和 Chat ID"})


# ==================== 报告预览和发送 API ====================

@router.get("/preview")
async def preview_report(period: ReportPeriod = "weekly", server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """预览指定服务器的观影报告图片"""
    actual_server_id = await get_server_id_or_default(server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    server_config = await get_server_config(actual_server_id)
    config = report_config_service.load(actual_server_id)

    user_ids = None
    if config.users:
        report_users = await report_service.get_report_users(config.users, server_config)
        user_ids = [uid for uid, _ in report_users]

    try:
        image_data = await report_service.generate_report_image(
            user_ids=user_ids,
            period=period,
            content_count=config.content_count,
            server_config=server_config
        )
        return Response(content=image_data, media_type="image/png")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"生成报告失败: {str(e)}"})


@router.get("/preview/{user_id}")
async def preview_user_report(user_id: str, period: ReportPeriod = "weekly", server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """预览指定服务器单个用户的观影报告图片"""
    actual_server_id = await get_server_id_or_default(server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    server_config = await get_server_config(actual_server_id)
    config = report_config_service.load(actual_server_id)

    try:
        image_data = await report_service.generate_report_image(
            user_ids=[user_id],
            period=period,
            content_count=config.content_count,
            server_config=server_config
        )
        return Response(content=image_data, media_type="image/png")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"生成报告失败: {str(e)}"})


@router.get("/stats")
async def get_report_stats(period: ReportPeriod = "weekly", server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """获取指定服务器的报告统计数据"""
    actual_server_id = await get_server_id_or_default(server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    server_config = await get_server_config(actual_server_id)
    config = report_config_service.load(actual_server_id)

    user_ids = None
    if config.users:
        report_users = await report_service.get_report_users(config.users, server_config)
        user_ids = [uid for uid, _ in report_users]

    # 获取时间范围
    _, start_date, _ = report_service._get_period_info(period)

    stats = await report_service.get_stats(user_ids, start_date, server_config)
    top_content = await report_service.get_top_content(user_ids, start_date, config.content_count, server_config)

    return {
        "stats": stats,
        "top_content": top_content
    }


@router.post("/send")
async def send_report(period: ReportPeriod = "weekly", server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """手动触发发送指定服务器的观影报告到 Telegram"""
    actual_server_id = await get_server_id_or_default(server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    server_config = await get_server_config(actual_server_id)
    config = report_config_service.load(actual_server_id)

    if not config.telegram.enabled or not config.telegram.bot_token or not config.telegram.chat_id:
        return JSONResponse(status_code=400, content={"error": "Telegram 未配置或未启用"})

    user_ids = None
    if config.users:
        report_users = await report_service.get_report_users(config.users, server_config)
        user_ids = [uid for uid, _ in report_users]

    period_names = {"daily": "今日", "weekly": "本周", "monthly": "本月", "yearly": "年度"}

    try:
        image_data = await report_service.generate_report_image(
            user_ids=user_ids,
            period=period,
            content_count=config.content_count,
            server_config=server_config
        )
        success = await telegram_service.send_photo_with_config(
            image_data,
            f"📊 {period_names[period]}观影报告",
            config.telegram.bot_token,
            config.telegram.chat_id,
            config.telegram.proxy
        )

        if success:
            return {"success": True, "message": "报告发送成功"}
        else:
            return JSONResponse(status_code=500, content={"error": "发送失败"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"生成报告失败: {str(e)}"})


@router.get("/users")
async def get_report_users(server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """获取指定服务器配置的报告用户列表"""
    actual_server_id = await get_server_id_or_default(server_id)
    if not actual_server_id:
        return JSONResponse(status_code=400, content={"error": "未找到服务器"})

    server_config = await get_server_config(actual_server_id)
    config = report_config_service.load(actual_server_id)
    users = await report_service.get_report_users(config.users if config.users else None, server_config)
    return {"users": [{"user_id": uid, "username": uname} for uid, uname in users]}


class TestPushRequest(BaseModel):
    bot_token: str
    chat_id: str


@router.post("/test-push")
async def test_push(request: TestPushRequest):
    """测试报告推送（直接使用提供的 bot_token 和 chat_id）"""
    if not request.bot_token or not request.chat_id:
        return JSONResponse(
            status_code=400,
            content={"error": "bot_token 和 chat_id 不能为空"}
        )

    # 测试消息内容
    test_message = "✅ 测试消息\n\nEmby Stats 报告推送配置成功！可以正常发送消息。"

    try:
        # 使用 Telegram Bot API 发送测试消息
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{request.bot_token}/sendMessage",
                json={
                    "chat_id": request.chat_id,
                    "text": test_message,
                    "parse_mode": "Markdown"
                }
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    return {
                        "success": True,
                        "message": "测试消息发送成功！请检查 Telegram 查看测试消息。"
                    }
                else:
                    error_msg = result.get("description", "未知错误")
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"发送失败: {error_msg}"}
                    )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"HTTP 错误: {response.status_code}"}
                )

    except httpx.TimeoutException:
        return JSONResponse(
            status_code=408,
            content={"error": "请求超时，请检查网络连接或代理设置"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"发送失败: {str(e)}"}
        )

