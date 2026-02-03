"""
观影报告生成服务
生成观影统计报告图片（美化版）
"""
import io
from datetime import datetime, timedelta
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional, Literal

from config import settings
from database import get_playback_db, get_count_expr, get_duration_filter, local_date
from services.users import user_service
from services.emby import emby_service


# 报告类型
ReportPeriod = Literal["daily", "weekly", "monthly", "yearly"]


class ReportService:
    """观影报告服务"""

    def __init__(self):
        # Vuetify 深色主题配色（与 Vue 前端保持一致）
        self.bg_gradient_start = (10, 13, 20)      # #0a0d14 - Vuetify background
        self.bg_gradient_end = (19, 22, 31)        # #13161f - Vuetify surface
        self.card_color = (19, 22, 31)             # #13161f - 卡片背景
        self.card_highlight = (26, 29, 42)         # #1a1d2a - 高亮卡片
        self.text_color = (248, 250, 252)          # 亮白文字
        self.secondary_color = (148, 163, 184)     # #94a3b8 - 灰色文字
        self.accent_color = (59, 130, 246)         # #3b82f6 - Vuetify primary
        self.accent_secondary = (96, 165, 250)     # #60a5fa - Vuetify secondary
        self.gold_color = (245, 158, 11)           # #f59e0b - 金色（第一名）
        self.silver_color = (203, 213, 225)        # #cbd5e1 - 银色（第二名）
        self.bronze_color = (251, 146, 60)         # #fb923c - 铜色（第三名）
        self.success_color = (34, 197, 94)         # #22c55e - Vuetify success

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取字体"""
        # 常规字体路径（按优先级排序）
        font_paths = [
            # Debian/Ubuntu fonts-noto-cjk 包的常见路径
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            # 简体中文特定字体
            "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
            "/usr/share/fonts/truetype/noto/NotoSansCJKsc-Regular.otf",
            # 其他可能的路径
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        if bold:
            bold_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf",
                "/usr/share/fonts/truetype/noto/NotoSansCJKsc-Bold.otf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
            font_paths = bold_paths + font_paths
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                # 字体文件不存在或无法读取，尝试下一个
                continue
        return ImageFont.load_default()

    def _format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if seconds < 60:
            return f"{seconds}秒"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}小时{minutes}分"
        return f"{minutes}分钟"

    def _format_duration_short(self, seconds: int) -> str:
        """格式化时长（简短）"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h{minutes}m"
        return f"{minutes}m"

    def _get_period_info(self, period: ReportPeriod) -> tuple[str, str, str]:
        """获取时间段信息：(标题, 开始日期, 副标题)"""
        now = datetime.now()
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            title = "今日观影报告"
            subtitle = now.strftime("%Y年%m月%d日")
        elif period == "weekly":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            title = "本周观影报告"
            end_of_week = start + timedelta(days=6)
            subtitle = f"{start.strftime('%m.%d')} - {end_of_week.strftime('%m.%d')}"
        elif period == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            title = "本月观影报告"
            subtitle = now.strftime("%Y年%m月")
        else:  # yearly
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            title = "年度观影报告"
            subtitle = now.strftime("%Y年")
        return title, start.strftime("%Y-%m-%d"), subtitle

    async def _get_poster_bytes(self, item_id: str, server_config: dict = None) -> Optional[bytes]:
        """获取海报图片"""
        try:
            data, _ = await emby_service.get_poster(item_id, max_height=200, max_width=140, server_config=server_config)
            return data if data else None
        except Exception:
            # 海报获取失败（网络错误、API 错误等），返回空
            return None

    def _create_gradient_background(self, width: int, height: int) -> Image.Image:
        """创建渐变背景 - 简化测试版本"""
        # 先用纯色测试，确保文字能显示
        img = Image.new("RGB", (width, height), self.bg_gradient_start)
        return img

    def _draw_rounded_rect(self, draw: ImageDraw.ImageDraw, xy: tuple, radius: int, fill: tuple):
        """绘制圆角矩形"""
        draw.rounded_rectangle(xy, radius=radius, fill=fill)

    def _draw_poster_with_shadow(self, img: Image.Image, poster_data: bytes, x: int, y: int, width: int, height: int, scale: float = 1.0):
        """绘制带阴影的海报"""
        try:
            poster = Image.open(io.BytesIO(poster_data))
            poster = poster.resize((width, height), Image.Resampling.LANCZOS)

            # 创建阴影（根据缩放调整）
            shadow_offset = int(10 * scale)
            shadow_blur = int(5 * scale)
            shadow = Image.new("RGBA", (width + shadow_offset, height + shadow_offset), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rounded_rectangle((shadow_offset // 2, shadow_offset // 2, width + shadow_offset // 2, height + shadow_offset // 2), radius=int(8 * scale), fill=(0, 0, 0, 100))
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))

            # 合成阴影
            img.paste(shadow, (x - int(3 * scale), y - int(1 * scale)), shadow)

            # 创建圆角遮罩
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0, 0, width, height), radius=int(6 * scale), fill=255)

            # 粘贴海报
            img.paste(poster, (x, y), mask)
        except Exception as e:
            # 绘制占位符
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle((x, y, x + width, y + height), radius=int(6 * scale), fill=(26, 29, 42))

    def _get_rank_color(self, rank: int) -> tuple:
        """获取排名颜色"""
        if rank == 1:
            return self.gold_color
        elif rank == 2:
            return self.silver_color
        elif rank == 3:
            return self.bronze_color
        return self.secondary_color

    async def get_stats(self, user_ids: list[str] = None, start_date: str = None, server_config: dict = None) -> dict:
        """获取统计数据"""
        async with get_playback_db(server_config) as db:
            duration_filter = get_duration_filter()
            date_col = local_date("DateCreated")

            user_filter = ""
            params_base = []
            if user_ids:
                placeholders = ",".join(["?" for _ in user_ids])
                user_filter = f"AND UserId IN ({placeholders})"
                params_base = user_ids

            date_filter = ""
            if start_date:
                date_filter = f"AND {date_col} >= date(?)"
                params_base.append(start_date)

            # 总时长
            query = f"""
                SELECT COALESCE(SUM(PlayDuration), 0)
                FROM PlaybackActivity
                WHERE 1=1 {user_filter} {date_filter} {duration_filter}
            """
            async with db.execute(query, params_base) as cursor:
                row = await cursor.fetchone()
                total_duration = row[0] or 0

            # 播放次数
            count_expr = get_count_expr()
            query = f"""
                SELECT COALESCE({count_expr}, 0)
                FROM PlaybackActivity
                WHERE 1=1 {user_filter} {date_filter} {duration_filter}
            """
            async with db.execute(query, params_base) as cursor:
                row = await cursor.fetchone()
                play_count = int(row[0] or 0)

            # 电影/剧集分类统计（时长）
            query = f"""
                SELECT ItemType, COALESCE(SUM(PlayDuration), 0)
                FROM PlaybackActivity
                WHERE 1=1 {user_filter} {date_filter} {duration_filter}
                GROUP BY ItemType
            """
            type_stats = {"Movie": {"duration": 0, "count": 0}, "Episode": {"duration": 0, "count": 0}}
            async with db.execute(query, params_base) as cursor:
                async for row in cursor:
                    item_type, duration = row
                    if item_type in type_stats:
                        type_stats[item_type]["duration"] = duration or 0

            # 电影/剧集分类统计（去重内容数量 - 同一个 ItemId 只算一次）
            query = f"""
                SELECT ItemType, COUNT(DISTINCT ItemId)
                FROM PlaybackActivity
                WHERE 1=1 {user_filter} {date_filter} {duration_filter}
                GROUP BY ItemType
            """
            async with db.execute(query, params_base) as cursor:
                async for row in cursor:
                    item_type, count = row
                    if item_type in type_stats:
                        type_stats[item_type]["count"] = int(count or 0)

        return {
            "total_duration": total_duration,
            "play_count": play_count,
            "movie_duration": type_stats["Movie"]["duration"],
            "movie_count": type_stats["Movie"]["count"],
            "episode_duration": type_stats["Episode"]["duration"],
            "episode_count": type_stats["Episode"]["count"],
        }

    async def get_top_content(self, user_ids: list[str] = None, start_date: str = None, limit: int = 5, server_config: dict = None) -> list[dict]:
        """获取热门内容排行"""
        async with get_playback_db(server_config) as db:
            duration_filter = get_duration_filter()
            count_expr = get_count_expr()
            date_col = local_date("DateCreated")

            user_filter = ""
            params = []
            if user_ids:
                placeholders = ",".join(["?" for _ in user_ids])
                user_filter = f"AND UserId IN ({placeholders})"
                params = user_ids.copy()

            date_filter = ""
            if start_date:
                date_filter = f"AND {date_col} >= date(?)"
                params.append(start_date)

            query = f"""
                SELECT ItemId, ItemName, ItemType,
                       {count_expr} as play_count,
                       COALESCE(SUM(PlayDuration), 0) as total_duration
                FROM PlaybackActivity
                WHERE 1=1 {user_filter} {date_filter} {duration_filter}
                GROUP BY ItemId, ItemName, ItemType
            """

            content_map = defaultdict(lambda: {"play_count": 0, "duration": 0, "item_id": None, "item_type": None})

            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    item_id, item_name, item_type, play_count, duration = row
                    item_name = item_name or "Unknown"

                    # 剧集按剧名聚合
                    if item_type == "Episode" and " - " in item_name:
                        key = item_name.split(" - ")[0]
                    else:
                        key = item_name

                    content_map[key]["play_count"] += int(play_count or 0)
                    content_map[key]["duration"] += duration or 0
                    if not content_map[key]["item_id"]:
                        content_map[key]["item_id"] = item_id
                        content_map[key]["item_type"] = item_type

            # 按播放次数排序
            sorted_content = sorted(content_map.items(), key=lambda x: x[1]["play_count"], reverse=True)[:limit]

            results = []
            for name, data in sorted_content:
                poster_id = data["item_id"]
                if data["item_type"] == "Episode":
                    item_info = await emby_service.get_item_info(data["item_id"], server_config)
                    if item_info.get("SeriesId"):
                        poster_id = item_info["SeriesId"]

                results.append({
                    "name": name,
                    "play_count": data["play_count"],
                    "duration": data["duration"],
                    "item_type": data["item_type"],
                    "poster_id": poster_id
                })

            return results

    async def generate_report_image(
        self,
        user_ids: list[str] = None,
        period: ReportPeriod = "weekly",
        content_count: int = 5,
        server_config: dict = None,
        scale: float = 2.0
    ) -> bytes:
        """生成观影报告图片（现代化重设计版本）

        Args:
            scale: 缩放因子，默认2.0表示2倍分辨率（960px宽）
        """
        title, start_date, subtitle = self._get_period_info(period)
        stats = await self.get_stats(user_ids, start_date, server_config)
        top_content = await self.get_top_content(user_ids, start_date, content_count, server_config)

        # 基础尺寸
        base_width = 540
        width = int(base_width * scale)

        # 动态计算高度
        base_padding = 20
        padding = int(base_padding * scale)

        # 各部分高度
        header_h = int(100 * scale)
        stats_card_h = int(140 * scale)
        section_title_h = int(40 * scale)
        content_item_h = int(120 * scale)
        footer_h = int(50 * scale)
        spacing = int(16 * scale)

        content_count_actual = len(top_content) if top_content else 0
        total_height = (header_h + spacing +
                       stats_card_h + spacing +
                       section_title_h +
                       (content_item_h + int(12 * scale)) * max(content_count_actual, 1) + spacing +
                       footer_h)

        # 创建背景
        img = self._create_gradient_background(width, total_height)
        draw = ImageDraw.Draw(img)

        # 字体
        font_header = self._get_font(int(32 * scale), bold=True)
        font_subtitle = self._get_font(int(14 * scale))
        font_stat_value = self._get_font(int(28 * scale), bold=True)
        font_stat_label = self._get_font(int(13 * scale))
        font_section = self._get_font(int(18 * scale), bold=True)
        font_name = self._get_font(int(16 * scale), bold=True)
        font_info = self._get_font(int(13 * scale))
        font_rank = self._get_font(int(24 * scale), bold=True)
        font_badge = self._get_font(int(11 * scale), bold=True)

        y = padding

        # === 顶部标题卡片 ===
        header_card_y = y
        self._draw_rounded_rect(draw, (padding, header_card_y, width - padding, header_card_y + header_h),
                               int(16 * scale), self.card_color)

        # 标题文字
        title_y = header_card_y + int(24 * scale)
        draw.text((padding + int(20 * scale), title_y), title, font=font_header, fill=self.text_color)

        # 副标题和装饰线
        subtitle_y = title_y + int(42 * scale)
        draw.text((padding + int(20 * scale), subtitle_y), subtitle, font=font_subtitle, fill=self.accent_color)

        # 右侧装饰图标区域
        icon_x = width - padding - int(70 * scale)
        icon_y = header_card_y + int(30 * scale)
        icon_size = int(40 * scale)
        # 主图标圆
        draw.ellipse((icon_x, icon_y, icon_x + icon_size, icon_y + icon_size), fill=self.accent_color)

        y = header_card_y + header_h + spacing

        # === 统计卡片（三栏布局）===
        stats_y = y
        self._draw_rounded_rect(draw, (padding, stats_y, width - padding, stats_y + stats_card_h),
                               int(16 * scale), self.card_color)

        col_width = (width - padding * 2 - int(40 * scale)) // 3
        col_x = [padding + int(20 * scale),
                padding + int(20 * scale) + col_width + int(20 * scale),
                padding + int(20 * scale) + col_width * 2 + int(40 * scale)]

        # 统计数据
        stat_items = [
            (self._format_duration(stats["total_duration"]), "观看时长", self.accent_color),
            (f"{stats['play_count']}", "播放次数", self.accent_secondary),
            (f"{stats['movie_count'] + stats['episode_count']}", "观看内容", self.success_color)
        ]

        for i, (value, label, color) in enumerate(stat_items):
            # 数值
            val_y = stats_y + int(35 * scale)
            bbox = draw.textbbox((0, 0), value, font=font_stat_value)
            val_w = bbox[2] - bbox[0]
            draw.text((col_x[i] + col_width // 2 - val_w // 2, val_y), value,
                     font=font_stat_value, fill=color)

            # 标签
            label_y = val_y + int(38 * scale)
            bbox = draw.textbbox((0, 0), label, font=font_stat_label)
            label_w = bbox[2] - bbox[0]
            draw.text((col_x[i] + col_width // 2 - label_w // 2, label_y), label,
                     font=font_stat_label, fill=self.secondary_color)

        # 底部细分信息
        detail_y = stats_y + int(105 * scale)
        movie_text = f"电影 {stats['movie_count']} · {self._format_duration_short(stats['movie_duration'])}"
        episode_text = f"剧集 {stats['episode_count']} · {self._format_duration_short(stats['episode_duration'])}"

        bbox1 = draw.textbbox((0, 0), movie_text, font=font_info)
        bbox2 = draw.textbbox((0, 0), episode_text, font=font_info)
        total_w = (bbox1[2] - bbox1[0]) + int(40 * scale) + (bbox2[2] - bbox2[0])
        start_x = (width - total_w) // 2

        draw.text((start_x, detail_y), movie_text, font=font_info, fill=self.secondary_color)
        draw.text((start_x + (bbox1[2] - bbox1[0]) + int(40 * scale), detail_y), episode_text,
                 font=font_info, fill=self.secondary_color)

        y = stats_y + stats_card_h + spacing

        # === 热门内容区域 ===
        if top_content:
            # 区块标题
            draw.text((padding + int(8 * scale), y), "热门内容", font=font_section, fill=self.text_color)
            y += section_title_h

            for idx, item in enumerate(top_content):
                # 每次循环开始都重新创建draw对象，确保其有效性
                draw = ImageDraw.Draw(img)

                item_y = y

                # 卡片背景（第一名特殊高亮）
                card_fill = self.card_highlight if idx == 0 else self.card_color
                self._draw_rounded_rect(draw, (padding, item_y, width - padding, item_y + content_item_h),
                                       int(14 * scale), card_fill)

                # 排名徽章（圆形）
                rank = idx + 1
                rank_color = self._get_rank_color(rank)
                badge_x = padding + int(18 * scale)
                badge_y = item_y + int(20 * scale)
                badge_size = int(36 * scale)

                # 徽章背景
                draw.ellipse((badge_x, badge_y, badge_x + badge_size, badge_y + badge_size), fill=rank_color)

                # 排名数字
                rank_text = str(rank)
                bbox = draw.textbbox((0, 0), rank_text, font=font_rank)
                text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text((badge_x + badge_size // 2 - text_w // 2,
                          badge_y + badge_size // 2 - text_h // 2 - int(2 * scale)),
                         rank_text, font=font_rank, fill=(255, 255, 255))

                # 海报
                poster_x = badge_x + badge_size + int(16 * scale)
                poster_y = item_y + int(15 * scale)
                poster_w, poster_h = int(65 * scale), int(90 * scale)

                poster_data = await self._get_poster_bytes(item["poster_id"], server_config)
                if poster_data:
                    self._draw_poster_with_shadow(img, poster_data, poster_x, poster_y, poster_w, poster_h, scale)
                    # paste操作后必须重新创建draw对象
                    draw = ImageDraw.Draw(img)
                else:
                    draw.rounded_rectangle((poster_x, poster_y, poster_x + poster_w, poster_y + poster_h),
                                         radius=int(8 * scale), fill=(26, 29, 42))

                # 内容信息区
                info_x = poster_x + poster_w + int(16 * scale)
                info_y = item_y + int(22 * scale)
                max_text_w = width - info_x - padding - int(16 * scale)

                # 标题（确保正确编码）
                name = str(item["name"])  # 确保是字符串
                # 截断过长标题
                while True:
                    bbox = draw.textbbox((0, 0), name, font=font_name)
                    if bbox[2] - bbox[0] <= max_text_w or len(name) <= 3:
                        break
                    name = name[:-1]
                if len(name) < len(item["name"]):
                    name = name.rstrip() + "..."

                draw.text((info_x, info_y), name, font=font_name, fill=self.text_color)

                # 类型徽章
                type_map = {"Movie": "电影", "Episode": "剧集", "Audio": "音乐"}
                type_text = type_map.get(item["item_type"], "视频")
                badge_y = info_y + int(32 * scale)

                bbox = draw.textbbox((0, 0), type_text, font=font_badge)
                badge_w = bbox[2] - bbox[0] + int(16 * scale)
                badge_h = int(22 * scale)

                # 类型徽章背景（使用accent color）
                draw.rounded_rectangle((info_x, badge_y, info_x + badge_w, badge_y + badge_h),
                                      radius=int(6 * scale), fill=self.accent_color)
                draw.text((info_x + int(8 * scale), badge_y + int(3 * scale)), type_text,
                         font=font_badge, fill=(255, 255, 255))

                # 播放统计
                stats_y_pos = badge_y + badge_h + int(12 * scale)
                stats_text = f"{item['play_count']} 次播放 · {self._format_duration_short(item['duration'])}"
                draw.text((info_x, stats_y_pos), stats_text, font=font_info, fill=self.secondary_color)

                y += content_item_h + int(12 * scale)
        else:
            # 空状态
            empty_h = int(120 * scale)
            self._draw_rounded_rect(draw, (padding, y, width - padding, y + empty_h),
                                   int(14 * scale), self.card_color)
            empty_text = "暂无观看记录"
            bbox = draw.textbbox((0, 0), empty_text, font=font_section)
            text_w = bbox[2] - bbox[0]
            draw.text(((width - text_w) // 2, y + int(50 * scale)), empty_text,
                     font=font_section, fill=self.secondary_color)
            y += empty_h + spacing

        # === 底部水印 ===
        watermark = "Generated by Emby Stats"
        bbox = draw.textbbox((0, 0), watermark, font=font_info)
        draw.text(((width - (bbox[2] - bbox[0])) // 2, total_height - int(32 * scale)),
                 watermark, font=font_info, fill=self.secondary_color)

        # 输出
        output = io.BytesIO()
        img.save(output, format="PNG", quality=95, optimize=True)
        output.seek(0)
        return output.getvalue()

    async def get_report_users(self, configured_users: list[str] = None, server_config: dict = None) -> list[tuple[str, str]]:
        """获取报告用户列表"""
        user_map = await user_service.get_user_map(server_config)
        if configured_users:
            result = []
            for user in configured_users:
                for uid, uname in user_map.items():
                    if user.lower() == uname.lower() or user.lower() == uid.lower():
                        result.append((uid, uname))
                        break
            return result
        return list(user_map.items())


report_service = ReportService()
