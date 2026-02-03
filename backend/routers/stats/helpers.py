"""
Stats helpers module
统计路由辅助函数
"""
from typing import Optional
from fastapi import HTTPException
from services.servers import server_service


async def get_server_config_from_id(server_id: Optional[str]) -> Optional[dict]:
    """
    根据 server_id 获取服务器配置的辅助函数
    所有 stats 子模块共享此函数
    """
    if not server_id:
        return None
    server_config = await server_service.get_server(server_id)
    if not server_config:
        raise HTTPException(status_code=404, detail="服务器不存在")
    return server_config
