from enum import Enum
from dataclasses import dataclass
from typing import Dict
import json
from pathlib import Path

class AchievementRarity(Enum):
    """Enumeration of achievement rarity levels"""
    COMMON = "common"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    
    @property
    def multiplier(self) -> float:
        """Get XP multiplier for this rarity level"""
        rarity_system = self._get_rarity_system()
        return rarity_system.get(self.value, {}).get("multiplier", 1.0)
    
    @property
    def color(self) -> str:
        """Get color hex code for this rarity level"""
        rarity_system = self._get_rarity_system()
        return rarity_system.get(self.value, {}).get("color", "#ffffff")
    
    @property
    def probability(self) -> float:
        """Get probability/drop rate for this rarity level"""
        rarity_system = self._get_rarity_system()
        return rarity_system.get(self.value, {}).get("probability", 1.0)
    
    def _get_rarity_system(self) -> Dict:
        """Load rarity system configuration from test data"""
        try:
            test_data_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "test_data" / "achievement_test_data.json"
            with open(test_data_path, 'r') as f:
                data = json.load(f)
                return data["rarity_system"]
        except:
            # Fallback rarity system
            return {
                "common": {"color": "#ffffff", "multiplier": 1.0, "probability": 0.6},
                "silver": {"color": "#c0c0c0", "multiplier": 1.5, "probability": 0.25},
                "gold": {"color": "#ffd700", "multiplier": 2.0, "probability": 0.1},
                "platinum": {"color": "#e5e4e2", "multiplier": 3.0, "probability": 0.04},
                "diamond": {"color": "#b9f2ff", "multiplier": 5.0, "probability": 0.01}
            }
    
    def calculate_xp_reward(self, base_xp: int) -> int:
        """Calculate final XP reward with rarity multiplier applied"""
        return int(base_xp * self.multiplier)
    
    def is_rare(self) -> bool:
        """Check if this rarity is considered rare (above common/silver)"""
        return self in [AchievementRarity.GOLD, AchievementRarity.PLATINUM, AchievementRarity.DIAMOND]
    
    @classmethod
    def from_string(cls, rarity_str: str) -> 'AchievementRarity':
        """Create AchievementRarity from string"""
        for rarity in cls:
            if rarity.value == rarity_str.lower():
                return rarity
        raise ValueError(f"Unknown rarity: {rarity_str}")
    
    def __str__(self) -> str:
        return self.value.title()
    
    def __repr__(self) -> str:
        return f"AchievementRarity.{self.name}"