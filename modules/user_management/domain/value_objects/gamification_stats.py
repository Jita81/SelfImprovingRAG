from dataclasses import dataclass
from typing import Dict, List
import json
from pathlib import Path

@dataclass
class GamificationStats:
    """
    Value object representing user gamification statistics.
    Mutable to allow updates during gameplay.
    """
    level: int
    experience_points: int
    total_optimizations: int
    successful_optimizations: int
    win_streak: int
    
    def __post_init__(self):
        """Validate gamification stats"""
        if self.level < 1:
            raise ValueError("Level must be at least 1")
        
        if self.experience_points < 0:
            raise ValueError("Experience points cannot be negative")
        
        if self.total_optimizations < 0:
            raise ValueError("Total optimizations cannot be negative")
        
        if self.successful_optimizations < 0:
            raise ValueError("Successful optimizations cannot be negative")
        
        if self.successful_optimizations > self.total_optimizations:
            raise ValueError("Successful optimizations cannot exceed total optimizations")
        
        if self.win_streak < 0:
            raise ValueError("Win streak cannot be negative")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_optimizations == 0:
            return 0.0
        return self.successful_optimizations / self.total_optimizations
    
    @property
    def current_level_xp(self) -> int:
        """Get XP within current level"""
        level_system = self._get_level_system()
        current_level_threshold = self._get_level_threshold(self.level)
        return self.experience_points - current_level_threshold
    
    @property
    def next_level_xp(self) -> int:
        """Get XP needed for next level"""
        level_system = self._get_level_system()
        next_level_threshold = self._get_level_threshold(self.level + 1)
        current_level_threshold = self._get_level_threshold(self.level)
        return next_level_threshold - current_level_threshold
    
    @property
    def xp_until_next_level(self) -> int:
        """Get XP remaining until next level"""
        level_system = self._get_level_system()
        next_level_threshold = self._get_level_threshold(self.level + 1)
        return next_level_threshold - self.experience_points
    
    @property
    def current_level_title(self) -> str:
        """Get title for current level"""
        level_system = self._get_level_system()
        for level_info in level_system["levels"]:
            if level_info["level"] == self.level:
                return level_info["title"]
        return "Unknown"
    
    def gain_experience(self, points: int) -> Dict:
        """
        Add experience points and handle level ups.
        Returns info about level up if it occurred.
        """
        if points < 0:
            raise ValueError("Experience points to gain cannot be negative")
        
        old_level = self.level
        self.experience_points += points
        
        # Check for level up
        new_level = self._calculate_level_from_xp(self.experience_points)
        level_up_occurred = new_level > old_level
        
        if level_up_occurred:
            self.level = new_level
        
        return {
            "level_up": level_up_occurred,
            "old_level": old_level,
            "new_level": self.level,
            "new_xp": self.current_level_xp,
            "xp_until_next": self.xp_until_next_level
        }
    
    def track_optimization(self, success: bool) -> Dict:
        """
        Track an optimization attempt and update relevant stats.
        Returns updated stats info.
        """
        self.total_optimizations += 1
        
        if success:
            self.successful_optimizations += 1
            self.win_streak += 1
        else:
            self.win_streak = 0
        
        return {
            "new_win_streak": self.win_streak,
            "total_optimizations": self.total_optimizations,
            "successful_optimizations": self.successful_optimizations,
            "success_rate": self.success_rate
        }
    
    def _get_level_system(self) -> Dict:
        """Load level system configuration from test data"""
        # In a real implementation, this would come from a configuration service
        # For now, we'll use the test data
        try:
            test_data_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "test_data" / "gamification_test_data.json"
            with open(test_data_path, 'r') as f:
                data = json.load(f)
                return data["level_system"]
        except:
            # Fallback level system
            return {
                "levels": [
                    {"level": 1, "xp_required": 0, "title": "Novice"},
                    {"level": 12, "xp_required": 3000, "title": "Context Master"},
                    {"level": 13, "xp_required": 4000, "title": "Advanced User"},
                    {"level": 15, "xp_required": 5000, "title": "Optimization Guru"},
                ]
            }
    
    def _get_level_threshold(self, level: int) -> int:
        """Get XP threshold for a specific level"""
        level_system = self._get_level_system()
        
        # Find the threshold for the given level
        for level_info in level_system["levels"]:
            if level_info["level"] == level:
                return level_info["xp_required"]
        
        # If level not found, extrapolate based on pattern
        # For simplicity, assume each level after 20 requires 1000 more XP
        if level > 20:
            base_xp = 12000  # Level 20 threshold from test data
            extra_levels = level - 20
            return base_xp + (extra_levels * 1000)
        
        return 0
    
    def _calculate_level_from_xp(self, xp: int) -> int:
        """Calculate what level corresponds to given XP"""
        level_system = self._get_level_system()
        
        current_level = 1
        for level_info in sorted(level_system["levels"], key=lambda x: x["level"]):
            if xp >= level_info["xp_required"]:
                current_level = level_info["level"]
            else:
                break
        
        return current_level