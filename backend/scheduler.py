"""
定时任务调度器
处理观影报告的定时推送（每个服务器独立配置，每日/每周/每月三个独立任务）
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Literal
from logger import get_logger

logger = get_logger("scheduler")


scheduler = AsyncIOScheduler()

ReportPeriod = Literal["daily", "weekly", "monthly"]


async def send_report_for_server(period: ReportPeriod, server_id: str):
    """发送指定服务器指定周期的观影报告"""
    from services.report import report_service
    from services.telegram import telegram_service
    from services.report_config import report_config_service
    from services.servers import server_service

    # 加载该服务器的配置
    config = report_config_service.load(server_id)

    if not config.telegram.enabled or not config.telegram.bot_token or not config.telegram.chat_id:
        logger.info(f"Scheduler [{server_id}][{period}]: Telegram not configured, skipping")
        return

    # 获取服务器配置
    server_config = await server_service.get_server(server_id)
    if not server_config:
        logger.warning(f"Scheduler [{server_id}][{period}]: Server not found, skipping")
        return

    server_name = server_config.get("name", server_id)
    period_names = {"daily": "今日", "weekly": "本周", "monthly": "本月"}
    logger.info(f"Scheduler [{server_name}][{period}]: Starting {period_names[period]} report...")

    # 获取配置的用户ID列表
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
        # 在报告标题中包含服务器名称（如果有多个服务器）
        caption = f"📊 {period_names[period]}观影报告"

        success = await telegram_service.send_photo_with_config(
            image_data,
            caption,
            config.telegram.bot_token,
            config.telegram.chat_id,
            config.telegram.proxy
        )
        if success:
            logger.info(f"Scheduler [{server_name}][{period}]: Report sent successfully")
        else:
            logger.error(f"Scheduler [{server_name}][{period}]: Failed to send report")
    except Exception as e:
        logger.error(f"Scheduler [{server_name}][{period}]: Error: {e}")


async def clean_expired_sessions():
    """清理过期会话"""
    from services.session import session_service
    cleaned = await session_service.clean_expired_sessions()
    logger.info(f"Scheduler: Cleaned {cleaned} expired sessions")


def _parse_cron(cron_str: str) -> dict:
    """解析 cron 表达式"""
    parts = cron_str.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron format: {cron_str}")
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4]
    }


def _get_job_id(server_id: str, period: str) -> str:
    """生成任务ID"""
    return f"{period}_report_{server_id}"


def _add_job(job_id: str, func, cron_str: str, args: tuple = None):
    """添加定时任务"""
    try:
        cron_params = _parse_cron(cron_str)
        trigger = CronTrigger(**cron_params)
        scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=job_id,
            args=args,
            replace_existing=True
        )
        logger.info(f"Scheduler: Added job '{job_id}' with cron '{cron_str}'")
    except Exception as e:
        logger.error(f"Scheduler: Failed to add job '{job_id}': {e}")


def _remove_all_report_jobs():
    """移除所有报告相关的定时任务"""
    jobs_to_remove = []
    for job in scheduler.get_jobs():
        if job.id.endswith("_report") or "_report_" in job.id:
            jobs_to_remove.append(job.id)

    for job_id in jobs_to_remove:
        try:
            scheduler.remove_job(job_id)
            logger.info(f"Scheduler: Removed job '{job_id}'")
        except Exception:
            pass


def setup_scheduler():
    """设置定时任务 - 为所有服务器设置独立的定时任务"""
    from services.report_config import report_config_service

    # 获取所有服务器的配置
    all_configs = report_config_service.get_all_configs()

    for server_id, config in all_configs.items():
        schedule = config.schedule

        # 每日报告
        if schedule.daily.enabled and schedule.daily.cron:
            job_id = _get_job_id(server_id, "daily")
            _add_job(job_id, send_report_for_server, schedule.daily.cron, ("daily", server_id))

        # 每周报告
        if schedule.weekly.enabled and schedule.weekly.cron:
            job_id = _get_job_id(server_id, "weekly")
            _add_job(job_id, send_report_for_server, schedule.weekly.cron, ("weekly", server_id))

        # 每月报告
        if schedule.monthly.enabled and schedule.monthly.cron:
            job_id = _get_job_id(server_id, "monthly")
            _add_job(job_id, send_report_for_server, schedule.monthly.cron, ("monthly", server_id))

    # 每小时清理过期会话
    _add_job("clean_sessions", clean_expired_sessions, "0 * * * *")

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler: Started")


def reload_scheduler():
    """重新加载调度器配置 - 重新设置所有服务器的定时任务"""
    from services.report_config import report_config_service

    # 移除所有报告相关的任务
    _remove_all_report_jobs()

    # 清除配置缓存
    report_config_service.reload()

    # 获取所有服务器的配置并重新设置
    all_configs = report_config_service.get_all_configs()

    for server_id, config in all_configs.items():
        schedule = config.schedule

        if schedule.daily.enabled and schedule.daily.cron:
            job_id = _get_job_id(server_id, "daily")
            _add_job(job_id, send_report_for_server, schedule.daily.cron, ("daily", server_id))

        if schedule.weekly.enabled and schedule.weekly.cron:
            job_id = _get_job_id(server_id, "weekly")
            _add_job(job_id, send_report_for_server, schedule.weekly.cron, ("weekly", server_id))

        if schedule.monthly.enabled and schedule.monthly.cron:
            job_id = _get_job_id(server_id, "monthly")
            _add_job(job_id, send_report_for_server, schedule.monthly.cron, ("monthly", server_id))

    logger.info("Scheduler: Reloaded")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler: Shutdown complete")
