"""
Telegram 推送服务
处理向 Telegram 发送消息和图片
"""
import httpx
from config import settings
from logger import get_logger

logger = get_logger("services.telegram")


class TelegramService:
    """Telegram 推送服务"""

    def __init__(self):
        self.base_url = "https://api.telegram.org"

    def is_configured(self) -> bool:
        """检查 Telegram 是否已配置"""
        return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """发送文本消息"""
        if not self.is_configured():
            logger.warning("Telegram not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": settings.TELEGRAM_CHAT_ID,
                        "text": text,
                        "parse_mode": parse_mode
                    },
                    timeout=30
                )
                if resp.status_code == 200:
                    return True
                else:
                    logger.error(f"Telegram send message failed: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_photo(self, photo: bytes, caption: str = "", parse_mode: str = "HTML") -> bool:
        """发送图片"""
        if not self.is_configured():
            logger.warning("Telegram not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                files = {"photo": ("report.png", photo, "image/png")}
                data = {
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                }
                if caption:
                    data["caption"] = caption
                    data["parse_mode"] = parse_mode

                resp = await client.post(
                    f"{self.base_url}/bot{settings.TELEGRAM_BOT_TOKEN}/sendPhoto",
                    data=data,
                    files=files,
                    timeout=60
                )
                if resp.status_code == 200:
                    return True
                else:
                    logger.error(f"Telegram send photo failed: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {e}")
            return False

    async def send_media_group(self, photos: list[bytes], caption: str = "") -> bool:
        """发送多张图片（媒体组）"""
        if not self.is_configured():
            logger.warning("Telegram not configured")
            return False

        if not photos:
            return False

        try:
            async with httpx.AsyncClient() as client:
                # 构建媒体组
                media = []
                files = {}
                for i, photo in enumerate(photos):
                    attach_name = f"photo{i}"
                    media.append({
                        "type": "photo",
                        "media": f"attach://{attach_name}",
                        "caption": caption if i == 0 else "",
                        "parse_mode": "HTML" if i == 0 and caption else None
                    })
                    files[attach_name] = (f"report_{i}.png", photo, "image/png")

                import json
                data = {
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "media": json.dumps(media)
                }

                resp = await client.post(
                    f"{self.base_url}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMediaGroup",
                    data=data,
                    files=files,
                    timeout=120
                )
                if resp.status_code == 200:
                    return True
                else:
                    logger.error(f"Telegram send media group failed: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram media group: {e}")
            return False

    # ==================== 使用自定义配置的方法 ====================

    async def send_message_with_config(self, text: str, bot_token: str, chat_id: str, proxy: str = "", parse_mode: str = "HTML") -> bool:
        """使用指定配置发送文本消息"""
        try:
            async with httpx.AsyncClient(proxies=proxy if proxy else None) as client:
                resp = await client.post(
                    f"{self.base_url}/bot{bot_token}/sendMessage",
                    json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                    timeout=30
                )
                if resp.status_code == 200:
                    return True
                else:
                    logger.error(f"Telegram send message failed: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_photo_with_config(self, photo: bytes, caption: str, bot_token: str, chat_id: str, proxy: str = "", parse_mode: str = "HTML") -> bool:
        """使用指定配置发送图片"""
        try:
            async with httpx.AsyncClient(proxies=proxy if proxy else None) as client:
                files = {"photo": ("report.png", photo, "image/png")}
                data = {"chat_id": chat_id}
                if caption:
                    data["caption"] = caption
                    data["parse_mode"] = parse_mode

                resp = await client.post(
                    f"{self.base_url}/bot{bot_token}/sendPhoto",
                    data=data,
                    files=files,
                    timeout=60
                )
                if resp.status_code == 200:
                    return True
                else:
                    logger.error(f"Telegram send photo failed: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {e}")
            return False


# 单例实例
telegram_service = TelegramService()
