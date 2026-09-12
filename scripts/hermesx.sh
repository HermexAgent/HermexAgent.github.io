#!/usr/bin/env bash
# ==============================================================================
# HermesX CLI Launcher & Daemon Controller
# ==============================================================================

INSTALL_DIR="$HOME/.hermesx"
[ -d "$INSTALL_DIR" ] || INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

VENV_PYTHON="$INSTALL_DIR/venv/bin/python3"
PID_FILE="$INSTALL_DIR/supervisor.pid"
LOG_FILE="$INSTALL_DIR/hermesx.log"

case "$1" in
    start)
        echo "🚀 Starting HermesX Stack..."
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "⚠️ HermesX is already running (PID: $(cat "$PID_FILE"))"
            exit 0
        fi
        nohup "$VENV_PYTHON" "$INSTALL_DIR/supervisor/main.py" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "✅ HermesX daemon started with PID $(cat "$PID_FILE")."
        echo "📖 View live logs: hermex logs"
        ;;
    stop)
        echo "🛑 Stopping HermesX Stack..."
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                rm -f "$PID_FILE"
                echo "✅ Stopped HermesX (PID: $PID)."
            else
                rm -f "$PID_FILE"
                echo "ℹ️ Process was not running, removed stale PID file."
            fi
        else
            echo "ℹ️ No running HermesX instance found."
        fi
        ;;
    status)
        echo "📊 HermesX System Status:"
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "  🟢 Supervisor Daemon: Running (PID: $(cat "$PID_FILE"))"
        else
            echo "  🔴 Supervisor Daemon: Stopped"
        fi
        # Check Ollama
        if command -v ollama &>/dev/null; then
            if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
                echo "  🟢 Local Ollama: Running (Port 11434)"
            else
                echo "  🟡 Local Ollama: Installed but not running"
            fi
        else
            echo "  ⚪️ Local Ollama: Not installed"
        fi
        ;;
    logs)
        tail -n 50 -f "$LOG_FILE"
        ;;
    update)
        echo "🔄 Updating HermesX stack..."
        cd "$INSTALL_DIR"
        git pull origin main
        source "$INSTALL_DIR/venv/bin/activate"
        pip install -r "$INSTALL_DIR/requirements.txt" --quiet
        echo "✅ HermesX updated successfully."
        ;;
    *)
        echo "Usage: hermesx {start|stop|status|logs|update}"
        exit 1
        ;;
esac
