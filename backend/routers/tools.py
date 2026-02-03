"""
工具 API 路由

提供各种维护和管理工具的 API 接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import aiosqlite

from database import get_playback_db
from services.servers import server_service
from logger import get_logger

router = APIRouter(prefix="/api/tools", tags=["Tools"])
logger = get_logger(__name__)


class ReplaceItemIdRequest(BaseModel):
    """Item ID 替换请求"""
    old_id: str
    new_id: str
    server_id: str  # 服务器 ID 是 UUID 字符串


class ReplaceItemIdResponse(BaseModel):
    """Item ID 替换响应"""
    success: bool
    updated_count: int
    message: str


@router.post("/replace-item-id", response_model=ReplaceItemIdResponse)
async def replace_item_id(request: ReplaceItemIdRequest):
    """
    替换播放记录数据库中的 Item ID

    用于处理剧集洗版后 ItemId 变化的情况
    """
    try:
        logger.info(f"[Tools] 收到替换请求: old_id={request.old_id}, new_id={request.new_id}, server_id={request.server_id}")

        # 获取服务器配置
        server_config = await server_service.get_server(request.server_id)
        if not server_config:
            logger.warning(f"[Tools] 服务器配置不存在: server_id={request.server_id}")
            raise HTTPException(status_code=404, detail="服务器配置不存在")

        # 连接数据库
        db_path = server_config.get("playback_db")
        if not db_path:
            raise HTTPException(status_code=400, detail="服务器未配置播放记录数据库")

        async with aiosqlite.connect(db_path) as db:
            # 设置 busy_timeout，避免多服务器环境下的锁死问题
            await db.execute("PRAGMA busy_timeout = 30000")
            # 查询受影响的记录数
            cursor = await db.execute(
                "SELECT COUNT(*) FROM PlaybackActivity WHERE ItemId = ?",
                (request.old_id,)
            )
            count_result = await cursor.fetchone()
            count = count_result[0] if count_result else 0

            if count == 0:
                logger.info(f"[Tools] 未找到 ItemId = {request.old_id} 的记录")
                return ReplaceItemIdResponse(
                    success=True,
                    updated_count=0,
                    message=f"未找到 ItemId = {request.old_id} 的记录"
                )

            logger.info(f"[Tools] 准备更新 {count} 条记录: {request.old_id} -> {request.new_id}")

            # 执行更新
            await db.execute(
                "UPDATE PlaybackActivity SET ItemId = ? WHERE ItemId = ?",
                (request.new_id, request.old_id)
            )

            # 提交更改
            await db.commit()

            logger.info(f"[Tools] 成功更新 {count} 条记录")

            return ReplaceItemIdResponse(
                success=True,
                updated_count=count,
                message=f"成功更新 {count} 条记录"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Tools] Item ID 替换失败: {e}")
        raise HTTPException(status_code=500, detail=f"替换失败: {str(e)}")
