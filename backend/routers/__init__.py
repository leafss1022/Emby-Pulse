"""路由模块"""
from .stats import all_routers as stats_routers
from .media import router as media_router
from .auth import router as auth_router
from .servers import router as servers_router
from .files import router as files_router
from .report import router as report_router
from .tg_bot import router as tg_bot_router
from .tools import router as tools_router

__all__ = [
    "stats_routers",
    "media_router",
    "auth_router",
    "servers_router",
    "files_router",
    "report_router",
    "tg_bot_router",
    "tools_router"
]
