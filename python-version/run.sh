#!/bin/bash
# Shimeji Mascot Launcher Script for Linux
# Detects environment and runs with appropriate settings

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python installation
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: Python not found. Please install Python 3.8 or higher.${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
}

# Check if we have a display
check_display() {
    if [ -n "$DISPLAY" ]; then
        return 0
    fi
    if command -v xset &> /dev/null; then
        xset q &> /dev/null
        return $?
    fi
    return 1
}

# Install dependencies
install_deps() {
    echo -e "${CYAN}Checking dependencies...${NC}"
    
    # Check PyQt6
    if ! $PYTHON_CMD -c "import PyQt6" 2>/dev/null; then
        echo -e "${YELLOW}Installing PyQt6...${NC}"
        $PYTHON_CMD -m pip install PyQt6
    fi
    
    # Check xdotool for window interaction
    if ! command -v xdotool &> /dev/null; then
        echo -e "${YELLOW}xdotool not found. Window interaction will be limited.${NC}"
        echo -e "${YELLOW}To install: sudo apt-get install xdotool${NC}"
    fi
}

# Main execution
echo -e "${CYAN}==================================${NC}"
echo -e "${CYAN}   Shimeji Mascot for Linux${NC}"
echo -e "${CYAN}==================================${NC}"
echo ""

check_python
install_deps

if check_display; then
    echo -e "${GREEN}Display detected. Running in desktop mode...${NC}"
    echo ""
    echo -e "${YELLOW}Tips:${NC}"
    echo "- Left click and drag to move the mascot"
    echo "- Right click for menu options"
    echo "- Press Ctrl+C to stop"
    echo ""
    
    $PYTHON_CMD main.py
else
    echo -e "${YELLOW}No display detected. Running with virtual display (Xvfb)...${NC}"
    
    # Check for xvfb
    if ! command -v xvfb-run &> /dev/null; then
        echo -e "${RED}Error: Xvfb not found. Please install it manually:${NC}"
        echo "  sudo apt-get install xvfb"
        exit 1
    fi
    
    # Run with virtual display
    xvfb-run -a -s "-screen 0 1280x720x24" $PYTHON_CMD main.py
fi
