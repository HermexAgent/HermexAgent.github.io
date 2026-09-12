"""
HermesX Telegram Command & Control Gateway
"""

import asyncio
import logging
import os
import yaml
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supervisor.hub.ollama_manager import OllamaHub, CATALOG_MODELS
from supervisor.hub.voice_manager import VoiceHub

logger = logging.getLogger("HermesX.TelegramBot")

class TelegramGateway:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.bot_token = self.config.get("telegram", {}).get("bot_token")
        self.allowed_users = self.config.get("telegram", {}).get("allowed_users", [])
        self.ollama_hub = OllamaHub(self.config.get("models", {}).get("ollama", {}).get("host", "http://127.0.0.1:11434"))
        self.voice_hub = VoiceHub()
        self.app = None

    def is_authorized(self, user_id: int) -> bool:
        if not self.allowed_users:
            # First user becomes admin
            self.allowed_users.append(user_id)
            return True
        return user_id in self.allowed_users

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔️ Access Denied. You are not authorized.")
            return

        welcome_text = (
            "🚀 *Welcome to HermesX Command Center*\n\n"
            "HermesX is your all-in-one autonomous AI assistant. You can chat directly, "
            "send voice messages, or manage local models with 1 click.\n\n"
            "📌 *Quick Actions:*"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📦 Ollama Model Hub", callback_data="hub_ollama"),
                InlineKeyboardButton("🎙 Voice & STT Hub", callback_data="hub_voice")
            ],
            [
                InlineKeyboardButton("📊 System Status", callback_data="sys_status"),
                InlineKeyboardButton("⚙️ Switch Model", callback_data="switch_model")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

    async def ollama_hub_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
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
        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")])

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_pull_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        model_id = query.data.replace("pull_", "")
        await query.answer(f"Starting download for {model_id}...")

        msg = await query.edit_message_text(
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
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            return

        user_prompt = update.message.text
        # Simulated agent thinking & response stream
        thinking_msg = await update.message.reply_text("🧠 _Agent thinking & processing tools..._", parse_mode="Markdown")
        await asyncio.sleep(1.0)
        await thinking_msg.edit_text(f"🤖 *HermesX Reply:*\n\nReceived your instruction: `{user_prompt}`\n\n(Agent execution pipeline active)", parse_mode="Markdown")

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            return

        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        temp_audio_path = f"/tmp/hermesx_voice_{voice.file_id}.ogg"
        await voice_file.download_to_drive(temp_audio_path)

        msg = await update.message.reply_text("🎙 _Transcribing voice message (Faster-Whisper)..._", parse_mode="Markdown")
        
        transcribed_text = await self.voice_hub.transcribe(temp_audio_path)
        if not transcribed_text:
            await msg.edit_text("⚠️ Could not transcribe audio.")
            return

        await msg.edit_text(f"🗣 *Transcribed:* \"_{transcribed_text}_\"\n\n🧠 _Thinking..._", parse_mode="Markdown")
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    def run(self):
        if not self.bot_token:
            logger.warning("Telegram Bot Token is empty. Telegram gateway skipped.")
            return

        self.app = Application.builder().token(self.bot_token).build()
        self.app.add_handler(CommandHandler("start", self.start_cmd))
        self.app.add_handler(CallbackQueryHandler(self.ollama_hub_menu, pattern="^hub_ollama$"))
        self.app.add_handler(CallbackQueryHandler(self.handle_pull_callback, pattern="^pull_"))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_chat_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

        logger.info("Starting Telegram Bot long-polling...")
        self.app.run_polling()
