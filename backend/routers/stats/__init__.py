"""
Stats routers package
统计相关路由模块包
"""
# 导入所有子模块的路由
from .overview import router as overview_router
from .trend import router as trend_router
from .users import router as users_router
from .content import router as content_router
from .history import router as history_router
from .favorites import router as favorites_router
from .filters import router as filters_router
from .mappings import router as mappings_router


# 导出所有路由列表，供 main.py 使用
all_routers = [
    overview_router,
    trend_router,
    users_router,
    content_router,
    history_router,
    favorites_router,
    filters_router,
    mappings_router,
]
