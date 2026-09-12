"""
HermexAgent Telegram Command & Control Gateway with Dynamic Voice/STT & Persian RTL Patcher
"""

import asyncio
import logging
import os
import yaml
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supervisor.hub.ollama_manager import OllamaHub, CATALOG_MODELS
from supervisor.hub.voice_manager import VoiceHub, WHISPER_CATALOG, TTS_VOICES
from supervisor.hub.persian_patcher import PersianPatcher

logger = logging.getLogger("HermexAgent.TelegramBot")

class TelegramGateway:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.bot_token = self.config.get("telegram", {}).get("bot_token")
        self.allowed_users = self.config.get("telegram", {}).get("allowed_users", [])
        self.ollama_hub = OllamaHub(self.config.get("models", {}).get("ollama", {}).get("host", "http://127.0.0.1:11434"))
        self.voice_hub = VoiceHub(
            model_size=self.config.get("voice", {}).get("stt", {}).get("model", "small"),
            tts_voice=self.config.get("voice", {}).get("tts", {}).get("voice", "fa-IR-DilaraNeural")
        )
        self.app = None

    def is_authorized(self, user_id: int) -> bool:
        if not self.allowed_users:
            self.allowed_users.append(user_id)
            return True
        return user_id in self.allowed_users

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not update.message:
            return
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔️ Access Denied. You are not authorized.")
            return

        welcome_text = (
            "🚀 *به مرکز کنترل HermexAgent خوش آمدید*\n\n"
            "دستیار هوشمند همه‌کاره برای چت صوتی/متنی، دانلود مدل‌های لوکال اولاما و بهینه‌سازی وب‌یوآی.\n\n"
            "📌 *دسترسی‌های سریع:*"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📦 هاب مدل‌های Ollama", callback_data="hub_ollama"),
                InlineKeyboardButton("🎙 هاب پردازش صوت (STT/TTS)", callback_data="hub_voice")
            ],
            [
                InlineKeyboardButton("🇮🇷 راست‌چین و فونت وزیر وب‌یوآی", callback_data="patch_persian_rtl"),
                InlineKeyboardButton("📊 وضعیت سیستم", callback_data="sys_status")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

    async def handle_persian_patch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """1-Click apply Vazirmatn font and smart RTL to Hermes WebUI."""
        query = update.callback_query
        if not query:
            return
        await query.answer("در حال اعمال فونت وزیرمتن و راست‌چین...")

        result = PersianPatcher.apply_persian_rtl_patch()
        if result.get("success"):
            text = (
                "✅ *پچ راست‌چین و فونت وزیرمتن با موفقیت اعمال شد!*\n\n"
                f"📝 {result.get('message')}\n\n"
                "تمامی متون فارسی در هرمس وب‌یوآی اکنون با فونت زیبای **وزیرمتن** و جهت راست‌به‌چپ (RTL) رندر می‌شوند."
            )
        else:
            text = (
                "⚠️ *نکته درباره پچ راست‌چین:*\n\n"
                f"{result.get('message')}\n\n"
                "برای اعمال دستی یا تغییر مسیر، می‌توانید ریپازیتوری زیر را بررسی کنید:\n"
                "🔗 https://github.com/m4tinbeigi-official/hermes-webui-persian"
            )

        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    async def voice_hub_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query:
            return
        await query.answer()

        text = (
            f"🎙 *Voice & Audio Processing Hub*\n\n"
            f"• *Active STT Model:* `{self.voice_hub.model_size}`\n"
            f"• *Active TTS Voice:* `{self.voice_hub.tts_voice}`\n\n"
            f"If you're not satisfied with speech recognition accuracy (e.g. Persian accents), "
            f"upgrade to **Whisper Medium** or **Large-v3-Turbo** with 1-click:"
        )

        keyboard = []
        for model in WHISPER_CATALOG:
            is_active = "✅ " if model["id"] == self.voice_hub.model_size else "⬇️ "
            keyboard.append([
                InlineKeyboardButton(
                    f"{is_active}{model['name']} ({model['size']}) | {model['fa_quality']}", 
                    callback_data=f"set_whisper_{model['id']}"
                )
            ])
            
        keyboard.append([
            InlineKeyboardButton("🗣 تغییر صدای پاسخ (TTS)", callback_data="list_tts_voices"),
            InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
        ])

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_whisper_switch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query or not query.data:
            return
        model_id = query.data.replace("set_whisper_", "")
        self.voice_hub.set_model_size(model_id)
        await query.answer(f"Switched STT model to {model_id}!")
        await self.voice_hub_menu(update, context)

    async def list_tts_voices_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query:
            return
        await query.answer()

        keyboard = []
        for v in TTS_VOICES:
            is_active = "✅ " if v["id"] == self.voice_hub.tts_voice else ""
            keyboard.append([
                InlineKeyboardButton(f"{is_active}{v['name']}", callback_data=f"set_tts_{v['id']}")
            ])
        keyboard.append([InlineKeyboardButton("🔙 Back to Voice Hub", callback_data="hub_voice")])

        await query.edit_message_text(
            "🗣 *انتخاب صدای گفتار (TTS):*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_tts_switch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query or not query.data:
            return
        voice_id = query.data.replace("set_tts_", "")
        self.voice_hub.set_tts_voice(voice_id)
        await query.answer(f"Switched TTS voice to {voice_id}!")
        await self.voice_hub_menu(update, context)

    async def ollama_hub_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query:
            return
        await query.answer()

        is_healthy = await self.ollama_hub.check_health()
        status_emoji = "🟢 Running" if is_healthy else "🔴 Stopped / Unreachable"
        
        text = (
            f"📦 *Ollama Local AI Hub*\n\n"
            f"• Status: {status_emoji}\n"
            f"• Host: `{self.ollama_hub.host}`\n\n"
            f"Select a model to download & install with 1-click:"
        )

        keyboard = []
        for model in CATALOG_MODELS:
            keyboard.append([
                InlineKeyboardButton(
                    f"⬇️ {model['name']} ({model['size']})", 
                    callback_data=f"pull_{model['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")])

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_pull_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query or not query.data:
            return
        model_id = query.data.replace("pull_", "")
        await query.answer(f"Starting download for {model_id}...")

        await query.edit_message_text(
            f"⏳ *Downloading `{model_id}` from Ollama...*\nPlease wait, streaming progress...",
            parse_mode="Markdown"
        )

        last_update_text = ""
        try:
            async for progress in self.ollama_hub.pull_model_stream(model_id):
                status = progress.get("status", "")
                completed = progress.get("completed", 0)
                total = progress.get("total", 0)

                if total > 0:
                    percent = int((completed / total) * 100)
                    progress_bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
                    text = f"⬇️ *Downloading `{model_id}`*\n`[{progress_bar}]` {percent}%\nStatus: {status}"
                else:
                    text = f"⚙️ *Setting up `{model_id}`*\nStatus: {status}"

                if text != last_update_text:
                    last_update_text = text
                    try:
                        await query.edit_message_text(text, parse_mode="Markdown")
                        await asyncio.sleep(0.8)
                    except Exception:
                        pass

            keyboard = [[InlineKeyboardButton("🔙 Back to Hub", callback_data="hub_ollama")]]
            await query.edit_message_text(
                f"✅ *Successfully downloaded and installed `{model_id}`!*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            await query.edit_message_text(f"❌ Failed to download model: {e}")

    async def handle_chat_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not update.message or not update.message.text:
            return
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            return

        user_prompt = update.message.text
        thinking_msg = await update.message.reply_text("🧠 _Agent thinking & processing tools..._", parse_mode="Markdown")
        await asyncio.sleep(1.0)
        await thinking_msg.edit_text(f"🤖 *HermexAgent Reply:*\n\nReceived your instruction: `{user_prompt}`\n\n(Agent execution pipeline active)", parse_mode="Markdown")

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not update.message or not update.message.voice:
            return
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            return

        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        temp_audio_path = f"/tmp/hermex_voice_{voice.file_id}.ogg"
        await voice_file.download_to_drive(temp_audio_path)

        msg = await update.message.reply_text("🎙 _Transcribing voice message (Faster-Whisper)..._", parse_mode="Markdown")
        
        result = await self.voice_hub.transcribe(temp_audio_path)
        if not result or not result.get("text"):
            await msg.edit_text("⚠️ Could not transcribe audio. Would you like to switch to a higher quality model?")
            return

        transcribed_text = result["text"]
        model_used = result.get("model_used", "small")
        prob = int(result.get("probability", 1.0) * 100)

        keyboard = []
        if model_used in ["tiny", "base", "small"]:
            keyboard.append([
                InlineKeyboardButton("🚀 کیفیت تشخیص کلمات کمه؟ ارتقا به Large Turbo", callback_data="hub_voice")
            ])

        reply_text = (
            f"🗣 *متن شناسایی‌شده:* \"_{transcribed_text}_\"\n\n"
            f"📊 _دقت مدل ({model_used}): {prob}%_\n\n"
            f"🧠 _در حال پردازش پاسخ توسط ایجنت..._"
        )

        await msg.edit_text(
            reply_text, 
            parse_mode="Markdown", 
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    def run(self):
        if not self.bot_token:
            logger.warning("Telegram Bot Token is empty. Telegram gateway skipped.")
            return

        self.app = Application.builder().token(self.bot_token).build()
        self.app.add_handler(CommandHandler("start", self.start_cmd))
        self.app.add_handler(CallbackQueryHandler(self.start_cmd, pattern="^main_menu$"))
        self.app.add_handler(CallbackQueryHandler(self.ollama_hub_menu, pattern="^hub_ollama$"))
        self.app.add_handler(CallbackQueryHandler(self.voice_hub_menu, pattern="^hub_voice$"))
        self.app.add_handler(CallbackQueryHandler(self.handle_persian_patch, pattern="^patch_persian_rtl$"))
        self.app.add_handler(CallbackQueryHandler(self.handle_whisper_switch, pattern="^set_whisper_"))
        self.app.add_handler(CallbackQueryHandler(self.list_tts_voices_menu, pattern="^list_tts_voices$"))
        self.app.add_handler(CallbackQueryHandler(self.handle_tts_switch, pattern="^set_tts_"))
        self.app.add_handler(CallbackQueryHandler(self.handle_pull_callback, pattern="^pull_"))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_chat_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

        logger.info("Starting Telegram Bot long-polling...")
        self.app.run_polling()
