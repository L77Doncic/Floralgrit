#!/usr/bin/env python3
"""
Shimeji Mascot - Python Version
Main entry point

Usage:
    python main.py              # Run with one mascot
    python main.py --count 3    # Run with 3 mascots
    ./run.sh                    # Auto-detect environment and run

Requirements:
    pip install -r requirements.txt
    
    For window interaction on Linux:
        sudo apt-get install xdotool
"""

import sys
import os
import argparse
import random

# Add shimeji package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from shimeji.manager import MascotManager


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Shimeji Mascot Python Version')
    parser.add_argument('--count', '-n', type=int, default=1,
                        help='Number of mascot instances (default: 1, max: 50)')
    
    # Maximum mascot limit (match original Java)
    MAX_MASCOTS = 50
    parser.add_argument('--xvfb', action='store_true',
                        help='Force use of virtual display (Xvfb)')
    args = parser.parse_args()
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window closed
    
    # Paths to local resources (independent from java-original)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.join(base_dir, 'conf')
    img_dir = os.path.join(base_dir, 'img')
    
    # Create manager
    manager = MascotManager(conf_dir=conf_dir, img_dir=img_dir)
    manager.all_removed.connect(app.quit)
    
    # Create initial mascots
    count = min(max(args.count, 1), MAX_MASCOTS)
    for i in range(count):
        x = 200 + random.randint(0, 200)
        y = 200 + random.randint(0, 100)
        manager.create_mascot(x, y)
    
    print(f"Shimeji Mascot started!")
    print(f"Running {manager.count()} mascot(s)")
    print("Right-click on mascot for options")
    print("Press Ctrl+C in terminal to exit")
    print("")
    print("Features:")
    print("  - Drag mascot with left mouse button")
    print("  - Right-click for menu")
    print("  - Mascot will climb on active windows if xdotool is installed")
    print("  - Double-click on mascot may trigger split (引っこ抜く)")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
