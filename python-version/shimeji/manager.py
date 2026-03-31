"""
Mascot Manager - Handles multiple mascot instances and breeding
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Optional
from .mascot import Mascot

# Constants
MAX_MASCOTS = 50  # Match original Java limit


class MascotManager(QObject):
    """Manages multiple mascot instances"""
    
    mascot_added = pyqtSignal(object)  # Emits when new mascot created
    mascot_removed = pyqtSignal(object)  # Emits when mascot removed
    all_removed = pyqtSignal()  # Emits when all mascots removed
    
    def __init__(self, conf_dir: str = '../conf', img_dir: str = '../img'):
        super().__init__()
        
        self.conf_dir = conf_dir
        self.img_dir = img_dir
        self.mascots: List[Mascot] = []
        
    def create_mascot(self, x: int = None, y: int = None, initial_behavior: str = None) -> Optional[Mascot]:
        """Create a new mascot instance"""
        if len(self.mascots) >= MAX_MASCOTS:
            print(f"Max mascot limit ({MAX_MASCOTS}) reached")
            return None
            
        mascot = Mascot(conf_dir=self.conf_dir, img_dir=self.img_dir)
        
        # Set position if provided
        if x is not None and y is not None:
            mascot.x = x
            mascot.y = y
            mascot.window.set_position(x, y)
            
        # Set up breeding callback
        mascot.on_breed = self._on_mascot_breed
        mascot.total_count = len(self.mascots) + 1
        
        # Update mascot references
        self.mascots.append(mascot)
        self._update_total_counts()
        
        # Show window
        mascot.show()
        
        # Set initial behavior if provided
        if initial_behavior:
            behavior = mascot.config.get_behavior(initial_behavior)
            if behavior:
                mascot._execute_behavior(behavior)
                
        self.mascot_added.emit(mascot)
        print(f"Created mascot #{len(self.mascots)} at ({mascot.x}, {mascot.y})")
        
        return mascot
        
    def remove_mascot(self, mascot: Mascot):
        """Remove a mascot instance"""
        if mascot in self.mascots:
            mascot.window.close()
            self.mascots.remove(mascot)
            self._update_total_counts()
            self.mascot_removed.emit(mascot)
            
        if not self.mascots:
            self.all_removed.emit()
            
    def remove_all(self):
        """Remove all mascot instances"""
        for mascot in self.mascots[:]:
            mascot.window.close()
        self.mascots.clear()
        self.all_removed.emit()
        
    def _update_total_counts(self):
        """Update total count for all mascots"""
        total = len(self.mascots)
        for mascot in self.mascots:
            mascot.total_count = total
            
    def _on_mascot_breed(self, x: int, y: int, behavior: str):
        """Handle mascot breeding (引っこ抜く/分裂)"""
        if len(self.mascots) < MAX_MASCOTS:
            self.create_mascot(x, y, behavior)
        else:
            print(f"Cannot breed: max limit ({MAX_MASCOTS}) reached")
            
    def get_mascot_at(self, x: int, y: int, tolerance: int = 50) -> Optional[Mascot]:
        """Find mascot at given position"""
        for mascot in self.mascots:
            dx = mascot.x - x
            dy = mascot.y - y
            if abs(dx) < tolerance and abs(dy) < tolerance:
                return mascot
        return None
        
    def count(self) -> int:
        """Get number of active mascots"""
        return len(self.mascots)
