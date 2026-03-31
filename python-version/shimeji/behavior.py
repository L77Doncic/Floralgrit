"""
Behavior System - Behavior tree and selection based on conditions
"""

import random
from typing import List, Optional, Dict
from .config import Behavior, BehaviorRef, evaluate_condition


class BehaviorManager:
    """Manages mascot behaviors"""
    
    def __init__(self, config):
        self.config = config
        self.current_behavior: Optional[Behavior] = None
        
    def select_behavior(self, mascot, environment) -> Optional[Behavior]:
        """Select next behavior based on conditions and frequencies"""
        candidates = []
        
        for name, behavior in self.config.behaviors.items():
            # Check if behavior is valid in current context
            if behavior.frequency <= 0:
                continue
                
            # Evaluate condition
            if behavior.condition:
                if not evaluate_condition(behavior.condition, mascot, environment):
                    continue
                    
            candidates.append((behavior, behavior.frequency))
            
        if not candidates:
            return None
            
        # Weighted random selection
        total_weight = sum(w for _, w in candidates)
        r = random.randint(1, total_weight)
        
        cumulative = 0
        for behavior, weight in candidates:
            cumulative += weight
            if r <= cumulative:
                self.current_behavior = behavior
                return behavior
                
        return candidates[-1][0] if candidates else None
        
    def get_next_behavior(self, mascot, environment) -> Optional[str]:
        """Get next behavior from current behavior's next list"""
        if not self.current_behavior or not self.current_behavior.next_behaviors:
            return None
            
        candidates = []
        for ref in self.current_behavior.next_behaviors:
            # Check condition
            if ref.condition:
                if not evaluate_condition(ref.condition, mascot, environment):
                    continue
                    
            candidates.append((ref.name, ref.frequency))
            
        if not candidates:
            return None
            
        # Weighted random selection
        total_weight = sum(w for _, w in candidates)
        r = random.randint(1, total_weight)
        
        cumulative = 0
        for name, weight in candidates:
            cumulative += weight
            if r <= cumulative:
                return name
                
        return candidates[-1][0] if candidates else None
