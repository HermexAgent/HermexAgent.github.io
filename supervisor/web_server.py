"""
HermexAgent Local Web Dashboard Server (FastAPI + Embedded UI)
"""

import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from supervisor.hub.ollama_manager import OllamaHub, CATALOG_MODELS

app = FastAPI(title="HermexAgent Web Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_hub = OllamaHub()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HermexAgent Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b0f19; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; }
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-4xl mx-auto space-y-8">
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-gray-800 pb-6">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
                    <span class="text-cyan-400">⚡️</span> HermexAgent
                </h1>
                <p class="text-sm text-gray-400 mt-1">The All-in-One Autonomous AI Stack</p>
            </div>
            <div class="flex items-center gap-3">
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Core Active
                </span>
            </div>
        </div>

        <!-- System Hub Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Ollama Model Hub -->
            <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
                <h2 class="text-lg font-bold text-white flex items-center gap-2">
                    📦 Local AI Models (Ollama)
                </h2>
                <p class="text-xs text-gray-400">Download and run high-performance models locally with 1-click.</p>
                <div class="space-y-3" id="model-list">
                    <div class="p-3 bg-gray-950 rounded-lg border border-gray-800 flex items-center justify-between">
                        <div>
                            <div class="font-medium text-sm text-gray-200">💻 Qwen 2.5 Coder (7B)</div>
                            <div class="text-xs text-gray-500">4.7 GB • Coding & Tools</div>
                        </div>
                        <button onclick="pullModel('qwen2.5-coder:7b')" class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold transition">
                            1-Click Install
                        </button>
                    </div>
                    <div class="p-3 bg-gray-950 rounded-lg border border-gray-800 flex items-center justify-between">
                        <div>
                            <div class="font-medium text-sm text-gray-200">🧠 DeepSeek R1 (8B)</div>
                            <div class="text-xs text-gray-500">4.9 GB • Deep Reasoning</div>
                        </div>
                        <button onclick="pullModel('deepseek-r1:8b')" class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold transition">
                            1-Click Install
                        </button>
                    </div>
                    <div class="p-3 bg-gray-950 rounded-lg border border-gray-800 flex items-center justify-between">
                        <div>
                            <div class="font-medium text-sm text-gray-200">⚡️ Llama 3.2 (3B)</div>
                            <div class="text-xs text-gray-500">2.0 GB • Ultra Fast</div>
                        </div>
                        <button onclick="pullModel('llama3.2:3b')" class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold transition">
                            1-Click Install
                        </button>
                    </div>
                </div>
                <div id="progress-container" class="hidden p-3 bg-gray-950 rounded border border-cyan-900 text-xs text-cyan-300 font-mono">
                    <div id="progress-text">Downloading...</div>
                </div>
            </div>

            <!-- Telegram & Control Gateway -->
            <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
                <h2 class="text-lg font-bold text-white flex items-center gap-2">
                    🤖 Telegram Remote Control
                </h2>
                <p class="text-xs text-gray-400">Control everything remotely from Telegram on your phone.</p>
                <div class="p-4 bg-gray-950 rounded-lg border border-gray-800 space-y-3">
                    <div class="text-sm text-gray-300">
                        • Send voice memos in Persian/English (STT)<br>
                        • Execute shell commands safely<br>
                        • Download Ollama models from Telegram
                    </div>
                    <div class="text-xs text-emerald-400 bg-emerald-950/60 p-2.5 rounded border border-emerald-800/60">
                        ✓ Telegram Gateway service is running in background.
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center text-xs text-gray-600 pt-6">
            HermexAgent • MIT License • <a href="https://hermexagent.github.io" class="text-cyan-500 hover:underline" target="_blank">Documentation</a>
        </div>
    </div>

    <script>
        async function pullModel(modelName) {
            const container = document.getElementById('progress-container');
            const text = document.getElementById('progress-text');
            container.classList.remove('hidden');
            text.innerText = `⏳ Starting download for ${modelName}...`;

            try {
                const res = await fetch(`/api/pull?model=${encodeURIComponent(modelName)}`, { method: 'POST' });
                const reader = res.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value);
                    text.innerText = chunk;
                }
                text.innerText = `✅ Successfully installed ${modelName}!`;
            } catch (err) {
                text.innerText = `❌ Error: ${err.message}`;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/api/models")
async def get_models():
    return {"catalog": CATALOG_MODELS, "installed": await ollama_hub.list_installed_models()}

@app.post("/api/pull")
async def pull_model_endpoint(model: str):
    from fastapi.responses import StreamingResponse

    async def event_generator():
        async for progress in ollama_hub.pull_model_stream(model):
            status = progress.get("status", "")
            completed = progress.get("completed", 0)
            total = progress.get("total", 0)
            if total > 0:
                percent = int((completed / total) * 100)
                yield f"[{percent}%] {status}\n"
            else:
                yield f"{status}\n"

    return StreamingResponse(event_generator(), media_type="text/plain")
