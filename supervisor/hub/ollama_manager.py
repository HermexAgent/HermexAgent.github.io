"""
HermesX Local Hub - 1-Click Ollama Manager & Fast Model Puller
"""

import asyncio
import json
import logging
import httpx
from typing import AsyncGenerator, Dict, Any, List

logger = logging.getLogger("HermesX.OllamaHub")

CATALOG_MODELS = [
    {
        "id": "qwen2.5-coder:7b",
        "name": "💻 Qwen 2.5 Coder (7B)",
        "category": "Coding & Engineering",
        "size": "4.7 GB",
        "recommended_ram": "8 GB"
    },
    {
        "id": "deepseek-r1:8b",
        "name": "🧠 DeepSeek R1 (8B)",
        "category": "Reasoning & Logic",
        "size": "4.9 GB",
        "recommended_ram": "16 GB"
    },
    {
        "id": "llama3.2:3b",
        "name": "⚡️ Llama 3.2 (3B)",
        "category": "Fast & Lightweight",
        "size": "2.0 GB",
        "recommended_ram": "4 GB"
    },
    {
        "id": "mistral:7b",
        "name": "🌐 Mistral (7B)",
        "category": "General Chat & Tools",
        "size": "4.1 GB",
        "recommended_ram": "8 GB"
    }
]

class OllamaHub:
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host.rstrip("/")

    async def check_health(self) -> bool:
        """Check if Ollama service is reachable."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.host}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def list_installed_models(self) -> List[Dict[str, Any]]:
        """Return list of locally downloaded models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.host}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return data.get("models", [])
        except Exception as e:
            logger.error(f"Error fetching installed models: {e}")
        return []

    async def pull_model_stream(self, model_name: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream progress of model pull from Ollama."""
        url = f"{self.host}/api/pull"
        payload = {"name": model_name, "stream": True}
        
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    yield {"status": "error", "message": f"HTTP {response.status_code}"}
                    return

                async for chunk in response.aiter_lines():
                    if not chunk:
                        continue
                    try:
                        data = json.loads(chunk)
                        yield data
                    except Exception:
                        pass
