"""
Action System - Executes different action types
"""

import os
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import Optional, Callable, Dict, Any
from .config import Action, Animation, evaluate_condition
from .animation import AnimationPlayer
from .window_control import get_window_controller, is_window_control_available, move_window, get_window_geometry


class ActionExecutor(QObject):
    """Executes mascot actions"""
    
    action_finished = pyqtSignal()
    image_changed = pyqtSignal(str)
    position_delta = pyqtSignal(int, int)  # dx, dy
    look_right_changed = pyqtSignal(bool)
    
    def __init__(self, mascot):
        super().__init__()
        
        self.mascot = mascot
        self.player = AnimationPlayer()
        self.player.frame_changed.connect(self.image_changed.emit)
        self.current_action: Optional[Action] = None
        self.is_executing = False
        self.look_right = True
        
    def execute(self, action: Action, params: Dict[str, Any] = None, on_complete: Callable = None):
        """Execute an action"""
        if self.is_executing:
            self.stop()
            
        self.current_action = action
        self.is_executing = True
        self._on_complete_callback = on_complete
        
        # Merge params
        merged_params = dict(action.params) if action.params else {}
        if params:
            merged_params.update(params)
            
        # Execute based on type
        if action.action_type == '静止':
            self._execute_static(action, merged_params)
        elif action.action_type == '移動':
            self._execute_move(action, merged_params)
        elif action.action_type == '固定':
            self._execute_fixed(action, merged_params)
        elif action.action_type == '複合':
            self._execute_composite(action, merged_params)
        elif action.action_type == '選択':
            self._execute_select(action, merged_params)
        elif action.action_type == '組み込み':
            self._execute_builtin(action, merged_params)
        else:
            self._finish()
            
    def stop(self):
        """Stop current action"""
        self.is_executing = False
        self.player.stop()
        
    def _execute_static(self, action: Action, params: Dict):
        """Execute static action (single pose for duration)"""
        if not action.animations:
            self._finish()
            return
            
        # Find matching animation by condition
        anim = self._select_animation(action.animations)
        if not anim:
            self._finish()
            return
            
        duration = self._parse_param(params.get('長さ', '100'), int)
        
        self.player.play(anim, on_complete=self._finish)
        
    def _execute_move(self, action: Action, params: Dict):
        """Execute move action (animation with movement)"""
        if not action.animations:
            self._finish()
            return
            
        anim = self._select_animation(action.animations)
        if not anim:
            self._finish()
            return
            
        dest_x = self._parse_param(params.get('目的地X'), float, None)
        dest_y = self._parse_param(params.get('目的地Y'), float, None)
        
        def on_frame(pose, frame):
            vx, vy = pose.velocity
            if not self.look_right:
                vx = -vx
            self.position_delta.emit(vx, vy)
            
        self.player.play(anim, on_frame=on_frame, on_complete=self._finish)
        
    def _execute_fixed(self, action: Action, params: Dict):
        """Execute fixed action (plays once without interruption)"""
        if not action.animations:
            self._finish()
            return
            
        anim = self._select_animation(action.animations)
        if anim:
            self.player.play(anim, on_complete=self._finish)
        else:
            self._finish()
            
    def _execute_composite(self, action: Action, params: Dict):
        """Execute composite action (sequence of sub-actions)"""
        self._execute_sub_actions(action.sub_actions, 0)
        
    def _execute_select(self, action: Action, params: Dict):
        """Execute select action (choose one sub-action)"""
        # Evaluate conditions and select first matching
        for sub in action.sub_actions:
            if 'nested' in sub:
                sub_action = sub['nested']
                # Check condition
                condition = sub_action.params.get('条件') if sub_action.params else None
                if condition is None or evaluate_condition(condition, self.mascot, self.mascot.environment):
                    self.execute(sub_action, {}, self._finish)
                    return
            elif 'name' in sub:
                # Reference to named action
                ref_params = sub.get('params', {})
                condition = ref_params.get('条件')
                if condition is None or evaluate_condition(condition, self.mascot, self.mascot.environment):
                    next_action = self.mascot.config.get_action(sub['name'])
                    if next_action:
                        self.execute(next_action, ref_params, self._finish)
                        return
                    
        self._finish()
        
    def _execute_builtin(self, action: Action, params: Dict):
        """Execute built-in action (jump, fall, drag, etc.)"""
        builtin_class = action.builtin_class
        
        if 'Jump' in builtin_class:
            self._execute_jump(params)
        elif 'Fall' in builtin_class:
            self._execute_fall(params)
        elif 'Dragged' in builtin_class:
            self._execute_dragged(params)
        elif 'Look' in builtin_class:
            self._execute_look(params)
        elif 'FallWithIE' in builtin_class:
            self._execute_fall_with_ie(action, params)
        elif 'WalkWithIE' in builtin_class:
            self._execute_walk_with_ie(action, params)
        elif 'ThrowIE' in builtin_class:
            self._execute_throw_ie(action, params)
        elif 'Regist' in builtin_class:
            self._execute_resist(action, params)
        elif 'Breed' in builtin_class:
            self._execute_breed(action, params)
        else:
            # Default: just play animation if available
            if action.animations:
                anim = action.animations[0]
                self.player.play(anim, on_complete=self._finish)
            else:
                self._finish()
                
    def _execute_jump(self, params: Dict):
        """Execute jump action"""
        dest_x = self._parse_param(params.get('目的地X'), float, self.mascot.x)
        dest_y = self._parse_param(params.get('目的地Y'), float, self.mascot.y)
        velocity = self._parse_param(params.get('速度', '20'), float)
        
        # Simple jump physics
        self.mascot.target_x = dest_x
        self.mascot.target_y = dest_y
        self._finish()
        
    def _execute_fall(self, params: Dict):
        """Execute fall action"""
        vx = self._parse_param(params.get('初速X', '0'), float)
        vy = self._parse_param(params.get('初速Y', '0'), float)
        gravity = self._parse_param(params.get('重力', '2'), float)
        
        # Fall until hitting floor
        self.mascot.velocity_x = vx
        self.mascot.velocity_y = vy
        self._finish()
        
    def _execute_dragged(self, params: Dict):
        """Execute dragged action"""
        # Follow cursor
        self.mascot.is_dragged = True
        self._finish()
        
    def _execute_look(self, params: Dict):
        """Execute look/turn action"""
        right = params.get('右向き')
        if right is not None:
            # Evaluate if needed
            if isinstance(right, str) and right.startswith('${'):
                # Use safe expression evaluator
                from .config import SafeExpressionEvaluator
                evaluator = SafeExpressionEvaluator(self.mascot, self.mascot.environment)
                try:
                    right = evaluator.evaluate(right[2:-1])
                except:
                    right = True
            else:
                right = str(right).lower() == 'true'
            self.look_right = right
            self.look_right_changed.emit(right)
        self._finish()
        
    def _execute_sub_actions(self, sub_actions: list, index: int):
        """Execute sub-actions sequentially"""
        if index >= len(sub_actions):
            self._finish()
            return
            
        sub = sub_actions[index]
        
        if 'nested' in sub:
            # Inline action
            self.execute(sub['nested'], {}, 
                        lambda: self._execute_sub_actions(sub_actions, index + 1))
        elif 'name' in sub:
            # Named action reference
            action = self.mascot.config.get_action(sub['name'])
            if action:
                self.execute(action, sub.get('params', {}),
                           lambda: self._execute_sub_actions(sub_actions, index + 1))
            else:
                self._execute_sub_actions(sub_actions, index + 1)
        else:
            self._execute_sub_actions(sub_actions, index + 1)
            
    def _select_animation(self, animations: list) -> Optional[Animation]:
        """Select animation matching current conditions"""
        for anim in animations:
            if anim.condition is None:
                return anim
            if evaluate_condition(anim.condition, self.mascot, self.mascot.environment):
                return anim
        return animations[0] if animations else None
        
    def _parse_param(self, value, type_func, default=None):
        """Parse parameter value using safe expression evaluator"""
        if value is None:
            return default
        if isinstance(value, str) and value.startswith('${'):
            # Expression - use safe evaluator
            from .config import SafeExpressionEvaluator
            evaluator = SafeExpressionEvaluator(self.mascot, self.mascot.environment)
            try:
                result = evaluator.evaluate(value[2:-1])
                return type_func(result)
            except:
                return default
        try:
            return type_func(value)
        except:
            return default
            
    def _execute_fall_with_ie(self, action: Action, params: Dict):
        """Execute fall with IE (grab window and fall with it)"""
        # IE offset from mascot
        ie_offset_x = self._parse_param(params.get('IEの端X', '0'), int, 0)
        ie_offset_y = self._parse_param(params.get('IEの端Y', '0'), int, -64)
        
        # Start tracking IE
        self.mascot.grabbed_ie = True
        self.mascot.ie_offset_x = ie_offset_x
        self.mascot.ie_offset_y = ie_offset_y
        
        # Play animation with falling physics
        if action.animations:
            def on_frame(pose, frame):
                vx, vy = pose.velocity
                self.position_delta.emit(vx, vy)
                # Move IE with mascot
                self._move_ie_with_mascot()
                
            self.player.play(action.animations[0], on_frame=on_frame, on_complete=self._finish)
        else:
            self._finish()
            
    def _execute_walk_with_ie(self, action: Action, params: Dict):
        """Execute walk while carrying IE"""
        ie_offset_x = self._parse_param(params.get('IEの端X', '0'), int, 0)
        ie_offset_y = self._parse_param(params.get('IEの端Y', '0'), int, -64)
        
        self.mascot.ie_offset_x = ie_offset_x
        self.mascot.ie_offset_y = ie_offset_y
        
        if action.animations:
            dest_x = self._parse_param(params.get('目的地X'), float, None)
            
            def on_frame(pose, frame):
                vx, vy = pose.velocity
                if not self.look_right:
                    vx = -vx
                self.position_delta.emit(vx, vy)
                self._move_ie_with_mascot()
                
            self.player.play(action.animations[0], on_frame=on_frame, on_complete=self._finish)
        else:
            self._finish()
            
    def _execute_throw_ie(self, action: Action, params: Dict):
        """Execute throw IE action"""
        # Get throw parameters
        initial_vx = self._parse_param(params.get('初速X', '32'), float, 32)
        initial_vy = self._parse_param(params.get('初速Y', '-10'), float, -10)
        gravity = self._parse_param(params.get('重力', '0.5'), float, 0.5)
        
        # Release IE
        self._throw_ie(initial_vx, initial_vy, gravity)
        self.mascot.grabbed_ie = False
        
        if action.animations:
            self.player.play(action.animations[0], on_complete=self._finish)
        else:
            self._finish()
            
    def _execute_resist(self, action: Action, params: Dict):
        """Execute resist action (when being dragged)"""
        if action.animations:
            self.player.play(action.animations[0], on_complete=self._finish)
        else:
            self._finish()
            
    def _execute_breed(self, action: Action, params: Dict):
        """Execute breed/duplicate action (引っこ抜く/分裂)"""
        # Parse spawn location
        spawn_x = self._parse_param(params.get('生まれる場所X', '-32'), int, -32)
        spawn_y = self._parse_param(params.get('生まれる場所Y', '96'), int, 96)
        spawn_behavior = params.get('生まれた時の行動', '引っこ抜かれる')
        
        # Signal to create new mascot instance
        if hasattr(self.mascot, 'on_breed'):
            spawn_world_x = self.mascot.x + spawn_x
            spawn_world_y = self.mascot.y + spawn_y
            self.mascot.on_breed(spawn_world_x, spawn_world_y, spawn_behavior)
            
        if action.animations:
            self.player.play(action.animations[0], on_complete=self._finish)
        else:
            self._finish()
            
    def _move_ie_with_mascot(self):
        """Move the active IE window with the mascot"""
        if not self.mascot.grabbed_ie:
            return
            
        # SECURITY: Only move windows if explicitly enabled via environment variable
        # This prevents accidental window manipulation
        if os.environ.get('SHIMEJI_ALLOW_WINDOW_CONTROL', '0') != '1':
            return
            
        # Check if window control is available
        if not is_window_control_available():
            return
            
        # Calculate IE position based on mascot position
        ie_x = self.mascot.x + self.mascot.ie_offset_x
        ie_y = self.mascot.y + self.mascot.ie_offset_y
        
        # Use cross-platform window controller
        try:
            controller = get_window_controller()
            window_info = controller.get_active_window()
            if window_info:
                window_id = window_info['id']
                move_window(window_id, int(ie_x), int(ie_y))
        except Exception:
            pass  # Silently fail if can't move window
            
    def _throw_ie(self, vx: float, vy: float, gravity: float):
        """Throw the IE window with physics"""
        # SECURITY: Only throw windows if explicitly enabled via environment variable
        if os.environ.get('SHIMEJI_ALLOW_WINDOW_CONTROL', '0') != '1':
            return
            
        # Check if window control is available
        if not is_window_control_available():
            return
            
        try:
            controller = get_window_controller()
            
            # Get active window
            window_info = controller.get_active_window()
            if window_info is None:
                return
                
            window_id = window_info['id']
            x = window_info['x']
            y = window_info['y']
            
            # Apply throw physics (simple simulation)
            velocity_x = vx
            velocity_y = vy
            
            # Animate throw over several frames
            for _ in range(20):
                x += velocity_x
                y += velocity_y
                velocity_y += gravity  # Apply gravity
                
                # Move window
                move_window(window_id, int(x), int(y))
                time.sleep(0.03)  # ~30fps
                
        except Exception:
            pass
            
    def _finish(self):
        """Finish current action"""
        self.is_executing = False
        self.action_finished.emit()
        if self._on_complete_callback:
            self._on_complete_callback()
