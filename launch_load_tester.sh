#!/bin/bash
# Shippy API Load Tester Launcher
# Professional load testing tool for management

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   Shippy API Load Testing Tool     ${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "stress_test_env" ]; then
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    python3 -m venv stress_test_env
    
    echo -e "${YELLOW}Installing dependencies...${NC}"
    source stress_test_env/bin/activate
    pip install aiohttp
    echo -e "${GREEN}Environment setup complete!${NC}"
    echo ""
else
    echo -e "${GREEN}Python environment ready${NC}"
    echo ""
fi

# Activate environment and launch GUI
echo -e "${BLUE}Starting Load Testing Dashboard...${NC}"
source stress_test_env/bin/activate

# Check if display is available (for GUI)
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo -e "${RED}Error: No display available for GUI${NC}"
    echo -e "${YELLOW}This tool requires a graphical desktop environment${NC}"
    exit 1
fi

# Launch the GUI application
python3 load_test_gui.py

echo -e "${GREEN}Load tester closed${NC}"