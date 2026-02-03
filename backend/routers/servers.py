"""
服务器管理路由模块
处理多服务器配置的 API 端点
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from services.servers import server_service

router = APIRouter(prefix="/api/servers", tags=["servers"])


class ServerCreateRequest(BaseModel):
    name: str
    emby_url: str
    playback_db: str
    users_db: str
    auth_db: str
    emby_api_key: Optional[str] = None
    is_default: bool = False


class ServerUpdateRequest(BaseModel):
    name: Optional[str] = None
    emby_url: Optional[str] = None
    playback_db: Optional[str] = None
    users_db: Optional[str] = None
    auth_db: Optional[str] = None
    emby_api_key: Optional[str] = None
    is_default: Optional[bool] = None


@router.get("")
async def get_all_servers():
    """获取所有服务器配置"""
    servers = await server_service.get_all_servers()
    return {"servers": servers}


@router.get("/default")
async def get_default_server():
    """获取默认服务器"""
    server = await server_service.get_default_server()
    if not server:
        raise HTTPException(status_code=404, detail="未找到默认服务器")
    return {"server": server}


@router.get("/{server_id}")
async def get_server(server_id: str):
    """获取指定服务器配置"""
    server = await server_service.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="服务器不存在")
    return {"server": server}


@router.post("")
async def create_server(request: ServerCreateRequest):
    """创建新服务器"""
    try:
        server_id = await server_service.add_server(
            name=request.name,
            emby_url=request.emby_url,
            playback_db=request.playback_db,
            users_db=request.users_db,
            auth_db=request.auth_db,
            emby_api_key=request.emby_api_key,
            is_default=request.is_default
        )
        return {"success": True, "server_id": server_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{server_id}")
async def update_server(server_id: str, request: ServerUpdateRequest):
    """更新服务器配置"""
    success = await server_service.update_server(
        server_id=server_id,
        name=request.name,
        emby_url=request.emby_url,
        playback_db=request.playback_db,
        users_db=request.users_db,
        auth_db=request.auth_db,
        emby_api_key=request.emby_api_key,
        is_default=request.is_default
    )
    if not success:
        raise HTTPException(status_code=404, detail="服务器不存在")
    return {"success": True}


@router.delete("/{server_id}")
async def delete_server(server_id: str):
    """删除服务器"""
    success = await server_service.delete_server(server_id)
    if not success:
        raise HTTPException(status_code=404, detail="服务器不存在")
    return {"success": True}


