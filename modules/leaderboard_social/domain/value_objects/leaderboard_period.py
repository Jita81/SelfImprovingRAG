"""
LeaderboardPeriod value object for time-based leaderboard filtering

This value object represents different time periods for leaderboard calculations
and provides utilities for date range handling.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple
from enum import Enum


class PeriodType(Enum):
    """Enumeration of supported leaderboard periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


@dataclass(frozen=True)
class LeaderboardPeriod:
    """
    Value object representing a leaderboard time period.
    
    Provides date range calculation and validation for different leaderboard periods.
    """
    period_type: PeriodType
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def __post_init__(self):
        """Validate the period configuration"""
        if self.period_type not in PeriodType:
            raise ValueError(f"Invalid period type: {self.period_type}")
    
    def get_date_range(self, reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
        """
        Calculate the actual date range for this period.
        
        Args:
            reference_date: The reference date for period calculation (defaults to now)
            
        Returns:
            Tuple of (start_date, end_date) as datetime objects
        """
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        if self.start_date and self.end_date:
            # Use explicit dates if provided
            start = datetime.fromisoformat(self.start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
            return start, end
        
        # Calculate based on period type
        if self.period_type == PeriodType.DAILY:
            start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1) - timedelta(microseconds=1)
        elif self.period_type == PeriodType.WEEKLY:
            # Start from Monday of current week
            days_since_monday = reference_date.weekday()
            start = (reference_date - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(days=7) - timedelta(microseconds=1)
        elif self.period_type == PeriodType.MONTHLY:
            # Start from first day of current month
            start = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Calculate last day of month
            if start.month == 12:
                next_month = start.replace(year=start.year + 1, month=1)
            else:
                next_month = start.replace(month=start.month + 1)
            end = next_month - timedelta(microseconds=1)
        else:  # ALL_TIME
            # Use very wide date range for all-time
            start = datetime(2000, 1, 1)
            end = datetime(2099, 12, 31, 23, 59, 59)
        
        return start, end
    
    def is_date_in_period(self, check_date: datetime, reference_date: Optional[datetime] = None) -> bool:
        """
        Check if a given date falls within this period.
        
        Args:
            check_date: The date to check
            reference_date: The reference date for period calculation
            
        Returns:
            True if the date is within the period
        """
        start, end = self.get_date_range(reference_date)
        return start <= check_date <= end
    
    def get_period_label(self) -> str:
        """
        Get a human-readable label for this period.
        
        Returns:
            String label for the period
        """
        labels = {
            PeriodType.DAILY: "Today",
            PeriodType.WEEKLY: "This Week",
            PeriodType.MONTHLY: "This Month",
            PeriodType.ALL_TIME: "All Time"
        }
        return labels.get(self.period_type, str(self.period_type.value))
    
    @classmethod
    def create_daily(cls, date: Optional[str] = None) -> 'LeaderboardPeriod':
        """Create a daily period"""
        if date:
            start = date
            # Calculate end of day
            dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
            end_dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            end = end_dt.isoformat().replace('+00:00', 'Z')
            return cls(PeriodType.DAILY, start, end)
        return cls(PeriodType.DAILY)
    
    @classmethod
    def create_weekly(cls, start_date: Optional[str] = None, end_date: Optional[str] = None) -> 'LeaderboardPeriod':
        """Create a weekly period"""
        return cls(PeriodType.WEEKLY, start_date, end_date)
    
    @classmethod
    def create_monthly(cls, start_date: Optional[str] = None, end_date: Optional[str] = None) -> 'LeaderboardPeriod':
        """Create a monthly period"""
        return cls(PeriodType.MONTHLY, start_date, end_date)
    
    @classmethod
    def create_all_time(cls) -> 'LeaderboardPeriod':
        """Create an all-time period"""
        return cls(PeriodType.ALL_TIME)