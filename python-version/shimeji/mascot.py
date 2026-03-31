"""
Main Mascot Class - Coordinates all systems
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from .window import MascotWindow
from .config import ConfigParser
from .action import ActionExecutor
from .behavior import BehaviorManager
from .environment import Environment


class Mascot(QObject):
    """Main mascot controller"""
    
    def __init__(self, conf_dir: str = '../conf', img_dir: str = '../img'):
        super().__init__()
        
        # Configuration
        self.config = ConfigParser(conf_dir)
        self.config.parse_all()
        
        # Environment
        self.environment = Environment()
        
        # Window
        self.window = MascotWindow(img_dir)
        self.window.mouse_pressed.connect(self._on_mouse_press)
        self.window.mouse_moved.connect(self._on_mouse_move)
        self.window.mouse_released.connect(self._on_mouse_release)
        
        # Action and behavior systems
        self.executor = ActionExecutor(self)
        self.executor.image_changed.connect(self.window.set_image)
        self.executor.position_delta.connect(self._on_position_delta)
        self.executor.look_right_changed.connect(self._on_look_right)
        self.executor.action_finished.connect(self._on_action_finished)
        
        self.behavior_manager = BehaviorManager(self.config)
        
        # State
        self.x = 200
        self.y = 200
        self.velocity_x = 0
        self.velocity_y = 0
        self.look_right = True
        self.is_dragged = False
        self.is_falling = False
        self.total_count = 1
        
        # IE window interaction state
        self.grabbed_ie = False
        self.ie_offset_x = 0
        self.ie_offset_y = -64
        
        # Breeding callback
        self.on_breed = None  # Set by manager to handle creating new instances
        
        # Position window
        self.window.set_position(self.x, self.y)
        
        # Behavior timer
        self._behavior_timer = QTimer()
        self._behavior_timer.timeout.connect(self._update)
        self._behavior_timer.start(16)  # ~60fps
        
        self._current_action_name = None
        self._start_next_behavior()
        
    def show(self):
        """Show the mascot window"""
        self.window.show()
        
    def _start_next_behavior(self):
        """Start next behavior"""
        # Check if we should continue with next from current behavior
        next_name = self.behavior_manager.get_next_behavior(self, self.environment)
        
        if next_name:
            behavior = self.config.get_behavior(next_name)
        else:
            behavior = self.behavior_manager.select_behavior(self, self.environment)
            
        if behavior:
            self._execute_behavior(behavior)
        else:
            # Default behavior
            self._execute_action_name('立つ')
            
    def _execute_behavior(self, behavior):
        """Execute a behavior (maps to action)"""
        action_name = behavior.name
        action = self.config.get_action(action_name)
        
        if action:
            self._current_action_name = action_name
            self.executor.execute(action, {}, self._on_action_finished)
        else:
            # Try to find a matching action or use default
            self._execute_action_name('立つ')
            
    def _execute_action_name(self, name: str):
        """Execute action by name"""
        action = self.config.get_action(name)
        if action:
            self._current_action_name = name
            self.executor.execute(action, {}, self._on_action_finished)
        else:
            QTimer.singleShot(100, self._start_next_behavior)
            
    def _on_action_finished(self):
        """Called when action completes"""
        self._start_next_behavior()
        
    def _on_position_delta(self, dx: int, dy: int):
        """Handle position change from action"""
        if self.is_dragged:
            return
            
        self.x += dx if self.look_right else -dx
        self.y += dy
        self.window.set_position(self.x, self.y)
        
    def _on_look_right(self, right: bool):
        """Handle look direction change"""
        self.look_right = right
        
    def _on_mouse_press(self, pos):
        """Handle mouse press"""
        # Start dragged action
        action = self.config.get_action('ドラッグされる')
        if action:
            self.executor.execute(action)
            
    def _on_mouse_move(self, pos):
        """Handle mouse move (dragging)"""
        pass
        
    def _on_mouse_release(self):
        """Handle mouse release"""
        self.is_dragged = False
        # Start thrown action
        action = self.config.get_action('投げられる')
        if action:
            self.executor.execute(action, {}, self._on_action_finished)
            
    def _update(self):
        """Main update loop"""
        # Handle falling physics
        if self.is_falling:
            self.velocity_y += 2  # Gravity
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            # Check floor collision
            if self.y >= self.environment.workArea.bottom - 128:
                self.y = self.environment.workArea.bottom - 128
                self.is_falling = False
                self.velocity_x = 0
                self.velocity_y = 0
                
            self.window.set_position(self.x, self.y)
            
    @property
    def anchor(self):
        """Get anchor point"""
        class Anchor:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        return Anchor(self.x + 64, self.y + 128)
