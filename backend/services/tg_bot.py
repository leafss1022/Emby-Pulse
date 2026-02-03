"""
Telegram Bot 交互服务
处理用户命令和交互，支持账户绑定和个人报告查询
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)
from typing import Optional
import json
import os

from services.tg_binding import tg_binding_service
from services.emby import emby_service
from services.servers import server_service
from services.report import report_service
from services.report_config import report_config_service
from logger import get_logger

logger = get_logger("services.tg_bot")

# Bot 配置文件路径
BOT_CONFIG_FILE = "/config/tg_bot_config.json"

# 会话状态
SELECTING_SERVER, WAITING_USERNAME, WAITING_PASSWORD = range(3)


class TgBotConfig:
    """Bot 配置管理"""

    def __init__(self):
        self._config = None

    def load(self) -> dict:
        """加载配置"""
        if self._config:
            return self._config

        default_config = {
            "enabled": False,
            "bot_token": "",
            "default_period": "monthly"
        }

        if os.path.exists(BOT_CONFIG_FILE):
            try:
                with open(BOT_CONFIG_FILE, "r") as f:
                    self._config = {**default_config, **json.load(f)}
            except:
                self._config = default_config
        else:
            self._config = default_config

        return self._config

    def save(self, config: dict) -> bool:
        """保存配置"""
        try:
            os.makedirs(os.path.dirname(BOT_CONFIG_FILE), exist_ok=True)
            with open(BOT_CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            self._config = config
            return True
        except Exception as e:
            logger.error(f"Error saving bot config: {e}")
            return False

    def reload(self):
        """重新加载配置"""
        self._config = None


bot_config = TgBotConfig()


class TgBotService:
    """Telegram Bot 服务"""

    def __init__(self):
        self.application: Optional[Application] = None
        self._running = False
        # 用于存储用户绑定过程中的临时数据
        self._bind_sessions = {}

    async def start(self):
        """启动 Bot"""
        config = bot_config.load()
        if not config.get("enabled") or not config.get("bot_token"):
            logger.info("TgBot: Not configured or disabled")
            return

        try:
            # 初始化绑定数据库
            await tg_binding_service.init_db()

            # 创建 Application
            self.application = Application.builder().token(config["bot_token"]).build()

            # 绑定会话处理器
            bind_handler = ConversationHandler(
                entry_points=[CommandHandler("bind", self.cmd_bind)],
                states={
                    SELECTING_SERVER: [CallbackQueryHandler(self.bind_server_selected, pattern="^bind_server_")],
                    WAITING_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.bind_username_received)],
                    WAITING_PASSWORD: [
                        CommandHandler("skip", self.bind_skip_password),
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.bind_password_received)
                    ],
                },
                fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
                per_user=True,
                per_chat=True
            )

            # 注册命令处理器
            self.application.add_handler(CommandHandler("start", self.cmd_start))
            self.application.add_handler(bind_handler)
            self.application.add_handler(CommandHandler("unbind", self.cmd_unbind))
            self.application.add_handler(CommandHandler("report", self.cmd_report))
            self.application.add_handler(CommandHandler("myinfo", self.cmd_myinfo))
            self.application.add_handler(CommandHandler("help", self.cmd_help))

            # 报告周期选择回调
            self.application.add_handler(CallbackQueryHandler(self.report_period_selected, pattern="^report_"))

            # 解绑确认回调
            self.application.add_handler(CallbackQueryHandler(self.unbind_confirmed, pattern="^unbind_"))

            # 启动 polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)

            # 设置 Bot 菜单命令
            commands = [
                BotCommand("start", "开始使用"),
                BotCommand("bind", "绑定 Emby 账户"),
                BotCommand("unbind", "解除绑定"),
                BotCommand("report", "获取观影报告"),
                BotCommand("myinfo", "查看绑定状态"),
                BotCommand("help", "帮助信息"),
            ]
            await self.application.bot.set_my_commands(commands)

            self._running = True
            logger.info("TgBot: Started successfully")

        except Exception as e:
            logger.error(f"TgBot: Failed to start: {e}")
            self._running = False

    async def stop(self):
        """停止 Bot"""
        if self.application and self._running:
            try:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                self._running = False
                logger.info("TgBot: Stopped")
            except Exception as e:
                logger.error(f"TgBot: Error stopping: {e}")

    def is_running(self) -> bool:
        """检查 Bot 是否运行中"""
        return self._running

    # ==================== 命令处理器 ====================

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        welcome_text = (
            f"👋 你好，{user.first_name}！\n\n"
            "我是 Emby Stats 观影报告机器人，可以帮你查看个人观影统计。\n\n"
            "📋 可用命令：\n"
            "/bind - 绑定 Emby 账户\n"
            "/unbind - 解除绑定\n"
            "/report - 获取观影报告\n"
            "/myinfo - 查看绑定状态\n"
            "/help - 帮助信息\n\n"
            "请先使用 /bind 绑定你的 Emby 账户。"
        )
        await update.message.reply_text(welcome_text)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        help_text = (
            "📖 使用帮助\n\n"
            "/bind - 绑定 Emby 账户\n"
            "  绑定后可以查看个人观影报告\n\n"
            "/unbind - 解除绑定\n"
            "  解除当前账户绑定\n\n"
            "/report - 获取观影报告\n"
            "  查看个人观影统计报告\n\n"
            "/myinfo - 查看绑定状态\n"
            "  显示当前绑定的账户信息\n\n"
            "/cancel - 取消当前操作\n"
            "  在绑定过程中可以使用此命令取消"
        )
        await update.message.reply_text(help_text)

    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /cancel 命令"""
        user_id = str(update.effective_user.id)
        if user_id in self._bind_sessions:
            del self._bind_sessions[user_id]
        await update.message.reply_text("❌ 操作已取消")
        return ConversationHandler.END

    # ==================== 绑定流程 ====================

    async def cmd_bind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /bind 命令 - 开始绑定流程"""
        user_id = str(update.effective_user.id)

        # 获取服务器列表
        servers = await server_service.get_all_servers()
        if not servers:
            await update.message.reply_text("❌ 暂无可用的 Emby 服务器，请联系管理员。")
            return ConversationHandler.END

        # 获取用户已绑定的服务器ID列表
        bound_server_ids = await tg_binding_service.get_bound_server_ids(user_id)

        # 过滤出未绑定的服务器
        unbound_servers = [s for s in servers if s["id"] not in bound_server_ids]

        if not unbound_servers:
            # 所有服务器都已绑定
            bindings = await tg_binding_service.get_user_bindings(user_id)
            binding_list = "\n".join([f"  • {b['emby_username']}" for b in bindings])
            await update.message.reply_text(
                f"✅ 你已绑定所有可用服务器的账户：\n{binding_list}\n\n"
                "如需重新绑定某个服务器，请先使用 /unbind 解除绑定。"
            )
            return ConversationHandler.END

        # 如果只有一个未绑定的服务器，直接进入用户名输入
        if len(unbound_servers) == 1:
            self._bind_sessions[user_id] = {
                "server_id": unbound_servers[0]["id"],
                "server_name": unbound_servers[0]["name"]
            }
            await update.message.reply_text(
                f"📡 服务器：{unbound_servers[0]['name']}\n\n"
                "请输入你的 Emby 用户名："
            )
            return WAITING_USERNAME

        # 多个未绑定的服务器，显示选择按钮
        keyboard = []
        for server in unbound_servers:
            keyboard.append([
                InlineKeyboardButton(server["name"], callback_data=f"bind_server_{server['id']}")
            ])

        # 显示已绑定信息
        hint = ""
        if bound_server_ids:
            hint = f"\n\n💡 你已绑定 {len(bound_server_ids)} 个服务器"

        await update.message.reply_text(
            f"请选择要绑定的 Emby 服务器：{hint}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SELECTING_SERVER

    async def bind_server_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理服务器选择"""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        server_id = query.data.replace("bind_server_", "")

        server = await server_service.get_server(server_id)
        if not server:
            await query.edit_message_text("❌ 服务器不存在，请重新开始绑定。")
            return ConversationHandler.END

        self._bind_sessions[user_id] = {
            "server_id": server_id,
            "server_name": server["name"]
        }

        await query.edit_message_text(
            f"📡 已选择服务器：{server['name']}\n\n"
            "请输入你的 Emby 用户名："
        )
        return WAITING_USERNAME

    async def bind_username_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理用户名输入"""
        user_id = str(update.effective_user.id)
        username = update.message.text.strip()

        if user_id not in self._bind_sessions:
            await update.message.reply_text("❌ 会话已过期，请重新使用 /bind 开始绑定。")
            return ConversationHandler.END

        self._bind_sessions[user_id]["username"] = username
        await update.message.reply_text(
            f"👤 用户名：{username}\n\n"
            "请输入你的 Emby 密码：\n"
            "（密码仅用于验证，不会被保存）\n\n"
            "💡 如果账户没有密码，请发送 /skip 跳过"
        )
        return WAITING_PASSWORD

    async def bind_skip_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理跳过密码（无密码账户绑定）"""
        user_id = str(update.effective_user.id)

        if user_id not in self._bind_sessions:
            await update.message.reply_text("❌ 会话已过期，请重新使用 /bind 开始绑定。")
            return ConversationHandler.END

        session = self._bind_sessions[user_id]
        server_id = session["server_id"]
        username = session["username"]

        # 发送验证中提示
        msg = await update.message.reply_text("🔄 正在查找账户...")

        # 获取服务器配置
        server_config = await server_service.get_server(server_id)
        if not server_config:
            await msg.edit_text("❌ 服务器配置错误，请联系管理员。")
            del self._bind_sessions[user_id]
            return ConversationHandler.END

        # 通过用户名查找用户
        user_result = await emby_service.find_user_by_name(username, server_config)

        if not user_result:
            await msg.edit_text(
                "❌ 未找到该用户名。\n\n"
                "请使用 /bind 重新开始绑定。"
            )
            del self._bind_sessions[user_id]
            return ConversationHandler.END

        # 保存绑定关系
        user = update.effective_user
        success = await tg_binding_service.create_binding(
            tg_user_id=user_id,
            tg_username=user.username or "",
            tg_first_name=user.first_name or "",
            server_id=server_id,
            emby_user_id=user_result["user_id"],
            emby_username=user_result["username"]
        )

        if success:
            await msg.edit_text(
                f"✅ 绑定成功！\n\n"
                f"📡 服务器：{session['server_name']}\n"
                f"👤 Emby 账户：{user_result['username']}\n\n"
                "现在可以使用 /report 查看你的观影报告了。"
            )
        else:
            await msg.edit_text("❌ 绑定失败，请稍后重试。")

        del self._bind_sessions[user_id]
        return ConversationHandler.END

    async def bind_password_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理密码输入并验证"""
        user_id = str(update.effective_user.id)
        password = update.message.text

        # 尝试删除包含密码的消息（可能因权限失败）
        try:
            await update.message.delete()
        except:
            pass

        if user_id not in self._bind_sessions:
            await update.effective_chat.send_message("❌ 会话已过期，请重新使用 /bind 开始绑定。")
            return ConversationHandler.END

        session = self._bind_sessions[user_id]
        server_id = session["server_id"]
        username = session["username"]

        logger.debug(f"[TgBot] bind_password_received: user_id={user_id}, server_id={server_id}, username={username}")

        # 发送验证中提示
        msg = await update.effective_chat.send_message("🔄 正在验证账户...")

        # 获取服务器配置
        server_config = await server_service.get_server(server_id)
        logger.debug(f"[TgBot] server_config for {server_id}: {server_config}")

        if not server_config:
            await msg.edit_text("❌ 服务器配置错误，请联系管理员。")
            del self._bind_sessions[user_id]
            return ConversationHandler.END

        # 验证 Emby 账户
        auth_result = await emby_service.authenticate_user(username, password, server_config)

        if not auth_result:
            await msg.edit_text(
                "❌ 验证失败，用户名或密码错误。\n\n"
                "请使用 /bind 重新开始绑定。"
            )
            del self._bind_sessions[user_id]
            return ConversationHandler.END

        # 保存绑定关系
        user = update.effective_user
        success = await tg_binding_service.create_binding(
            tg_user_id=user_id,
            tg_username=user.username or "",
            tg_first_name=user.first_name or "",
            server_id=server_id,
            emby_user_id=auth_result["user_id"],
            emby_username=auth_result["username"]
        )

        if success:
            await msg.edit_text(
                f"✅ 绑定成功！\n\n"
                f"📡 服务器：{session['server_name']}\n"
                f"👤 Emby 账户：{auth_result['username']}\n\n"
                "现在可以使用 /report 查看你的观影报告了。"
            )
        else:
            await msg.edit_text("❌ 绑定失败，请稍后重试。")

        del self._bind_sessions[user_id]
        return ConversationHandler.END

    # ==================== 解绑流程 ====================

    async def cmd_unbind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /unbind 命令"""
        user_id = str(update.effective_user.id)

        bindings = await tg_binding_service.get_user_bindings(user_id)
        if not bindings:
            await update.message.reply_text("❌ 你还没有绑定任何账户。")
            return

        # 如果只有一个绑定，直接确认解绑
        if len(bindings) == 1:
            binding = bindings[0]
            server = await server_service.get_server(binding["server_id"])
            server_name = server["name"] if server else "未知服务器"

            keyboard = [
                [
                    InlineKeyboardButton("✅ 确认解绑", callback_data=f"unbind_confirm_{binding['server_id']}"),
                    InlineKeyboardButton("❌ 取消", callback_data="unbind_cancel")
                ]
            ]

            await update.message.reply_text(
                f"⚠️ 确定要解除绑定吗？\n\n"
                f"📡 服务器：{server_name}\n"
                f"👤 账户：{binding['emby_username']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # 多个绑定，让用户选择要解绑哪个
        keyboard = []
        for binding in bindings:
            server = await server_service.get_server(binding["server_id"])
            server_name = server["name"] if server else "未知"
            keyboard.append([
                InlineKeyboardButton(
                    f"{server_name}: {binding['emby_username']}",
                    callback_data=f"unbind_select_{binding['server_id']}"
                )
            ])

        # 添加全部解绑选项
        keyboard.append([
            InlineKeyboardButton("🗑️ 解绑全部", callback_data="unbind_select_all")
        ])
        keyboard.append([
            InlineKeyboardButton("❌ 取消", callback_data="unbind_cancel")
        ])

        await update.message.reply_text(
            f"你已绑定 {len(bindings)} 个服务器账户，请选择要解绑的账户：",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def unbind_confirmed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理解绑确认"""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        data = query.data

        if data == "unbind_cancel":
            await query.edit_message_text("❌ 已取消解绑操作。")
            return

        # 处理选择要解绑的服务器
        if data.startswith("unbind_select_"):
            server_id = data.replace("unbind_select_", "")

            if server_id == "all":
                # 确认全部解绑
                keyboard = [
                    [
                        InlineKeyboardButton("✅ 确认全部解绑", callback_data="unbind_confirm_all"),
                        InlineKeyboardButton("❌ 取消", callback_data="unbind_cancel")
                    ]
                ]
                await query.edit_message_text(
                    "⚠️ 确定要解除所有服务器的绑定吗？",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                # 确认解绑特定服务器
                binding = await tg_binding_service.get_binding(user_id, server_id)
                if not binding:
                    await query.edit_message_text("❌ 绑定信息不存在。")
                    return

                server = await server_service.get_server(server_id)
                server_name = server["name"] if server else "未知服务器"

                keyboard = [
                    [
                        InlineKeyboardButton("✅ 确认解绑", callback_data=f"unbind_confirm_{server_id}"),
                        InlineKeyboardButton("❌ 取消", callback_data="unbind_cancel")
                    ]
                ]
                await query.edit_message_text(
                    f"⚠️ 确定要解除绑定吗？\n\n"
                    f"📡 服务器：{server_name}\n"
                    f"👤 账户：{binding['emby_username']}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            return

        # 处理确认解绑
        if data.startswith("unbind_confirm_"):
            server_id = data.replace("unbind_confirm_", "")

            if server_id == "all":
                # 解绑全部
                success = await tg_binding_service.delete_binding(user_id)
                if success:
                    await query.edit_message_text("✅ 已成功解除所有绑定。")
                else:
                    await query.edit_message_text("❌ 解绑失败，请稍后重试。")
            else:
                # 解绑特定服务器
                success = await tg_binding_service.delete_binding(user_id, server_id)
                if success:
                    await query.edit_message_text("✅ 已成功解除绑定。")
                else:
                    await query.edit_message_text("❌ 解绑失败，请稍后重试。")

    # ==================== 报告查询 ====================

    async def cmd_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /report 命令"""
        user_id = str(update.effective_user.id)

        bindings = await tg_binding_service.get_user_bindings(user_id)
        if not bindings:
            await update.message.reply_text(
                "❌ 你还没有绑定 Emby 账户。\n\n"
                "请先使用 /bind 绑定账户。"
            )
            return

        # 如果有多个绑定，先让用户选择服务器
        if len(bindings) > 1:
            keyboard = []
            for binding in bindings:
                server = await server_service.get_server(binding["server_id"])
                server_name = server["name"] if server else "未知"
                keyboard.append([
                    InlineKeyboardButton(
                        f"{server_name}: {binding['emby_username']}",
                        callback_data=f"report_server_{binding['server_id']}"
                    )
                ])

            await update.message.reply_text(
                "📊 请选择要查看报告的服务器：",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # 只有一个绑定，直接显示周期选择
        keyboard = [
            [
                InlineKeyboardButton("📅 今日", callback_data=f"report_period_{bindings[0]['server_id']}_daily"),
                InlineKeyboardButton("📆 本周", callback_data=f"report_period_{bindings[0]['server_id']}_weekly"),
            ],
            [
                InlineKeyboardButton("📊 本月", callback_data=f"report_period_{bindings[0]['server_id']}_monthly"),
                InlineKeyboardButton("📈 本年", callback_data=f"report_period_{bindings[0]['server_id']}_yearly"),
            ]
        ]

        await update.message.reply_text(
            "📊 选择报告周期",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def report_period_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理报告服务器和周期选择"""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        data = query.data

        # 处理服务器选择：report_server_{server_id}
        if data.startswith("report_server_"):
            server_id = data.replace("report_server_", "")
            binding = await tg_binding_service.get_binding(user_id, server_id)
            if not binding:
                await query.edit_message_text("❌ 绑定信息已失效，请重新绑定。")
                return

            server = await server_service.get_server(server_id)
            server_name = server["name"] if server else "未知"

            keyboard = [
                [
                    InlineKeyboardButton("📅 今日", callback_data=f"report_period_{server_id}_daily"),
                    InlineKeyboardButton("📆 本周", callback_data=f"report_period_{server_id}_weekly"),
                ],
                [
                    InlineKeyboardButton("📊 本月", callback_data=f"report_period_{server_id}_monthly"),
                    InlineKeyboardButton("📈 本年", callback_data=f"report_period_{server_id}_yearly"),
                ]
            ]

            await query.edit_message_text(
                f"📊 {server_name} - 选择报告周期",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # 处理周期选择：report_period_{server_id}_{period}
        if data.startswith("report_period_"):
            parts = data.replace("report_period_", "").rsplit("_", 1)
            if len(parts) != 2:
                await query.edit_message_text("❌ 参数错误，请重新操作。")
                return

            server_id, period = parts
            binding = await tg_binding_service.get_binding(user_id, server_id)
            if not binding:
                await query.edit_message_text("❌ 绑定信息已失效，请重新绑定。")
                return

            period_names = {"daily": "今日", "weekly": "本周", "monthly": "本月", "yearly": "本年"}
            await query.edit_message_text(f"🔄 正在生成{period_names.get(period, '')}观影报告...")

            try:
                # 获取服务器配置
                server_config = await server_service.get_server(server_id)
                if not server_config:
                    await query.edit_message_text("❌ 服务器配置错误，请联系管理员。")
                    return

                # 获取报告配置（用于 content_count）
                report_cfg = report_config_service.load(server_id)

                # 生成报告图片
                image_data = await report_service.generate_report_image(
                    user_ids=[binding["emby_user_id"]],
                    period=period,
                    content_count=report_cfg.content_count,
                    server_config=server_config
                )

                # 发送图片
                await query.delete_message()
                await update.effective_chat.send_photo(
                    photo=image_data,
                    caption=f"📊 {binding['emby_username']} 的{period_names.get(period, '')}观影报告"
                )

            except Exception as e:
                logger.error(f"[TgBot] Error generating report: {e}")
                await query.edit_message_text(f"❌ 生成报告失败：{str(e)}")

    # ==================== 信息查询 ====================

    async def cmd_myinfo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /myinfo 命令"""
        user_id = str(update.effective_user.id)

        bindings = await tg_binding_service.get_user_bindings(user_id)
        if not bindings:
            await update.message.reply_text(
                "❌ 你还没有绑定 Emby 账户。\n\n"
                "请使用 /bind 绑定账户。"
            )
            return

        # 获取 TG 显示名称（从第一个绑定获取）
        tg_display = bindings[0].get('tg_first_name') or bindings[0].get('tg_username') or '未知'

        info_text = f"📋 绑定信息\n\n💬 Telegram：{tg_display}（{user_id}）\n"

        # 显示所有绑定
        for i, binding in enumerate(bindings, 1):
            server = await server_service.get_server(binding["server_id"])
            server_name = server["name"] if server else "未知"

            if len(bindings) > 1:
                info_text += f"\n━━━ 绑定 {i} ━━━\n"

            info_text += (
                f"📡 服务器：{server_name}\n"
                f"👤 Emby 账户：{binding['emby_username']}\n"
                f"🕐 绑定时间：{binding['created_at'][:19]}\n"
            )

        await update.message.reply_text(info_text)


# 单例实例
tg_bot_service = TgBotService()
