from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class AchievementTrigger:
    """
    Value object representing conditions that trigger achievement unlocks.
    Immutable to ensure trigger conditions cannot be modified.
    """
    trigger_type: str
    threshold: float
    minimum_attempts: Optional[int] = None
    count: Optional[int] = None
    quality_threshold: Optional[float] = None
    
    def __post_init__(self):
        """Validate trigger configuration"""
        if not self.trigger_type:
            raise ValueError("Trigger type cannot be empty")
        
        if self.threshold < 0:
            raise ValueError("Threshold cannot be negative")
        
        if self.minimum_attempts is not None and self.minimum_attempts < 0:
            raise ValueError("Minimum attempts cannot be negative")
        
        if self.count is not None and self.count < 0:
            raise ValueError("Count cannot be negative")
    
    def check_trigger(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if event data satisfies this trigger's conditions.
        
        Args:
            event_data: Dictionary containing event-specific data
            
        Returns:
            True if trigger conditions are met, False otherwise
        """
        try:
            if self.trigger_type == "optimization_count":
                optimization_count = event_data.get("optimization_count", 0)
                return optimization_count >= self.threshold
            
            elif self.trigger_type == "success_rate":
                success_rate = event_data.get("success_rate", 0.0)
                total_optimizations = event_data.get("total_optimizations", 0)
                
                # Check both success rate and minimum attempts
                meets_rate = success_rate >= self.threshold
                meets_attempts = (self.minimum_attempts is None or 
                                total_optimizations >= self.minimum_attempts)
                
                return meets_rate and meets_attempts
            
            elif self.trigger_type == "speed_optimization":
                # Check if user has completed required number of optimizations under threshold time
                speed_records = event_data.get("speed_records", [])
                if not speed_records:
                    return False
                
                fast_optimizations = [
                    record for record in speed_records 
                    if record.get("duration_seconds", float('inf')) <= self.threshold
                ]
                
                required_count = self.count or 1
                return len(fast_optimizations) >= required_count
            
            elif self.trigger_type == "betting_streak":
                current_streak = event_data.get("streak", 0)
                return current_streak >= self.threshold
            
            elif self.trigger_type == "teammate_help":
                teammates_helped = event_data.get("teammates_helped", 0)
                return teammates_helped >= self.threshold
            
            elif self.trigger_type == "bug_reports":
                bug_reports = event_data.get("bug_reports", 0)
                quality_score = event_data.get("average_quality_score", 0.0)
                
                meets_count = bug_reports >= self.threshold
                meets_quality = (self.quality_threshold is None or 
                               quality_score >= self.quality_threshold)
                
                return meets_count and meets_quality
            
            elif self.trigger_type == "daily_streak":
                streak_days = event_data.get("streak_days", 0)
                return streak_days >= self.threshold
            
            elif self.trigger_type == "first_optimization":
                # Special trigger for first-time events
                is_first = event_data.get("is_first_optimization", False)
                optimization_count = event_data.get("optimization_count", 0)
                return is_first or optimization_count == 1
            
            else:
                # Unknown trigger type - be conservative and don't unlock
                return False
                
        except (KeyError, TypeError, ValueError):
            # If event data is malformed or missing, don't unlock achievement
            return False
    
    def calculate_progress(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate progress toward this achievement trigger.
        
        Args:
            event_data: Dictionary containing event-specific data
            
        Returns:
            Dictionary with current_progress, required_progress, and progress_percentage
        """
        try:
            if self.trigger_type == "optimization_count":
                current = event_data.get("optimization_count", 0)
                required = int(self.threshold)
                
            elif self.trigger_type == "success_rate":
                current_rate = event_data.get("success_rate", 0.0)
                current_attempts = event_data.get("total_optimizations", 0)
                
                # For success rate, progress is based on both rate and attempts
                rate_progress = min(current_rate / self.threshold, 1.0) * 50  # 50% weight
                attempts_progress = 0
                if self.minimum_attempts:
                    attempts_progress = min(current_attempts / self.minimum_attempts, 1.0) * 50  # 50% weight
                
                current = rate_progress + attempts_progress
                required = 100
                
            elif self.trigger_type == "betting_streak":
                current = event_data.get("streak", 0)
                required = int(self.threshold)
                
            elif self.trigger_type == "teammate_help":
                current = event_data.get("teammates_helped", 0)
                required = int(self.threshold)
                
            elif self.trigger_type == "daily_streak":
                current = event_data.get("streak_days", 0)
                required = int(self.threshold)
                
            else:
                # For unknown or complex triggers, return minimal progress info
                return {
                    "current_progress": 0,
                    "required_progress": 1,
                    "progress_percentage": 0
                }
            
            progress_percentage = min((current / required) * 100, 100) if required > 0 else 0
            
            return {
                "current_progress": current,
                "required_progress": required,
                "progress_percentage": int(progress_percentage)
            }
            
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return {
                "current_progress": 0,
                "required_progress": 1,
                "progress_percentage": 0
            }
    
    @property
    def description(self) -> str:
        """Get human-readable description of this trigger"""
        if self.trigger_type == "optimization_count":
            return f"Complete {int(self.threshold)} optimization(s)"
        elif self.trigger_type == "success_rate":
            attempts_text = f" over {self.minimum_attempts} attempts" if self.minimum_attempts else ""
            return f"Achieve {self.threshold*100:.0f}% success rate{attempts_text}"
        elif self.trigger_type == "speed_optimization":
            count_text = f" {self.count}" if self.count else ""
            return f"Complete{count_text} optimization(s) in under {self.threshold} seconds"
        elif self.trigger_type == "betting_streak":
            return f"Win {int(self.threshold)} token bets in a row"
        elif self.trigger_type == "teammate_help":
            return f"Help {int(self.threshold)} teammate(s) improve their success rate"
        elif self.trigger_type == "daily_streak":
            return f"Maintain a {int(self.threshold)}-day optimization streak"
        else:
            return f"Meet {self.trigger_type} threshold of {self.threshold}"