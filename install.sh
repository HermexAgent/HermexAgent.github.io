#!/usr/bin/env bash
# ==============================================================================
#  _   _                       _                    _   
# | \ | | _____  ___   _ ___  / \   __ _  ___ _ __ | |_ 
# |  \| |/ _ \ \/ / | | / __|/ _ \ / _` |/ _ \ '_ \| __|
# | |\  |  __/>  <| |_| \__ / ___ \ (_| |  __/ | | | |_ 
# |_| \_|\___/_/\_\\__,_|___/_/   \_\__, |\___|_| |_|\__|
#                                   |___/                
# NexusAgent - The All-in-One Autonomous AI Stack
# Zero-Config Setup, Local AI Hub & Full Telegram Remote Control
# ==============================================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << "EOF"
  _   _                       _                    _   
 | \ | | _____  ___   _ ___  / \   __ _  ___ _ __ | |_ 
 |  \| |/ _ \ \/ / | | / __|/ _ \ / _` |/ _ \ '_ \| __|
 | |\  |  __/>  <| |_| \__ / ___ \ (_| |  __/ | | | |_ 
 |_| \_|\___/_/\_\\__,_|___/_/   \_\__, |\___|_| |_|\__|
                                   |___/                
       The All-in-One Autonomous AI Stack
EOF
echo -e "${NC}"

INSTALL_DIR="$HOME/.nexusagent"
REPO_URL="https://github.com/m4tinbeigi-official/NexusAgent.git"

echo -e "${YELLOW}🔍 Checking system prerequisites...${NC}"

# Check OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac
echo -e "${GREEN}✓ Platform: ${PLATFORM}${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is required. Please install Python 3.10+ and re-run.${NC}"
    exit 1
fi
PY_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python: ${PY_VER}${NC}"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is not installed. Installing git...${NC}"
    if [ "$PLATFORM" = "Mac" ]; then
        xcode-select --install || true
    elif [ "$PLATFORM" = "Linux" ]; then
        sudo apt-get update && sudo apt-get install -y git || true
    fi
fi
echo -e "${GREEN}✓ Git: $(git --version)${NC}"

# Clone or update NexusAgent
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${CYAN}📦 Updating existing NexusAgent installation at ${INSTALL_DIR}...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo -e "${CYAN}📦 Installing NexusAgent to ${INSTALL_DIR}...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Setup Python Virtual Environment
echo -e "${YELLOW}⚙️ Setting up isolated Python environment...${NC}"
if [ ! -d "$INSTALL_DIR/venv" ]; then
    python3 -m venv "$INSTALL_DIR/venv"
fi

source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip setuptools wheel --quiet
pip install -r "$INSTALL_DIR/requirements.txt" --quiet
echo -e "${GREEN}✓ Virtualenv ready.${NC}"

# Configuration Setup
CONFIG_FILE="$INSTALL_DIR/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}📝 Creating initial configuration...${NC}"
    cp "$INSTALL_DIR/config.example.yaml" "$CONFIG_FILE"
    
    echo -e "\n${BOLD}${CYAN}──────────────────────────────────────────────────────────${NC}"
    echo -e "${BOLD}🤖 Telegram Bot Setup (Optional but Recommended)${NC}"
    echo -e "You can control everything from Telegram (Chat, Voice, Ollama Hub)."
    echo -e "Get a token from @BotFather on Telegram, or press Enter to skip."
    echo -e "${BOLD}${CYAN}──────────────────────────────────────────────────────────${NC}\n"
    
    read -p "Enter Telegram Bot Token [leave empty to configure later]: " TG_TOKEN
    if [ -n "$TG_TOKEN" ]; then
        sed -i.bak "s|bot_token: \"\"|bot_token: \"$TG_TOKEN\"|g" "$CONFIG_FILE" && rm -f "$CONFIG_FILE.bak"
        echo -e "${GREEN}✓ Telegram bot token saved.${NC}"
    fi
fi

# Symlink CLI
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/scripts/nexus.sh" "$HOME/.local/bin/nexus"

# Add ~/.local/bin to PATH if not present
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    SHELL_RC="$HOME/.bashrc"
    [ -n "$ZSH_VERSION" ] && SHELL_RC="$HOME/.zshrc"
    [ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    echo -e "${YELLOW}ℹ️ Added ~/.local/bin to your PATH in $SHELL_RC${NC}"
fi

echo -e "\n${GREEN}${BOLD}==========================================================${NC}"
echo -e "${GREEN}${BOLD}🎉 NexusAgent successfully installed!${NC}"
echo -e "${GREEN}${BOLD}==========================================================${NC}"
echo -e "To start NexusAgent now, simply run:"
echo -e "  ${CYAN}${BOLD}nexus start${NC}"
echo -e ""
echo -e "Other useful commands:"
echo -e "  ${YELLOW}nexus status${NC}   - Check health of supervisor, Ollama & bot"
echo -e "  ${YELLOW}nexus stop${NC}     - Stop all background daemons"
echo -e "  ${YELLOW}nexus logs${NC}     - View live stream logs"
echo -e "  ${YELLOW}nexus update${NC}   - Update without touching personal data"
echo -e ""
