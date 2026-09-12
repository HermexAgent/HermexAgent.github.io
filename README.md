# 🌐 HermexAgent

<div align="center">

```
  _   _                                           _                    _   
 | | | | ___ _ __ _ __ ___   _____  __   / \   __ _  ___ _ __ | |_ 
 | |_| |/ _ \ '__| '_ ` _ \ / _ \ \/ /  / _ \ / _` |/ _ \ '_ \| __|
 |  _  |  __/ |  | | | | | |  __/>  <  / ___ \ (_| |  __/ | | | |_ 
 |_| |_|\___|_|  |_| |_| |_|\___/_/\_\/_/   \_\__, |\___|_| |_|\__|
                                               |___/                
```

**The All-in-One Autonomous AI Stack**  
*Zero-Config Installer • 1-Click Local Ollama & Voice Hub • Claude/Gmail Direct Login • Telegram Remote C2*

[![GitHub Stars](https://img.shields.io/github/stars/HermexAgent/HermexAgent.github.io?style=for-the-badge&color=blue)](https://github.com/HermexAgent/HermexAgent.github.io)
[![Website](https://img.shields.io/badge/Website-HermexAgent.github.io-purple.svg?style=for-the-badge)](https://hermexagent.github.io)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)

</div>

---

## ⚡️ Quick Start (1-Line Install)

Run this single command in your terminal to install and setup the entire stack:

```bash
curl -fsSL https://raw.githubusercontent.com/HermexAgent/HermexAgent.github.io/main/install.sh | bash
```

---

## 🌟 Key Superpowers

1. 📦 **1-Click Local AI (Ollama Hub):**
   - Download, run and switch models (`DeepSeek-R1`, `Qwen2.5-Coder`, `Llama-3.2`) with 1-click directly from Telegram or the Desktop UI with live download progress bars.

2. 🎙 **Local Voice & Speech-to-Text (STT):**
   - Integrated with **Faster-Whisper** and **Edge-TTS**. Send voice memos in Persian/English to get instant transcriptions and vocal responses.

3. 🤖 **Full Telegram Remote Control (C2):**
   - Full control over agent reasoning, terminal PTY executions, scheduled cron jobs, and approval prompts directly inside Telegram.

4. 🔑 **Zero-API-Key Direct Web Sessions:**
   - Native drivers for Claude Pro/Max web sessions, Google Gemini, and ChatGPT Plus without paying extra per API token.

5. 🛡 **Decoupled & Upstream-Safe:**
   - Designed with an isolated supervisor architecture: upstream updates to underlying agent frameworks will never break your personal setup or configurations.

---

## 🕹 CLI Management

After installation, control HermexAgent easily from your terminal:

```bash
hermex start      # Start supervisor daemon in background
hermex status     # Check health of supervisor, Ollama & bot
hermex stop       # Stop all background daemons
hermex logs       # View live stream logs
hermex update     # Safe-update core stack without losing data
```

---

## 📁 Project Architecture

```text
HermexAgent/
├── install.sh                  # 1-Line Zero-Config Installer
├── scripts/hermex.sh           # Universal CLI control daemon
├── config.example.yaml         # Central unified configuration
├── supervisor/                 # Core supervisor & orchestration engine
│   ├── bot/                    # Telegram C2 Gateway & Interactive Menus
│   ├── hub/                    # 1-Click Ollama Manager & Whisper STT
│   ├── web_server.py           # Embedded Local Web Dashboard
│   └── main.py                 # Master background service
└── web-ui/                     # Interactive Desktop / Web UI Workspace
```

---

## 📄 License

MIT © [HermexAgent](https://github.com/HermexAgent)
