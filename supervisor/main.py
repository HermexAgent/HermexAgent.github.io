"""
HermexAgent Master Supervisor Runtime (Orchestrates Background Web, Telegram & Ollama)
"""

import os
import sys
import asyncio
import logging
import subprocess
import uvicorn
import yaml
from supervisor.bot.telegram_bot import TelegramGateway
from supervisor.web_server import app as web_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("HermexAgent.Supervisor")

def ensure_ollama_running():
    """Check and auto-start Ollama daemon if not already running."""
    try:
        import httpx
        res = httpx.get("http://127.0.0.1:11434/api/tags", timeout=1.5)
        if res.status_code == 200:
            logger.info("✓ Ollama daemon is active and reachable on port 11434.")
            return
    except Exception:
        pass

    # Try starting Ollama
    try:
        logger.info("⚡️ Auto-starting Ollama service in background...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.warning(f"Could not auto-start Ollama (is it installed?): {e}")

async def run_services():
    install_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(install_dir, "config.yaml")
    
    if not os.path.exists(config_path):
        config_path = os.path.join(install_dir, "config.example.yaml")

    ensure_ollama_running()

    # 1. Start FastAPI Web Dashboard Server
    config = uvicorn.Config(web_app, host="127.0.0.1", port=7860, log_level="warning")
    server = uvicorn.Server(config)
    
    logger.info("🌐 Web Dashboard running at http://127.0.0.1:7860")

    # 2. Start Telegram Gateway in background task
    tg_gateway = TelegramGateway(config_path)
    if tg_gateway.bot_token:
        asyncio.create_task(asyncio.to_thread(tg_gateway.run))
        logger.info("🤖 Telegram Gateway initialized.")
    else:
        logger.info("ℹ️ Telegram Bot token not configured yet. Web Dashboard active.")

    await server.serve()

def main():
    logger.info("🚀 Booting HermexAgent Stack (Auto-Wired Mode)...")
    try:
        asyncio.run(run_services())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutting down HermexAgent Stack.")

if __name__ == "__main__":
    main()
