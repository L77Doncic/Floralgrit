"""
Environment - Screen detection, cursor tracking, window borders
"""

from PyQt6.QtCore import QPoint, QRect, QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication
from typing import Optional

from .window_control import get_window_controller, is_window_control_available


class Cursor:
    """Mouse cursor tracking"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dx = 0  # Delta x
        self.dy = 0  # Delta y
        self._last_pos = QPoint(0, 0)
        
    def update(self):
        """Update cursor position"""
        pos = QCursor.pos()
        self.x = pos.x()
        self.y = pos.y()
        self.dx = self.x - self._last_pos.x()
        self.dy = self.y - self._last_pos.y()
        self._last_pos = pos


class Border:
    """Screen or window border for collision detection"""
    def __init__(self, rect: QRect):
        self.rect = rect
        
    def isOn(self, anchor: QPoint, tolerance: int = 10) -> bool:
        """Check if anchor is on/near this border"""
        # Simplified check - can be expanded based on border type
        return (abs(anchor.x() - self.rect.left()) < tolerance or
                abs(anchor.x() - self.rect.right()) < tolerance or
                abs(anchor.y() - self.rect.top()) < tolerance or
                abs(anchor.y() - self.rect.bottom()) < tolerance)


class ActiveIE:
    """Active window detection for mascot interaction
    
    Detects the currently focused/active window and provides
    its geometry for mascot behaviors like climbing on windows,
    walking on window borders, etc.
    
    Supports Windows, macOS, and Linux (X11).
    """
    def __init__(self):
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.width = 0
        self.height = 0
        self.visible = False
        self._window_id: Optional[str] = None
        self._controller = get_window_controller()
        
        # Borders - initialized as empty
        self.topBorder = Border(QRect(0, 0, 0, 1))
        self.bottomBorder = Border(QRect(0, 0, 0, 1))
        self.leftBorder = Border(QRect(0, 0, 1, 0))
        self.rightBorder = Border(QRect(0, 0, 1, 0))
        
    def update(self):
        """Update active window info using platform-specific method"""
        if is_window_control_available():
            self._update_with_controller()
        else:
            self._update_fallback()
            
    def _update_with_controller(self):
        """Get active window geometry using cross-platform controller"""
        try:
            window_info = self._controller.get_active_window()
            if window_info is None:
                self.visible = False
                return
                
            self._window_id = window_info['id']
            self.left = window_info['x']
            self.top = window_info['y']
            self.width = window_info['width']
            self.height = window_info['height']
            self.right = self.left + self.width
            self.bottom = self.top + self.height
            self.visible = (self.width > 100 and self.height > 100)
            
            self._update_borders()
                
        except Exception:
            self.visible = False
            
    def _update_fallback(self):
        """Fallback: Use a simulated window area or screen portion"""
        # When no window detection is available, create a simulated
        # "active window" in the center of the screen for testing
        screen = QApplication.primaryScreen()
        geo = screen.geometry()
        
        # Create a virtual window in the center (for testing behaviors)
        self.width = int(geo.width() * 0.5)
        self.height = int(geo.height() * 0.5)
        self.left = int((geo.width() - self.width) / 2)
        self.top = int((geo.height() - self.height) / 3)  # Upper portion
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.visible = True
        self._window_id = None
        
        self._update_borders()
        
    def _update_borders(self):
        """Update border objects with current geometry"""
        self.topBorder = Border(QRect(self.left, self.top, self.width, 1))
        self.bottomBorder = Border(QRect(self.left, self.bottom, self.width, 1))
        self.leftBorder = Border(QRect(self.left, self.top, 1, self.height))
        self.rightBorder = Border(QRect(self.right, self.top, 1, self.height))


class WorkArea:
    """Screen work area (excluding taskbar)"""
    def __init__(self):
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        
        self.left = geometry.left()
        self.right = geometry.right()
        self.top = geometry.top()
        self.bottom = geometry.bottom()
        self.width = geometry.width()
        self.height = geometry.height()
        
        # Borders
        self.leftBorder = Border(geometry)
        self.rightBorder = Border(geometry)
        self.topBorder = Border(geometry)
        self.bottomBorder = Border(geometry)


class Screen:
    """Full screen dimensions"""
    def __init__(self):
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        
        self.width = geometry.width()
        self.height = geometry.height()


class Environment:
    """Complete environment state"""
    def __init__(self):
        self.cursor = Cursor()
        self.workArea = WorkArea()
        self.screen = Screen()
        self.activeIE = ActiveIE()
        self.floor = self.workArea.bottomBorder  # Alias for convenience
        self.ceiling = self.workArea.topBorder
        
        # Update timer
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(16)  # ~60fps
        
    def update(self):
        """Update environment state"""
        self.cursor.update()
        self.activeIE.update()
