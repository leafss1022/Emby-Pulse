"""
观影报告配置服务
管理报告推送的配置（每个服务器独立配置，持久化到 JSON 文件）
"""
import json
import os
import glob
from typing import Optional
from pydantic import BaseModel
from logger import get_logger

logger = get_logger("services.report_config")


class TelegramConfig(BaseModel):
    """Telegram 配置"""
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""
    proxy: str = ""  # 代理地址，如 http://127.0.0.1:7890 或 socks5://127.0.0.1:1080


class ScheduleItemConfig(BaseModel):
    """单个定时任务配置"""
    enabled: bool = False
    cron: str = ""


class ScheduleConfig(BaseModel):
    """定时任务配置 - 四个独立任务"""
    daily: ScheduleItemConfig = ScheduleItemConfig(cron="0 21 * * *")    # 每天21:00
    weekly: ScheduleItemConfig = ScheduleItemConfig(cron="0 21 * * 0")   # 每周日21:00
    monthly: ScheduleItemConfig = ScheduleItemConfig(cron="0 21 1 * *")  # 每月1号21:00
    yearly: ScheduleItemConfig = ScheduleItemConfig(cron="0 21 1 1 *")   # 每年1月1号21:00


class ReportConfig(BaseModel):
    """报告配置"""
    telegram: TelegramConfig = TelegramConfig()
    schedule: ScheduleConfig = ScheduleConfig()
    users: list[str] = []  # 空列表表示所有用户
    content_count: int = 5  # 热门内容数量


CONFIG_DIR = "/config"
CONFIG_PREFIX = "report_config"
# 旧的全局配置文件（用于迁移）
LEGACY_CONFIG_FILE = "/config/report_config.json"


class ReportConfigService:
    """报告配置服务 - 支持每个服务器独立配置"""

    def __init__(self):
        self._configs: dict[str, ReportConfig] = {}  # server_id -> config

    def _ensure_dir(self):
        """确保配置目录存在"""
        os.makedirs(CONFIG_DIR, exist_ok=True)

    def _get_config_file(self, server_id: str) -> str:
        """获取指定服务器的配置文件路径"""
        return f"{CONFIG_DIR}/{CONFIG_PREFIX}_{server_id}.json"

    def load(self, server_id: str) -> ReportConfig:
        """加载指定服务器的配置"""
        if server_id in self._configs:
            return self._configs[server_id]

        config_file = self._get_config_file(server_id)
        try:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    config = ReportConfig(**data)
            else:
                config = ReportConfig()
            self._configs[server_id] = config
        except Exception as e:
            logger.error(f"Error loading report config for server {server_id}: {e}")
            config = ReportConfig()
            self._configs[server_id] = config

        return config

    def save(self, server_id: str, config: ReportConfig) -> bool:
        """保存指定服务器的配置"""
        try:
            self._ensure_dir()
            config_file = self._get_config_file(server_id)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
            self._configs[server_id] = config
            return True
        except Exception as e:
            logger.error(f"Error saving report config for server {server_id}: {e}")
            return False

    def reload(self, server_id: str = None):
        """重新加载配置"""
        if server_id:
            self._configs.pop(server_id, None)
            return self.load(server_id)
        else:
            # 清除所有缓存
            self._configs.clear()

    def get_all_configs(self) -> dict[str, ReportConfig]:
        """获取所有服务器的配置（用于定时任务）"""
        configs = {}
        pattern = f"{CONFIG_DIR}/{CONFIG_PREFIX}_*.json"
        for config_file in glob.glob(pattern):
            # 从文件名提取 server_id
            filename = os.path.basename(config_file)
            # report_config_{server_id}.json
            server_id = filename[len(CONFIG_PREFIX) + 1:-5]  # 去掉前缀和 .json
            if server_id:
                configs[server_id] = self.load(server_id)
        return configs

    def migrate_legacy_config(self, default_server_id: str):
        """迁移旧的全局配置到新的服务器配置"""
        if not os.path.exists(LEGACY_CONFIG_FILE):
            return

        # 检查是否已经有新配置
        new_config_file = self._get_config_file(default_server_id)
        if os.path.exists(new_config_file):
            return

        try:
            with open(LEGACY_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 移除旧的 server_id 字段（如果存在）
                data.pop("server_id", None)
                config = ReportConfig(**data)
                self.save(default_server_id, config)
                logger.info(f"Migrated legacy report config to server {default_server_id}")
        except Exception as e:
            logger.error(f"Error migrating legacy report config: {e}")


# 单例实例
report_config_service = ReportConfigService()
