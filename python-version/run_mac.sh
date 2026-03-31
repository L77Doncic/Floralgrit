#!/bin/bash
# Shimeji Mascot Launcher Script for macOS
# Detects environment and runs with appropriate settings

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if we're in a graphical environment
check_display() {
    # On macOS, check if running under normal GUI (not SSH)
    if [ "$TERM_PROGRAM" = "Apple_Terminal" ] || [ "$TERM_PROGRAM" = "iTerm.app" ] || [ -z "$SSH_TTY" ]; then
        return 0
    fi
    return 1
}

# Check Python installation
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: Python not found. Please install Python 3.8 or higher.${NC}"
        echo "Visit: https://www.python.org/downloads/mac-osx/"
        exit 1
    fi
    
    # Check version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
}

# Install dependencies if needed
install_deps() {
    echo -e "${CYAN}Checking dependencies...${NC}"
    
    # Check if pip packages are installed
    if ! $PYTHON_CMD -c "import PyQt6" 2>/dev/null; then
        echo -e "${YELLOW}Installing PyQt6...${NC}"
        $PYTHON_CMD -m pip install PyQt6
    fi
    
    # Note: macOS doesn't need xdotool, window control uses AppleScript
    echo -e "${GREEN}Dependencies OK${NC}"
}

# Check for accessibility permissions (needed for window control)
check_accessibility() {
    echo -e "${CYAN}Note: If window interaction doesn't work, you may need to grant${NC}"
    echo -e "${CYAN}      accessibility permissions to your terminal application.${NC}"
    echo -e "${CYAN}      Go to: System Settings > Privacy & Security > Accessibility${NC}"
    echo ""
}

# Main execution
echo -e "${CYAN}==================================${NC}"
echo -e "${CYAN}   Shimeji Mascot for macOS${NC}"
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
    
    check_accessibility
    
    $PYTHON_CMD main.py
else
    echo -e "${YELLOW}No display detected. Running in headless mode...${NC}"
    echo -e "${RED}Note: macOS requires a graphical session to run Shimeji.${NC}"
    echo -e "${RED}      Please run this script from Terminal.app or iTerm2.${NC}"
    exit 1
fi
