"""
HermexAgent Main Supervisor Entrypoint
"""

import os
import sys
import logging
import yaml
from supervisor.bot.telegram_bot import TelegramGateway

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("HermexAgent.Supervisor")

def main():
    logger.info("🚀 Booting HermexAgent Supervisor Daemon...")
    
    install_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(install_dir, "config.yaml")
    
    if not os.path.exists(config_path):
        config_path = os.path.join(install_dir, "config.example.yaml")
        logger.info(f"Using default config template: {config_path}")

    # Start Telegram Gateway
    tg_gateway = TelegramGateway(config_path)
    tg_gateway.run()

if __name__ == "__main__":
    main()
