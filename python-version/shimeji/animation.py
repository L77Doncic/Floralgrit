"""
Animation System - Frame playback and management
"""

from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from typing import List, Callable, Optional
from .config import Pose, Animation, Action


class AnimationPlayer(QObject):
    """Plays animation sequences"""
    
    frame_changed = pyqtSignal(str)  # Emits image path
    animation_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.current_poses: List[Pose] = []
        self.current_pose_index = 0
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_frame)
        self.frame_delay_ms = 16  # ~60fps
        self.is_playing = False
        self.on_frame_callback: Optional[Callable] = None
        self.on_complete_callback: Optional[Callable] = None
        
    def play(self, animation: Animation, on_frame: Callable = None, on_complete: Callable = None):
        """Play an animation"""
        if not animation.poses:
            if on_complete:
                on_complete()
            return
            
        self.current_poses = animation.poses
        self.current_pose_index = 0
        self.current_frame = 0
        self.on_frame_callback = on_frame
        self.on_complete_callback = on_complete
        self.is_playing = True
        
        # Show first frame
        self._show_current_pose()
        
        # Start timer
        self.timer.start(self.frame_delay_ms)
        
    def _on_frame(self):
        """Called on each frame tick"""
        if not self.is_playing or not self.current_poses:
            return
            
        self.current_frame += 1
        current_pose = self.current_poses[self.current_pose_index]
        
        # Check if pose duration elapsed
        if self.current_frame >= current_pose.duration:
            self.current_pose_index += 1
            self.current_frame = 0
            
            # Check if animation complete
            if self.current_pose_index >= len(self.current_poses):
                self.is_playing = False
                self.timer.stop()
                self.animation_finished.emit()
                if self.on_complete_callback:
                    self.on_complete_callback()
                return
                
            # Show next pose
            self._show_current_pose()
        else:
            # Continue current pose - call frame callback for movement
            if self.on_frame_callback:
                self.on_frame_callback(current_pose, self.current_frame)
                
    def _show_current_pose(self):
        """Display current pose"""
        if self.current_pose_index < len(self.current_poses):
            pose = self.current_poses[self.current_pose_index]
            self.frame_changed.emit(pose.image)
            
            if self.on_frame_callback:
                self.on_frame_callback(pose, 0)
                
    def stop(self):
        """Stop current animation"""
        self.is_playing = False
        self.timer.stop()
        
    def get_current_velocity(self) -> tuple:
        """Get current frame's velocity"""
        if self.current_pose_index < len(self.current_poses):
            return self.current_poses[self.current_pose_index].velocity
        return (0, 0)
