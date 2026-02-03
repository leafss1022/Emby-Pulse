"""
认证相关路由模块
处理用户登录、登出和会话验证
"""
import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from services.servers import server_service
from services.session import session_service
from logger import get_logger

logger = get_logger("auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str
    server_id: str  # 添加 server_id 字段


class LoginResponse(BaseModel):
    authenticated: bool
    user: dict | None = None


async def authenticate_user_on_server(server_config: dict, username: str, password: str) -> dict | None:
    """在指定服务器上认证用户"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{server_config['emby_url']}/emby/Users/AuthenticateByName",
                headers={
                    "X-Emby-Authorization": 'MediaBrowser Client="Emby Stats", Device="Web", DeviceId="emby-stats", Version="1.0.0"',
                    "Content-Type": "application/json"
                },
                json={
                    "Username": username,
                    "Pw": password
                },
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                user_data = data.get("User", {})
                policy = user_data.get("Policy", {})
                return {
                    "user_id": user_data.get("Id"),
                    "username": user_data.get("Name"),
                    "is_admin": policy.get("IsAdministrator", False)
                }
    except Exception as e:
        logger.error(f"Authentication error: {e}")
    return None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response):
    """用户登录（仅限管理员）"""
    # 获取服务器配置
    server_config = await server_service.get_server(request.server_id)
    if not server_config:
        raise HTTPException(status_code=404, detail="服务器不存在")

    # 验证用户
    user_info = await authenticate_user_on_server(
        server_config, request.username, request.password
    )

    if not user_info:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 检查是否是管理员
    if not user_info.get("is_admin"):
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    # 创建会话（持久化到数据库）
    session_id = await session_service.create_session(
        user_id=user_info["user_id"],
        username=user_info["username"],
        is_admin=user_info["is_admin"],
        server_id=request.server_id
    )

    # 设置 cookie（30天有效期）
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=session_service.session_expire,
        samesite="lax",
        path="/"
    )

    return LoginResponse(
        authenticated=True,
        user={
            "user_id": user_info["user_id"],
            "username": user_info["username"],
            "is_admin": user_info["is_admin"]
        }
    )


@router.post("/logout")
async def logout(request: Request, response: Response):
    """用户登出"""
    session_id = request.cookies.get("session_id")
    if session_id:
        await session_service.delete_session(session_id)

    response.delete_cookie("session_id", path="/")
    return {"success": True}


@router.get("/check")
async def check_auth(request: Request):
    """检查登录状态"""
    session_id = request.cookies.get("session_id")
    session = await session_service.get_session(session_id)

    if not session:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "user": {
            "user_id": session.get("user_id"),
            "username": session.get("username"),
            "is_admin": session.get("is_admin")
        }
    }


async def get_current_session(request: Request) -> dict | None:
    """获取当前会话（供中间件使用）"""
    session_id = request.cookies.get("session_id")
    return await session_service.get_session(session_id)
