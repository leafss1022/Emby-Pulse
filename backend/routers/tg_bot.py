"""
Telegram Bot 管理路由
提供 Bot 配置和绑定管理的 API
"""
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from services.tg_bot import tg_bot_service, bot_config
from services.tg_binding import tg_binding_service
from services.servers import server_service

router = APIRouter(prefix="/api/tg-bot", tags=["tg-bot"])


# ==================== 配置管理 ====================

class BotConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    bot_token: Optional[str] = None
    default_period: Optional[str] = None


@router.get("/config")
async def get_bot_config():
    """获取 Bot 配置"""
    config = bot_config.load()
    # 隐藏 token 的部分内容
    masked_token = ""
    if config.get("bot_token"):
        token = config["bot_token"]
        if len(token) > 10:
            masked_token = token[:5] + "..." + token[-5:]
        else:
            masked_token = "***"

    return {
        "enabled": config.get("enabled", False),
        "bot_token_masked": masked_token,
        "bot_token_configured": bool(config.get("bot_token")),
        "default_period": config.get("default_period", "monthly"),
        "is_running": tg_bot_service.is_running()
    }


@router.post("/config")
async def save_bot_config(request: BotConfigRequest):
    """保存 Bot 配置"""
    config = bot_config.load()

    if request.enabled is not None:
        config["enabled"] = request.enabled
    if request.bot_token is not None:
        config["bot_token"] = request.bot_token
    if request.default_period is not None:
        config["default_period"] = request.default_period

    success = bot_config.save(config)
    if not success:
        return JSONResponse(status_code=500, content={"error": "保存配置失败"})

    return {"success": True, "message": "配置已保存，重启服务后生效"}


@router.post("/restart")
async def restart_bot():
    """重启 Bot"""
    try:
        # 停止现有 Bot
        await tg_bot_service.stop()

        # 重新加载配置
        bot_config.reload()

        # 启动 Bot
        await tg_bot_service.start()

        return {
            "success": True,
            "is_running": tg_bot_service.is_running(),
            "message": "Bot 已重启" if tg_bot_service.is_running() else "Bot 未启动（可能未配置或已禁用）"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"重启失败: {str(e)}"})


@router.post("/stop")
async def stop_bot():
    """停止 Bot"""
    try:
        await tg_bot_service.stop()
        return {"success": True, "message": "Bot 已停止"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"停止失败: {str(e)}"})


@router.get("/status")
async def get_bot_status():
    """获取 Bot 状态"""
    config = bot_config.load()
    return {
        "enabled": config.get("enabled", False),
        "configured": bool(config.get("bot_token")),
        "is_running": tg_bot_service.is_running()
    }


# ==================== 绑定管理 ====================

@router.get("/bindings")
async def get_all_bindings(server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """获取所有绑定关系"""
    bindings = await tg_binding_service.get_all_bindings(server_id)

    # 获取服务器名称映射
    servers = await server_service.get_all_servers()
    server_map = {s["id"]: s["name"] for s in servers}

    # 添加服务器名称
    for binding in bindings:
        binding["server_name"] = server_map.get(binding["server_id"], "未知")

    return {
        "bindings": bindings,
        "total": len(bindings)
    }


@router.delete("/bindings/{tg_user_id}")
async def delete_binding(
    tg_user_id: str,
    server_id: Optional[str] = Query(default=None, description="服务器ID，不指定则删除该用户所有绑定")
):
    """管理员删除绑定"""
    # 先检查绑定是否存在
    if server_id:
        binding = await tg_binding_service.get_binding(tg_user_id, server_id)
        if not binding:
            return JSONResponse(status_code=404, content={"error": "绑定不存在"})
    else:
        bindings = await tg_binding_service.get_user_bindings(tg_user_id)
        if not bindings:
            return JSONResponse(status_code=404, content={"error": "绑定不存在"})

    success = await tg_binding_service.delete_binding(tg_user_id, server_id)
    if success:
        msg = "绑定已删除" if server_id else "所有绑定已删除"
        return {"success": True, "message": msg}
    else:
        return JSONResponse(status_code=500, content={"error": "删除失败"})


@router.get("/bindings/count")
async def get_binding_count(server_id: Optional[str] = Query(default=None, description="服务器ID")):
    """获取绑定数量"""
    count = await tg_binding_service.get_binding_count(server_id)
    return {"count": count}

