"""
Name mappings router
名称映射管理路由模块
"""
from fastapi import APIRouter

from name_mappings import name_mapping_service

router = APIRouter(prefix="/api", tags=["stats-mappings"])


@router.get("/name-mappings")
async def get_name_mappings():
    """获取名称映射配置"""
    return name_mapping_service.get_all_mappings()


@router.post("/name-mappings")
async def save_name_mappings(mappings: dict):
    """保存名称映射配置"""
    success = name_mapping_service.save_mappings(mappings)
    if success:
        return {"status": "ok", "message": "映射配置已保存"}
    else:
        return {"status": "error", "message": "保存失败"}


@router.post("/name-mappings/reload")
async def reload_name_mappings():
    """重新加载名称映射配置"""
    name_mapping_service.reload()
    return {"status": "ok", "message": "配置已重新加载"}
