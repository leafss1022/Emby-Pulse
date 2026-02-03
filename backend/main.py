"""
Emby Stats - 播放统计分析应用
主入口文件
"""
import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from routers import (
    stats_routers,
    media_router,
    auth_router,
    servers_router,
    files_router,
    report_router,
    tg_bot_router,
    tools_router
)
from routers.auth import get_current_session
from services.session import session_service
from services.servers import server_service
from services.tg_binding import tg_binding_service
from services.tg_bot import tg_bot_service
from scheduler import setup_scheduler
from logger import init_logging, get_logger
from db_pool import pool_manager

# 初始化日志系统
init_logging()
logger = get_logger("main")

# 创建应用实例
app = FastAPI(title="Emby Stats")

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 不需要认证的路径
PUBLIC_PATHS = {
    "/api/auth/login",
    "/api/auth/check",
    "/api/auth/logout",
    "/api/debug/scheduler",  # 调试端点
    "/manifest.json",
    "/sw.js",
}

# 不需要认证的路径前缀
PUBLIC_PREFIXES = [
    "/api/servers",      # 服务器列表（登录页需要）
    "/api/files",        # 文件浏览器（添加服务器时需要）
    "/icons/",
    "/static/",
]


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """认证中间件：保护 API 端点"""
    path = request.url.path

    # 静态资源和认证接口不需要验证
    if path in PUBLIC_PATHS:
        return await call_next(request)

    for prefix in PUBLIC_PREFIXES:
        if path.startswith(prefix):
            return await call_next(request)

    # 前端页面（非 API）不在这里拦截，由前端处理
    if not path.startswith("/api/"):
        return await call_next(request)

    # API 请求需要验证
    session = await get_current_session(request)
    if not session:
        return JSONResponse(
            status_code=401,
            content={"detail": "未登录"}
        )

    return await call_next(request)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """HTTP 请求/响应日志中间件"""
    # 排除静态资源和健康检查的日志
    path = request.url.path
    if path.startswith(("/icons/", "/static/", "/manifest.json", "/sw.js")) or path == "/":
        return await call_next(request)

    # 记录请求开始时间
    start_time = time.time()

    # 处理请求
    try:
        response = await call_next(request)
        # 计算响应时间
        duration_ms = int((time.time() - start_time) * 1000)

        # 根据状态码选择日志级别（仅记录错误）
        status_code = response.status_code
        method = request.method

        if 400 <= status_code < 500:
            # 客户端错误：警告级别
            logger.warning(
                f"{method} {path} - {status_code} ({duration_ms}ms)"
            )
        elif status_code >= 500:
            # 服务器错误：错误级别
            logger.error(
                f"{method} {path} - {status_code} ({duration_ms}ms)"
            )
        # 成功的请求（200-399）不记录日志，减少日志噪音

        return response

    except Exception as e:
        # 未捕获的异常
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"{request.method} {path} - 500 ({duration_ms}ms) - Exception: {str(e)}"
        )
        raise


async def check_database_indexes():
    """检查数据库索引，提示性能优化"""
    # 要检查的索引
    expected_indexes = [
        "idx_playback_date_user_item",
        "idx_playback_item_date",
        "idx_playback_user_date",
        "idx_playback_date",
    ]

    try:
        servers = await server_service.get_all_servers()
        if not servers:
            return

        from database import get_playback_db

        has_warning = False
        for server in servers:
            playback_db = server.get("playback_db")
            if not playback_db or not os.path.exists(playback_db):
                continue

            server_name = server.get("name", "Unknown")

            async with get_playback_db(server) as db:
                # 检查已存在的索引
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='index'
                    AND tbl_name='PlaybackActivity'
                    AND name LIKE 'idx_playback_%'
                """)
                existing_indexes = {row[0] for row in await cursor.fetchall()}

                missing_indexes = [idx for idx in expected_indexes if idx not in existing_indexes]

                if missing_indexes:
                    if not has_warning:
                        logger.warning("⚠️  检测到部分服务器缺少数据库性能优化索引")
                        has_warning = True
                    logger.info(f"   服务器 [{server_name}] 缺少 {len(missing_indexes)} 个索引")
                else:
                    logger.info(f"✓ 服务器 [{server_name}] 数据库索引已优化 (已有 {len(existing_indexes)} 个优化索引)")

        if has_warning:
            logger.warning("💡 由于数据库是只读挂载，需要在宿主机上手动优化：")
            logger.warning("   cd /path/to/emby/data && sqlite3 playback_reporting.db < /path/to/create_indexes.sql")
            logger.warning("   或使用工具脚本: docker exec emby-stats python /app/tools/add_playback_indexes.py /data/playback_reporting.db")

    except Exception as e:
        # 索引检查失败不影响启动
        logger.debug(f"索引检查失败: {e}")


@app.on_event("startup")
async def startup_event():
    """应用启动时执行的初始化操作"""
    # 初始化会话数据库
    await session_service.init_db()
    logger.info("✓ 会话数据库初始化完成")

    # 初始化服务器配置数据库
    await server_service.init_servers_table()
    logger.info("✓ 服务器配置数据库初始化完成")

    # 迁移旧版配置（从环境变量自动创建默认服务器）
    await server_service.migrate_legacy_config()
    servers = await server_service.get_all_servers()
    if servers:
        logger.info(f"✓ 已加载 {len(servers)} 个服务器配置")
    else:
        logger.warning("⚠ 未检测到服务器配置，请在登录页添加服务器")

    # 清理过期会话
    cleaned = await session_service.clean_expired_sessions()
    if cleaned > 0:
        logger.info(f"✓ 清理了 {cleaned} 个过期会话")

    # 检查数据库索引优化状态
    await check_database_indexes()

    # 启动定时任务调度器
    setup_scheduler()
    logger.info("✓ 定时任务调度器已启动")

    # 初始化 TG 绑定数据库
    await tg_binding_service.init_db()
    logger.info("✓ TG 绑定数据库初始化完成")

    # 启动 Telegram Bot
    await tg_bot_service.start()
    if tg_bot_service.is_running():
        logger.info("✓ Telegram Bot 已启动")
    else:
        logger.info("ℹ Telegram Bot 未启用或配置不完整")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的清理操作"""
    # 停止 Telegram Bot
    await tg_bot_service.stop()

    # 关闭所有数据库连接池
    await pool_manager.close_all()
    logger.info("✓ 数据库连接池已关闭")


# 注册路由
app.include_router(auth_router)
# 注册所有 stats 子路由
for router in stats_routers:
    app.include_router(router)
app.include_router(media_router)
app.include_router(servers_router)
app.include_router(files_router)
app.include_router(report_router)
app.include_router(tg_bot_router)
app.include_router(tools_router)


# 调试用：查看调度器状态
@app.get("/api/debug/scheduler")
async def debug_scheduler_status():
    """查看调度器状态（调试用）"""
    from scheduler import scheduler

    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger)
        })

    return {
        "running": scheduler.running,
        "job_count": len(scheduler.get_jobs()),
        "jobs": jobs_info
    }


# 静态文件服务
frontend_path = "/app/frontend"
if os.path.exists(frontend_path):
    # PWA 文件路由
    @app.get("/manifest.json")
    async def serve_manifest():
        return FileResponse(
            os.path.join(frontend_path, "manifest.json"),
            media_type="application/manifest+json"
        )

    @app.get("/sw.js")
    async def serve_sw():
        return FileResponse(
            os.path.join(frontend_path, "sw.js"),
            media_type="application/javascript"
        )

    # Icons 目录
    icons_path = os.path.join(frontend_path, "icons")
    if os.path.exists(icons_path):
        app.mount("/icons", StaticFiles(directory=icons_path), name="icons")

    # Static assets (JS, CSS from Vite build)
    static_path = os.path.join(frontend_path, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    # Catch-all for SPA routing (in case using React Router in the future)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        file_path = os.path.join(frontend_path, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))
