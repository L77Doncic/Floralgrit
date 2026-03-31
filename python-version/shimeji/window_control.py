"""
Cross-platform window control module
Supports Windows (Win32 API), macOS (AppleScript/PyObjC), and Linux (xdotool)
"""

import os
import platform
import subprocess
import shutil
import logging
from typing import Optional, Tuple, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

__all__ = [
    'WindowController',
    'LinuxX11Controller',
    'WindowsController', 
    'MacOSController',
    'get_window_controller',
    'is_window_control_available',
    'get_active_window',
    'move_window',
    'get_window_geometry',
]


class WindowController(ABC):
    """Abstract base class for window control"""
    
    @abstractmethod
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get active window info: {'id': str, 'x': int, 'y': int, 'width': int, 'height': int}"""
        pass
    
    @abstractmethod
    def move_window(self, window_id: str, x: int, y: int) -> bool:
        """Move window to position (x, y)"""
        pass
    
    @abstractmethod
    def get_window_geometry(self, window_id: str) -> Optional[Tuple[int, int, int, int]]:
        """Get window geometry: (x, y, width, height)"""
        pass
    
    def is_available(self) -> bool:
        """Check if this controller is available on current system"""
        return True


class LinuxX11Controller(WindowController):
    """Linux X11 window controller using xdotool"""
    
    def __init__(self):
        self._has_xdotool = shutil.which('xdotool') is not None
        self._has_xwininfo = shutil.which('xwininfo') is not None
        self._has_xprop = shutil.which('xprop') is not None
        
    def is_available(self) -> bool:
        return self._has_xdotool or self._has_xwininfo
    
    def _validate_window_id(self, window_id: str) -> bool:
        """Validate X11 window ID (decimal or hex format like 0x1a00003)"""
        if not window_id:
            return False
        # Remove '0x' or '0X' prefix if present
        clean_id = window_id.lower().replace('0x', '')
        # Allow hex digits (0-9, a-f)
        return all(c in '0123456789abcdef' for c in clean_id)
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        if not self._has_xdotool:
            return self._get_active_window_fallback()
            
        try:
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True, text=True, timeout=0.5
            )
            if result.returncode != 0:
                return None
                
            window_id = result.stdout.strip()
            if not window_id or window_id == '0':
                return None
                
            geo = self.get_window_geometry(window_id)
            if geo:
                x, y, w, h = geo
                return {
                    'id': window_id,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                }
        except Exception:
            pass
        return None
    
    def _get_active_window_fallback(self) -> Optional[Dict[str, Any]]:
        """Fallback using xprop and xwininfo"""
        if not self._has_xprop or not self._has_xwininfo:
            return None
            
        try:
            result = subprocess.run(
                ['xprop', '-root', '_NET_ACTIVE_WINDOW'],
                capture_output=True, text=True, timeout=0.5
            )
            if result.returncode != 0:
                return None
                
            line = result.stdout.strip()
            if 'window id #' not in line:
                return None
                
            window_id = line.split('window id #')[-1].strip()
            geo = self.get_window_geometry(window_id)
            if geo:
                x, y, w, h = geo
                return {
                    'id': window_id,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                }
        except Exception:
            pass
        return None
    
    def move_window(self, window_id: str, x: int, y: int) -> bool:
        if not self._has_xdotool:
            return False
            
        try:
            # SECURITY: Validate window ID (supports decimal and hex)
            if not self._validate_window_id(window_id):
                return False
                
            result = subprocess.run(
                ['xdotool', 'windowmove', window_id, str(int(x)), str(int(y))],
                capture_output=True, timeout=0.5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_window_geometry(self, window_id: str) -> Optional[Tuple[int, int, int, int]]:
        if not self._has_xdotool:
            return self._get_geometry_with_xwininfo(window_id)
            
        try:
            result = subprocess.run(
                ['xdotool', 'getwindowgeometry', window_id],
                capture_output=True, text=True, timeout=0.5
            )
            if result.returncode != 0:
                return None
                
            lines = result.stdout.strip().split('\n')
            pos_line = [l for l in lines if 'Position:' in l]
            geo_line = [l for l in lines if 'Geometry:' in l]
            
            if pos_line and geo_line:
                pos_part = pos_line[0].split(':')[1].split('(')[0].strip()
                x, y = map(int, pos_part.split(','))
                
                geo_part = geo_line[0].split(':')[1].strip()
                w, h = map(int, geo_part.split('x'))
                
                return (x, y, w, h)
        except Exception:
            pass
        return None
    
    def _get_geometry_with_xwininfo(self, window_id: str) -> Optional[Tuple[int, int, int, int]]:
        """Fallback using xwininfo"""
        if not self._has_xwininfo:
            return None
            
        try:
            result = subprocess.run(
                ['xwininfo', '-id', window_id],
                capture_output=True, text=True, timeout=0.5
            )
            if result.returncode != 0:
                return None
                
            x, y, w, h = 0, 0, 0, 0
            for line in result.stdout.split('\n'):
                if 'Absolute upper-left X:' in line:
                    x = int(line.split(':')[1].strip())
                elif 'Absolute upper-left Y:' in line:
                    y = int(line.split(':')[1].strip())
                elif 'Width:' in line:
                    w = int(line.split(':')[1].strip())
                elif 'Height:' in line:
                    h = int(line.split(':')[1].strip())
                    
            if w > 0 and h > 0:
                return (x, y, w, h)
        except Exception:
            pass
        return None


class WindowsController(WindowController):
    """Windows window controller using Win32 API"""
    
    def __init__(self):
        self._win32_available = False
        self._user32 = None
        self._ctypes = None
        self._wintypes = None
        try:
            import ctypes
            from ctypes import wintypes
            self._ctypes = ctypes
            self._wintypes = wintypes
            self._user32 = ctypes.windll.user32
            
            # Set up function signatures for type safety
            self._user32.GetForegroundWindow.argtypes = []
            self._user32.GetForegroundWindow.restype = wintypes.HWND
            
            self._user32.GetWindowRect.argtypes = [wintypes.HWND, self._ctypes.POINTER(wintypes.RECT)]
            self._user32.GetWindowRect.restype = wintypes.BOOL
            
            self._user32.SetWindowPos.argtypes = [
                wintypes.HWND, wintypes.HWND,
                self._ctypes.c_int, self._ctypes.c_int, self._ctypes.c_int, self._ctypes.c_int,
                self._ctypes.c_uint
            ]
            self._user32.SetWindowPos.restype = wintypes.BOOL
            
            self._win32_available = True
        except (ImportError, AttributeError):
            pass
    
    def is_available(self) -> bool:
        return self._win32_available
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        if not self._win32_available:
            return None
            
        try:
            # Get foreground window
            hwnd = self._user32.GetForegroundWindow()
            if not hwnd or hwnd == 0:
                return None
                
            # Get window rect
            rect = self._wintypes.RECT()
            if not self._user32.GetWindowRect(hwnd, self._ctypes.byref(rect)):
                return None
                
            x = rect.left
            y = rect.top
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            
            return {
                'id': str(hwnd),
                'x': x,
                'y': y,
                'width': w,
                'height': h
            }
        except Exception:
            return None
    
    def move_window(self, window_id: str, x: int, y: int) -> bool:
        if not self._win32_available:
            return False
            
        try:
            # Validate and convert window ID
            hwnd_val = int(window_id)
            # HWND should be a positive integer within valid range
            if hwnd_val <= 0 or hwnd_val > 0xFFFFFFFF:
                return False
            hwnd = self._wintypes.HWND(hwnd_val)
            
            # SWP flags
            SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004
            SWP_SHOWWINDOW = 0x0040
            
            result = self._user32.SetWindowPos(
                hwnd,
                self._wintypes.HWND(0),  # HWND_TOP (0)
                int(x), int(y), 0, 0,
                SWP_NOSIZE | SWP_NOZORDER | SWP_SHOWWINDOW
            )
            return result != 0
        except (ValueError, OverflowError):
            return False
        except Exception:
            return False
    
    def get_window_geometry(self, window_id: str) -> Optional[Tuple[int, int, int, int]]:
        if not self._win32_available:
            return None
            
        try:
            # Validate and convert window ID
            hwnd_val = int(window_id)
            if hwnd_val <= 0 or hwnd_val > 0xFFFFFFFF:
                return False
            hwnd = self._wintypes.HWND(hwnd_val)
            
            rect = self._wintypes.RECT()
            
            if not self._user32.GetWindowRect(hwnd, self._ctypes.byref(rect)):
                return None
                
            x = rect.left
            y = rect.top
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            
            return (x, y, w, h)
        except (ValueError, OverflowError):
            return None
        except Exception:
            return None


class MacOSController(WindowController):
    """macOS window controller using AppleScript"""
    
    def __init__(self):
        self._osascript_available = shutil.which('osascript') is not None
        
    def is_available(self) -> bool:
        return self._osascript_available and platform.system() == 'Darwin'
    
    def _run_applescript(self, script: str) -> Optional[str]:
        """Run AppleScript and return output"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        if not self._osascript_available:
            return None
            
        try:
            # Get frontmost application and its front window
            script = '''
                tell application "System Events"
                    set frontApp to first application process whose frontmost is true
                    set frontAppName to name of frontApp
                    tell process frontAppName
                        set frontWin to first window
                        set winPos to position of frontWin
                        set winSize to size of frontWin
                        return frontAppName & "|" & (item 1 of winPos) & "," & (item 2 of winPos) & "," & (item 1 of winSize) & "," & (item 2 of winSize)
                    end tell
                end tell
            '''
            output = self._run_applescript(script)
            if not output or '|' not in output:
                return None
                
            parts = output.split('|')
            app_name = parts[0]
            geo_parts = parts[1].split(',')
            
            if len(geo_parts) == 4:
                x, y, w, h = map(int, geo_parts)
                return {
                    'id': app_name,  # Use app name as window ID on macOS
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                }
        except Exception:
            pass
        return None
    
    def move_window(self, window_id: str, x: int, y: int) -> bool:
        if not self._osascript_available:
            return False
            
        try:
            # Move the front window of the frontmost application
            # window_id is the app name on macOS
            script = f'''
                tell application "System Events"
                    tell process "{window_id}"
                        set position of first window to {{{int(x)}, {int(y)}}}
                    end tell
                end tell
            '''
            output = self._run_applescript(script)
            return output is not None
        except Exception:
            return False
    
    def get_window_geometry(self, window_id: str) -> Optional[Tuple[int, int, int, int]]:
        if not self._osascript_available:
            return None
            
        try:
            script = '''
                tell application "System Events"
                    set frontApp to first application process whose frontmost is true
                    tell frontApp
                        set frontWin to first window
                        set winPos to position of frontWin
                        set winSize to size of frontWin
                        return (item 1 of winPos) & "," & (item 2 of winPos) & "," & (item 1 of winSize) & "," & (item 2 of winSize)
                    end tell
                end tell
            '''
            output = self._run_applescript(script)
            if output:
                parts = output.split(',')
                if len(parts) == 4:
                    return tuple(map(int, parts))
        except Exception:
            pass
        return None


# Global controller instance
_controller: Optional[WindowController] = None

def get_window_controller() -> WindowController:
    """Get the appropriate window controller for current platform"""
    global _controller
    
    if _controller is not None:
        return _controller
        
    system = platform.system()
    
    if system == 'Windows':
        _controller = WindowsController()
    elif system == 'Darwin':
        _controller = MacOSController()
    else:  # Linux and others
        _controller = LinuxX11Controller()
        
    return _controller


def is_window_control_available() -> bool:
    """Check if window control is available on current system"""
    controller = get_window_controller()
    return controller.is_available()


def get_active_window() -> Optional[Dict[str, Any]]:
    """Get active window information"""
    controller = get_window_controller()
    return controller.get_active_window()


def move_window(window_id: str, x: int, y: int) -> bool:
    """Move window to position"""
    controller = get_window_controller()
    return controller.move_window(window_id, x, y)


def get_window_geometry(window_id: str) -> Optional[Tuple[int, int, int, int]]:
    """Get window geometry"""
    controller = get_window_controller()
    return controller.get_window_geometry(window_id)
