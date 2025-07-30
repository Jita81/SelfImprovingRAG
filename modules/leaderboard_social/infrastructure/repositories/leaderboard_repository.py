"""
Leaderboard Repository for data persistence

Abstract repository interface and in-memory implementation for
leaderboard entries and historical snapshots.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

try:
    from ...domain.entities.leaderboard_entry import LeaderboardEntry
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from domain.entities.leaderboard_entry import LeaderboardEntry


class LeaderboardRepository(ABC):
    """Abstract repository interface for leaderboard data"""
    
    @abstractmethod
    def save_entry(self, entry: LeaderboardEntry) -> LeaderboardEntry:
        """Save a leaderboard entry"""
        pass
    
    @abstractmethod
    def find_entries_by_period(self, period: str, limit: int = 10, offset: int = 0) -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific period"""
        pass
    
    @abstractmethod
    def find_entry_by_user_id(self, user_id: str, period: str = "all_time") -> Optional[LeaderboardEntry]:
        """Find leaderboard entry for a specific user"""
        pass
    
    @abstractmethod
    def find_entries_by_team(self, team_name: str, period: str = "all_time") -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific team"""
        pass
    
    @abstractmethod
    def find_entries_by_category(self, category: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific category"""
        pass
    
    @abstractmethod
    def save_historical_snapshot(self, snapshot_id: str, period: str, snapshot_date: str, entries: List[LeaderboardEntry]) -> None:
        """Save a historical leaderboard snapshot"""
        pass
    
    @abstractmethod
    def get_historical_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a historical snapshot"""
        pass


class InMemoryLeaderboardRepository(LeaderboardRepository):
    """In-memory implementation of leaderboard repository for testing"""
    
    def __init__(self):
        self._entries: Dict[str, LeaderboardEntry] = {}
        self._historical_snapshots: Dict[str, Dict[str, Any]] = {}
        self._load_test_data()
    
    def _load_test_data(self) -> None:
        """Load test data from JSON file"""
        try:
            test_data_path = os.path.join(os.path.dirname(__file__), '../../../../tests/test_data/leaderboard_test_data.json')
            
            if os.path.exists(test_data_path):
                with open(test_data_path, 'r') as f:
                    data = json.load(f)
                
                # Load users as leaderboard entries
                for user_data in data.get('users', []):
                    entry = self._create_entry_from_user_data(user_data)
                    self._entries[f"{user_data['user_id']}_all_time"] = entry
                
                # Load historical snapshots
                for snapshot in data.get('historical_snapshots', []):
                    snapshot_id = f"snapshot_{snapshot['snapshot_date']}_{snapshot['period']}"
                    self._historical_snapshots[snapshot_id] = snapshot
                    
        except Exception as e:
            print(f"Warning: Could not load test data: {e}")
    
    def _create_entry_from_user_data(self, user_data: Dict[str, Any]) -> LeaderboardEntry:
        """Create LeaderboardEntry from user test data"""
        return LeaderboardEntry(
            user_id=user_data['user_id'],
            rank=1,  # Will be calculated based on actual ranking
            user_name=user_data['name'],
            success_rate=user_data['success_rate'],
            total_optimizations=user_data['total_optimizations'],
            successful_optimizations=user_data['successful_optimizations'],
            current_streak=user_data['current_streak'],
            best_streak=user_data['best_streak'],
            level=user_data['level'],
            total_xp=user_data['total_xp'],
            achievements=user_data.get('achievements', []),
            badges=user_data.get('badges', []),
            is_visible=user_data['privacy_settings']['show_in_leaderboard'],
            show_stats=user_data['privacy_settings']['show_stats_to_others']
        )
    
    def save_entry(self, entry: LeaderboardEntry) -> LeaderboardEntry:
        """Save a leaderboard entry"""
        key = f"{entry.user_id}_all_time"
        self._entries[key] = entry
        return entry
    
    def find_entries_by_period(self, period: str, limit: int = 10, offset: int = 0) -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific period"""
        # Filter entries by period and visibility
        entries = []
        
        for key, entry in self._entries.items():
            if entry.is_visible:
                entries.append(entry)
        
        # Sort by composite score or success rate (for now, using success rate)
        entries.sort(key=lambda x: (x.success_rate, x.total_optimizations, x.current_streak), reverse=True)
        
        # Assign ranks
        for i, entry in enumerate(entries):
            entry.rank = i + 1
        
        # Apply pagination
        return entries[offset:offset + limit]
    
    def find_entry_by_user_id(self, user_id: str, period: str = "all_time") -> Optional[LeaderboardEntry]:
        """Find leaderboard entry for a specific user"""
        key = f"{user_id}_{period}"
        return self._entries.get(key)
    
    def find_entries_by_team(self, team_name: str, period: str = "all_time") -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific team"""
        entries = []
        
        for entry in self._entries.values():
            if entry.team_name == team_name and entry.is_visible:
                entries.append(entry)
        
        # Sort by performance
        entries.sort(key=lambda x: (x.success_rate, x.total_optimizations), reverse=True)
        
        # Assign ranks within team
        for i, entry in enumerate(entries):
            entry.rank = i + 1
        
        return entries
    
    def find_entries_by_category(self, category: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific category"""
        # For now, return top entries (in a real implementation, would filter by category)
        entries = list(self._entries.values())
        entries = [e for e in entries if e.is_visible]
        
        # Sort by success rate for this category
        entries.sort(key=lambda x: x.success_rate, reverse=True)
        
        # Set category-specific data
        for i, entry in enumerate(entries[:limit]):
            entry.rank = i + 1
            entry.category_score = entry.success_rate  # Simplified for now
            entry.category_rank = i + 1
        
        return entries[:limit]
    
    def save_historical_snapshot(self, snapshot_id: str, period: str, snapshot_date: str, entries: List[LeaderboardEntry]) -> None:
        """Save a historical leaderboard snapshot"""
        snapshot_data = {
            "snapshot_id": snapshot_id,
            "period": period,
            "snapshot_date": snapshot_date,
            "entries": [entry.to_dict() for entry in entries],
            "created_at": datetime.utcnow().isoformat()
        }
        self._historical_snapshots[snapshot_id] = snapshot_data
    
    def get_historical_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a historical snapshot"""
        return self._historical_snapshots.get(snapshot_id)


class FileLeaderboardRepository(LeaderboardRepository):
    """File-based implementation of leaderboard repository"""
    
    def __init__(self, data_file: str = "leaderboard_data.json"):
        self.data_file = data_file
        self._entries: Dict[str, LeaderboardEntry] = {}
        self._historical_snapshots: Dict[str, Dict[str, Any]] = {}
        self._load_from_file()
    
    def _load_from_file(self) -> None:
        """Load data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load entries
                for entry_data in data.get('entries', []):
                    entry = LeaderboardEntry.from_dict(entry_data)
                    key = f"{entry.user_id}_all_time"
                    self._entries[key] = entry
                
                # Load snapshots
                self._historical_snapshots = data.get('snapshots', {})
        except Exception as e:
            print(f"Warning: Could not load leaderboard data from file: {e}")
    
    def _save_to_file(self) -> None:
        """Save data to file"""
        try:
            data = {
                'entries': [entry.to_dict() for entry in self._entries.values()],
                'snapshots': self._historical_snapshots,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save leaderboard data to file: {e}")
    
    def save_entry(self, entry: LeaderboardEntry) -> LeaderboardEntry:
        """Save a leaderboard entry"""
        key = f"{entry.user_id}_all_time"
        self._entries[key] = entry
        self._save_to_file()
        return entry
    
    def find_entries_by_period(self, period: str, limit: int = 10, offset: int = 0) -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific period"""
        entries = [e for e in self._entries.values() if e.is_visible]
        entries.sort(key=lambda x: (x.success_rate, x.total_optimizations), reverse=True)
        
        for i, entry in enumerate(entries):
            entry.rank = i + 1
        
        return entries[offset:offset + limit]
    
    def find_entry_by_user_id(self, user_id: str, period: str = "all_time") -> Optional[LeaderboardEntry]:
        """Find leaderboard entry for a specific user"""
        key = f"{user_id}_{period}"
        return self._entries.get(key)
    
    def find_entries_by_team(self, team_name: str, period: str = "all_time") -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific team"""
        entries = [e for e in self._entries.values() if e.team_name == team_name and e.is_visible]
        entries.sort(key=lambda x: x.success_rate, reverse=True)
        
        for i, entry in enumerate(entries):
            entry.rank = i + 1
        
        return entries
    
    def find_entries_by_category(self, category: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Find leaderboard entries for a specific category"""
        entries = [e for e in self._entries.values() if e.is_visible]
        entries.sort(key=lambda x: x.success_rate, reverse=True)
        
        for i, entry in enumerate(entries[:limit]):
            entry.rank = i + 1
            entry.category_score = entry.success_rate
        
        return entries[:limit]
    
    def save_historical_snapshot(self, snapshot_id: str, period: str, snapshot_date: str, entries: List[LeaderboardEntry]) -> None:
        """Save a historical leaderboard snapshot"""
        snapshot_data = {
            "snapshot_id": snapshot_id,
            "period": period,
            "snapshot_date": snapshot_date,
            "entries": [entry.to_dict() for entry in entries],
            "created_at": datetime.utcnow().isoformat()
        }
        self._historical_snapshots[snapshot_id] = snapshot_data
        self._save_to_file()
    
    def get_historical_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a historical snapshot"""
        return self._historical_snapshots.get(snapshot_id)