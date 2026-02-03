"""
简化版报告生成服务 - 确保可靠工作
"""
import io
from datetime import datetime, timedelta
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Literal

from database import get_playback_db, get_count_expr, get_duration_filter, local_date
from services.users import user_service
from services.emby import emby_service


ReportPeriod = Literal["daily", "weekly", "monthly", "yearly"]


class ReportServiceSimple:
    """简化报告服务"""

    def __init__(self):
        self.bg_gradient_start = (20, 25, 35)    # 渐变起始色
        self.bg_gradient_end = (35, 40, 50)      # 渐变结束色
        self.card_color = (45, 50, 60)           # 卡片颜色
        self.text_color = (255, 255, 255)        # 白色文字
        self.accent_color = (100, 150, 255)      # 蓝色强调
        self.gold_color = (245, 158, 11)         # 金色（第一名）
        self.silver_color = (203, 213, 225)      # 银色（第二名）
        self.bronze_color = (251, 146, 60)       # 铜色（第三名）

    def _get_font(self, size: int):
        """获取字体"""
        paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        for path in paths:
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
        return ImageFont.load_default()

    def _format_duration(self, seconds: int) -> str:
        """格式化时长"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{minutes}分钟"

    def _get_period_info(self, period: ReportPeriod):
        """获取时间段信息"""
        now = datetime.now()
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            title = "今日观影报告"
        elif period == "weekly":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            title = "本周观影报告"
        elif period == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            title = "本月观影报告"
        else:  # yearly
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            title = "年度观影报告"
        return title, start.strftime("%Y-%m-%d")

    def _get_rank_color(self, rank: int) -> tuple:
        """获取排名颜色"""
        if rank == 1:
            return self.gold_color
        elif rank == 2:
            return self.silver_color
        elif rank == 3:
            return self.bronze_color
        return self.accent_color

    def _create_gradient_bg(self, width: int, height: int) -> Image.Image:
        """创建渐变背景"""
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        # 垂直渐变
        r1, g1, b1 = self.bg_gradient_start
        r2, g2, b2 = self.bg_gradient_end

        for y in range(height):
            # 计算当前行的颜色
            ratio = y / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)

            draw.line([(0, y), (width, y)], fill=(r, g, b))

        return img

    def _draw_poster_with_shadow(self, img: Image.Image, poster_data: bytes, x: int, y: int, width: int, height: int, scale: float = 1.0):
        """绘制带圆角和阴影的海报"""
        try:
            poster = Image.open(io.BytesIO(poster_data))
            poster = poster.resize((width, height), Image.Resampling.LANCZOS)

            # 创建圆角遮罩
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0, 0, width, height), radius=int(8 * scale), fill=255)

            # 创建轻微的阴影
            shadow_offset = int(4 * scale)   # 减小偏移
            shadow_blur = int(8 * scale)     # 减小模糊
            shadow = Image.new("RGBA", (width + shadow_offset * 2, height + shadow_offset * 2), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rounded_rectangle(
                (shadow_offset, shadow_offset, width + shadow_offset, height + shadow_offset),
                radius=int(8 * scale),
                fill=(0, 0, 0, 80)  # 降低透明度
            )

            # 应用模糊
            from PIL import ImageFilter
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))

            # 转换主图为RGBA以支持透明度合成
            if img.mode != "RGBA":
                img_rgba = img.convert("RGBA")
            else:
                img_rgba = img

            # 粘贴阴影
            img_rgba.paste(shadow, (x - shadow_offset, y - shadow_offset), shadow)

            # 粘贴海报
            if poster.mode != "RGBA":
                poster = poster.convert("RGBA")
            img_rgba.paste(poster, (x, y), mask)

            # 转回RGB
            if img.mode == "RGB":
                return img_rgba.convert("RGB")
            return img_rgba

        except Exception as e:
            return img

    def _draw_card_with_shadow(self, draw: ImageDraw.ImageDraw, img: Image.Image, x: int, y: int, width: int, height: int, radius: int, fill: tuple, scale: float = 1.0):
        """绘制带阴影的卡片"""
        # 创建阴影
        shadow_offset = int(4 * scale)
        shadow_blur = int(12 * scale)
        shadow = Image.new("RGBA", (width + shadow_offset * 2, height + shadow_offset * 2), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            (shadow_offset, shadow_offset, width + shadow_offset, height + shadow_offset),
            radius=radius,
            fill=(0, 0, 0, 100)
        )

        # 应用模糊
        from PIL import ImageFilter
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))

        # 转换为RGBA
        if img.mode != "RGBA":
            img_rgba = img.convert("RGBA")
        else:
            img_rgba = img

        # 粘贴阴影
        img_rgba.paste(shadow, (x - shadow_offset, y - shadow_offset), shadow)

        # 转回RGB并绘制卡片
        img_rgb = img_rgba.convert("RGB")
        draw_new = ImageDraw.Draw(img_rgb)
        draw_new.rounded_rectangle((x, y, x + width, y + height), radius=radius, fill=fill)

        return img_rgb

    async def _get_poster_bytes(self, item_id: str, item_type: str, server_config: dict = None) -> Optional[bytes]:
        """获取海报图片"""
        try:
            data, _ = await emby_service.get_poster(item_id, max_height=180, max_width=120, server_config=server_config)
            return data if data else None
        except:
            return None

    async def get_stats(self, user_ids=None, start_date=None, server_config=None):
        """获取统计数据"""
        async with get_playback_db(server_config) as db:
            duration_filter = get_duration_filter()
            date_col = local_date("DateCreated")

            user_filter = ""
            params = []
            if user_ids:
                placeholders = ",".join(["?" for _ in user_ids])
                user_filter = f"AND UserId IN ({placeholders})"
                params = user_ids

            date_filter = ""
            if start_date:
                date_filter = f"AND {date_col} >= date(?)"
                params.append(start_date)

            # 总时长
            query = f"SELECT COALESCE(SUM(PlayDuration), 0) FROM PlaybackActivity WHERE 1=1 {user_filter} {date_filter} {duration_filter}"
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                total_duration = row[0] or 0

            # 播放次数
            count_expr = get_count_expr()
            query = f"SELECT COALESCE({count_expr}, 0) FROM PlaybackActivity WHERE 1=1 {user_filter} {date_filter} {duration_filter}"
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                play_count = int(row[0] or 0)

            # 内容数量
            query = f"SELECT COUNT(DISTINCT ItemId) FROM PlaybackActivity WHERE 1=1 {user_filter} {date_filter} {duration_filter}"
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                item_count = int(row[0] or 0)

            return {
                "total_duration": total_duration,
                "play_count": play_count,
                "item_count": item_count
            }

    async def get_top_content(self, user_ids=None, start_date=None, limit=5, server_config=None):
        """获取热门内容"""
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
                SELECT ItemId, ItemName, ItemType, {count_expr} as play_count, COALESCE(SUM(PlayDuration), 0) as duration
                FROM PlaybackActivity
                WHERE 1=1 {user_filter} {date_filter} {duration_filter}
                GROUP BY ItemId, ItemName, ItemType
                ORDER BY play_count DESC
            """

            # 使用字典聚合剧集
            content_map = {}
            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    item_id = row[0]
                    item_name = row[1] or "Unknown"
                    item_type = row[2]
                    play_count = int(row[3] or 0)
                    duration = int(row[4] or 0)

                    # 剧集按剧名聚合（去掉 " - S01E01" 部分）
                    if item_type == "Episode" and " - " in item_name:
                        key = item_name.split(" - ")[0]
                    else:
                        key = item_name

                    # 聚合播放次数和时长
                    if key in content_map:
                        content_map[key]["count"] += play_count
                        content_map[key]["duration"] += duration
                    else:
                        content_map[key] = {
                            "name": key,
                            "count": play_count,
                            "duration": duration,
                            "item_id": item_id,
                            "item_type": item_type
                        }

            # 按播放次数排序并限制数量
            results = sorted(content_map.values(), key=lambda x: x["count"], reverse=True)[:limit]

            # 对于剧集，获取剧集的 SeriesId 用于显示整部剧的海报
            for item in results:
                if item["item_type"] == "Episode":
                    try:
                        item_info = await emby_service.get_item_info(item["item_id"], server_config)
                        if item_info.get("SeriesId"):
                            item["poster_id"] = item_info["SeriesId"]
                        else:
                            item["poster_id"] = item["item_id"]
                    except:
                        item["poster_id"] = item["item_id"]
                else:
                    item["poster_id"] = item["item_id"]

            return results

    async def generate_report_image(self, user_ids=None, period="weekly", content_count=5, server_config=None, scale=1.5):
        """生成报告图片 - 带海报的美化版本"""
        title, start_date = self._get_period_info(period)
        stats = await self.get_stats(user_ids, start_date, server_config)
        top_content = await self.get_top_content(user_ids, start_date, content_count, server_config)

        # 尺寸计算
        width = int(600 * scale)
        padding = int(30 * scale)

        # 各部分高度
        header_h = int(80 * scale)
        stats_h = int(120 * scale)
        section_h = int(50 * scale)
        item_h = int(140 * scale)
        item_spacing = int(15 * scale)
        footer_h = int(40 * scale)

        # 动态计算总高度
        content_count_actual = len(top_content) if top_content else 1

        # 总高度 = 顶部padding + 标题 + 统计卡片 + 间距 + 热门内容标题 + (内容项 + 间距) * N + 底部水印 + 底部padding
        height = int(
            padding +                                              # 顶部padding
            header_h +                                            # 标题区
            stats_h + int(30 * scale) +                           # 统计卡片 + 间距
            section_h +                                           # "热门内容"标题
            (item_h + item_spacing) * content_count_actual +      # 所有内容项和它们之间的间距
            footer_h +                                            # 底部水印
            padding                                               # 底部padding
        )

        # 创建渐变背景
        img = self._create_gradient_bg(width, height)
        draw = ImageDraw.Draw(img)

        # 加载字体
        font_title = self._get_font(int(40 * scale))
        font_big = self._get_font(int(26 * scale))      # 增大数值字体
        font_medium = self._get_font(int(22 * scale))
        font_small = self._get_font(int(18 * scale))

        y = padding

        # === 标题 ===
        draw.text((width // 2, y + int(30 * scale)), title, font=font_title, fill=self.text_color, anchor="mm")
        y += header_h

        # === 统计卡片（三栏） ===
        card_y = y
        card_w = (width - padding * 2 - int(40 * scale)) // 3

        stats_data = [
            (self._format_duration(stats["total_duration"]), "观看时长"),
            (str(stats["play_count"]), "播放次数"),
            (str(stats["item_count"]), "观看内容")
        ]

        for i, (value, label) in enumerate(stats_data):
            x = padding + i * (card_w + int(20 * scale))
            # 卡片背景（带阴影）
            img = self._draw_card_with_shadow(draw, img, x, card_y, card_w, stats_h, int(12 * scale), self.card_color, scale)
            draw = ImageDraw.Draw(img)

            # 数值（居中）
            draw.text(
                (x + card_w // 2, card_y + int(35 * scale)),
                value,
                font=font_big,
                fill=self.accent_color,
                anchor="mm"
            )
            # 标签（居中）
            draw.text(
                (x + card_w // 2, card_y + int(75 * scale)),
                label,
                font=font_small,
                fill=self.text_color,
                anchor="mm"
            )

        y += stats_h + int(30 * scale)

        # === 热门内容标题 ===
        draw.text((padding + int(10 * scale), y + int(20 * scale)), "热门内容", font=font_medium, fill=self.text_color)
        y += section_h

        # === 热门内容列表 ===
        if top_content:
            for idx, item in enumerate(top_content):
                item_y = y
                rank = idx + 1
                rank_color = self._get_rank_color(rank)

                # 内容卡片背景（带阴影）
                img = self._draw_card_with_shadow(draw, img, padding, item_y, width - padding * 2, item_h, int(10 * scale), self.card_color, scale)
                draw = ImageDraw.Draw(img)

                # 排名圆圈
                rank_x = padding + int(20 * scale)
                rank_y = item_y + int(20 * scale)
                rank_size = int(40 * scale)
                draw.ellipse(
                    (rank_x, rank_y, rank_x + rank_size, rank_y + rank_size),
                    fill=rank_color
                )
                # 排名数字
                draw.text(
                    (rank_x + rank_size // 2, rank_y + rank_size // 2),
                    str(rank),
                    font=font_medium,
                    fill=(255, 255, 255),
                    anchor="mm"
                )

                # 海报区域
                poster_x = rank_x + rank_size + int(20 * scale)
                poster_y = item_y + int(15 * scale)
                poster_w = int(80 * scale)
                poster_h = int(110 * scale)

                # 获取并绘制海报
                poster_data = await self._get_poster_bytes(item["poster_id"], item["item_type"], server_config)
                if poster_data:
                    img = self._draw_poster_with_shadow(img, poster_data, poster_x, poster_y, poster_w, poster_h, scale)
                    # 重新创建 draw 对象
                    draw = ImageDraw.Draw(img)
                else:
                    # 绘制占位符
                    draw.rounded_rectangle(
                        (poster_x, poster_y, poster_x + poster_w, poster_y + poster_h),
                        radius=int(8 * scale),
                        fill=(50, 50, 60)
                    )

                # 文字信息区域
                info_x = poster_x + poster_w + int(15 * scale)
                info_y = item_y + int(30 * scale)
                max_text_width = width - info_x - padding - int(10 * scale)

                # 标题（截断过长文字）
                name = item["name"]
                while True:
                    bbox = draw.textbbox((0, 0), name, font=font_medium)
                    text_w = bbox[2] - bbox[0]
                    if text_w <= max_text_width or len(name) <= 3:
                        break
                    name = name[:-1]
                if len(name) < len(item["name"]):
                    name = name.rstrip() + "..."

                draw.text((info_x, info_y), name, font=font_medium, fill=self.text_color)

                # 类型标签
                type_map = {"Movie": "电影", "Episode": "剧集", "Audio": "音乐"}
                type_text = type_map.get(item["item_type"], "视频")
                type_y = info_y + int(35 * scale)

                bbox = draw.textbbox((0, 0), type_text, font=font_small)
                badge_w = bbox[2] - bbox[0] + int(16 * scale)
                badge_h = int(24 * scale)

                draw.rounded_rectangle(
                    (info_x, type_y, info_x + badge_w, type_y + badge_h),
                    radius=int(6 * scale),
                    fill=self.accent_color
                )
                draw.text(
                    (info_x + int(8 * scale), type_y + int(3 * scale)),
                    type_text,
                    font=font_small,
                    fill=(255, 255, 255)
                )

                # 播放统计（次数 + 时长）
                count_y = type_y + badge_h + int(10 * scale)
                duration_text = self._format_duration(item['duration'])
                stats_text = f"{item['count']} 次播放 · {duration_text}"
                draw.text(
                    (info_x, count_y),
                    stats_text,
                    font=font_small,
                    fill=(180, 180, 180)
                )

                y += item_h + item_spacing
        else:
            # 空状态
            draw.text(
                (width // 2, y + int(60 * scale)),
                "暂无观看记录",
                font=font_medium,
                fill=(120, 120, 130),
                anchor="mm"
            )
            y += int(120 * scale)

        # === 底部水印 ===
        watermark = "Generated by Emby Stats"
        bbox = draw.textbbox((0, 0), watermark, font=font_small)
        draw.text(
            ((width - (bbox[2] - bbox[0])) // 2, height - footer_h // 2),
            watermark,
            font=font_small,
            fill=(100, 100, 110)
        )

        # 输出
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        return output.getvalue()

    async def get_report_users(self, configured_users=None, server_config=None):
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


report_service_simple = ReportServiceSimple()
