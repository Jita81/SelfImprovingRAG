"""
Real-time Update Service for Live Leaderboard Updates

This service provides real-time notifications and updates for leaderboard changes,
ranking updates, and social interactions with WebSocket support and event streaming.
"""

from typing import Dict, Any, List, Callable, Optional, Set
from datetime import datetime, timedelta
import json
import threading
import time
from enum import Enum
import uuid

try:
    from .leaderboard_service import LeaderboardService
    from ..dtos.leaderboard_requests import GetLeaderboardRequest
except ImportError:
    class LeaderboardService:
        pass


class UpdateType(Enum):
    """Types of real-time updates"""
    RANKING_CHANGE = "ranking_change"
    NEW_LEADER = "new_leader"
    STREAK_UPDATE = "streak_update"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    TEAM_UPDATE = "team_update"
    SOCIAL_UPDATE = "social_update"
    LEADERBOARD_REFRESH = "leaderboard_refresh"


class UpdatePriority(Enum):
    """Priority levels for updates"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class RealtimeUpdate:
    """Represents a real-time update event"""
    
    def __init__(self, update_type: UpdateType, data: Dict[str, Any], 
                 priority: UpdatePriority = UpdatePriority.MEDIUM,
                 target_users: Optional[List[str]] = None):
        self.update_id = str(uuid.uuid4())
        self.update_type = update_type
        self.data = data
        self.priority = priority
        self.target_users = target_users or []  # Empty means broadcast to all
        self.timestamp = datetime.utcnow()
        self.created_at = self.timestamp.isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert update to dictionary for transmission"""
        return {
            "update_id": self.update_id,
            "type": self.update_type.value,
            "priority": self.priority.value,
            "data": self.data,
            "target_users": self.target_users,
            "timestamp": self.created_at
        }


class RealtimeUpdateService:
    """
    Service for managing real-time leaderboard updates and notifications.
    
    Provides WebSocket-like functionality for live updates, event queuing,
    and subscription management.
    """
    
    def __init__(self, leaderboard_service: Optional['LeaderboardService'] = None):
        self.leaderboard_service = leaderboard_service
        
        # Subscriber management
        self.subscribers: Dict[str, Dict[str, Any]] = {}  # connection_id -> subscriber info
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        
        # Update queue and processing
        self.update_queue: List[RealtimeUpdate] = []
        self.update_history: List[RealtimeUpdate] = []
        self.max_history_size = 1000
        
        # Configuration
        self.update_interval = 1.0  # seconds
        self.ranking_change_threshold = 3  # minimum rank change to trigger update
        self.batch_update_size = 10
        
        # State tracking for change detection
        self.last_rankings: Dict[str, Dict[str, Any]] = {}  # period -> {user_id: rank}
        self.last_leaderboard_update = datetime.utcnow()
        
        # Background processing
        self.is_running = False
        self.update_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.stats = {
            "total_updates_sent": 0,
            "total_subscribers": 0,
            "updates_per_minute": 0,
            "last_activity": datetime.utcnow().isoformat()
        }
    
    def start_realtime_service(self):
        """Start the real-time update processing service"""
        if self.is_running:
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._process_updates_loop, daemon=True)
        self.update_thread.start()
        print("🚀 Real-time update service started")
    
    def stop_realtime_service(self):
        """Stop the real-time update processing service"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5.0)
        print("🛑 Real-time update service stopped")
    
    def subscribe_user(self, user_id: str, connection_id: str, 
                      subscription_filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Subscribe a user to real-time updates.
        
        Args:
            user_id: ID of the user
            connection_id: Unique connection identifier (e.g., WebSocket ID)
            subscription_filters: Optional filters for update types
            
        Returns:
            Subscription confirmation with details
        """
        # Default subscription filters
        default_filters = {
            "update_types": [t.value for t in UpdateType],
            "priority_threshold": UpdatePriority.LOW.value,
            "include_global": True,
            "include_personal": True,
            "include_team": True,
            "include_friends": True
        }
        
        filters = {**default_filters, **(subscription_filters or {})}
        
        # Store subscriber info
        self.subscribers[connection_id] = {
            "user_id": user_id,
            "filters": filters,
            "connected_at": datetime.utcnow().isoformat(),
            "last_ping": datetime.utcnow().isoformat(),
            "updates_received": 0
        }
        
        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        self.stats["total_subscribers"] = len(self.subscribers)
        
        # Send welcome message with current state
        welcome_update = RealtimeUpdate(
            update_type=UpdateType.LEADERBOARD_REFRESH,
            data={
                "message": "Connected to real-time updates",
                "user_id": user_id,
                "connection_id": connection_id,
                "filters": filters
            },
            target_users=[user_id]
        )
        
        self._queue_update(welcome_update)
        
        return {
            "success": True,
            "connection_id": connection_id,
            "user_id": user_id,
            "filters": filters,
            "message": "Successfully subscribed to real-time updates"
        }
    
    def unsubscribe_user(self, connection_id: str) -> Dict[str, Any]:
        """
        Unsubscribe a user from real-time updates.
        
        Args:
            connection_id: Connection identifier to remove
            
        Returns:
            Unsubscription confirmation
        """
        if connection_id not in self.subscribers:
            return {"success": False, "error": "Connection not found"}
        
        subscriber = self.subscribers[connection_id]
        user_id = subscriber["user_id"]
        
        # Remove from subscribers
        del self.subscribers[connection_id]
        
        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:  # No more connections
                del self.user_connections[user_id]
        
        self.stats["total_subscribers"] = len(self.subscribers)
        
        return {
            "success": True,
            "connection_id": connection_id,
            "user_id": user_id,
            "message": "Successfully unsubscribed from real-time updates"
        }
    
    def trigger_ranking_update(self, user_id: str, old_rank: int, new_rank: int, 
                              period: str = "all_time") -> None:
        """
        Trigger a ranking change update.
        
        Args:
            user_id: User whose rank changed
            old_rank: Previous rank
            new_rank: New rank
            period: Leaderboard period
        """
        rank_change = old_rank - new_rank
        
        # Only trigger if change is significant
        if abs(rank_change) >= self.ranking_change_threshold:
            update = RealtimeUpdate(
                update_type=UpdateType.RANKING_CHANGE,
                data={
                    "user_id": user_id,
                    "old_rank": old_rank,
                    "new_rank": new_rank,
                    "rank_change": rank_change,
                    "period": period,
                    "direction": "up" if rank_change > 0 else "down"
                },
                priority=UpdatePriority.HIGH if abs(rank_change) >= 10 else UpdatePriority.MEDIUM,
                target_users=[user_id]  # Personal update
            )
            
            self._queue_update(update)
            
            # Also send to friends/teammates if significant change
            if abs(rank_change) >= 5:
                self._trigger_social_updates(user_id, "ranking_change", update.data)
    
    def trigger_new_leader(self, user_id: str, period: str = "all_time") -> None:
        """
        Trigger a new leader update.
        
        Args:
            user_id: New leader user ID
            period: Leaderboard period
        """
        update = RealtimeUpdate(
            update_type=UpdateType.NEW_LEADER,
            data={
                "new_leader_user_id": user_id,
                "period": period,
                "message": f"New leader in {period} leaderboard!"
            },
            priority=UpdatePriority.CRITICAL
            # No target_users means broadcast to everyone
        )
        
        self._queue_update(update)
    
    def trigger_streak_update(self, user_id: str, new_streak: int, milestone: bool = False) -> None:
        """
        Trigger a streak update.
        
        Args:
            user_id: User with streak update
            new_streak: New streak value
            milestone: Whether this is a milestone streak
        """
        priority = UpdatePriority.HIGH if milestone else UpdatePriority.MEDIUM
        
        update = RealtimeUpdate(
            update_type=UpdateType.STREAK_UPDATE,
            data={
                "user_id": user_id,
                "new_streak": new_streak,
                "milestone": milestone,
                "message": f"{'Milestone: ' if milestone else ''}{new_streak} consecutive successes!"
            },
            priority=priority,
            target_users=[user_id]
        )
        
        self._queue_update(update)
        
        # Share milestone streaks with social network
        if milestone:
            self._trigger_social_updates(user_id, "streak_milestone", update.data)
    
    def trigger_achievement_update(self, user_id: str, achievement_data: Dict[str, Any]) -> None:
        """
        Trigger an achievement unlock update.
        
        Args:
            user_id: User who unlocked achievement
            achievement_data: Achievement details
        """
        update = RealtimeUpdate(
            update_type=UpdateType.ACHIEVEMENT_UNLOCK,
            data={
                "user_id": user_id,
                "achievement": achievement_data,
                "message": f"Achievement unlocked: {achievement_data.get('name', 'Unknown')}"
            },
            priority=UpdatePriority.HIGH,
            target_users=[user_id]
        )
        
        self._queue_update(update)
        
        # Share rare achievements with social network
        if achievement_data.get("rarity") in ["Platinum", "Diamond"]:
            self._trigger_social_updates(user_id, "rare_achievement", update.data)
    
    def trigger_leaderboard_refresh(self, period: str = "all_time") -> None:
        """
        Trigger a full leaderboard refresh.
        
        Args:
            period: Leaderboard period to refresh
        """
        update = RealtimeUpdate(
            update_type=UpdateType.LEADERBOARD_REFRESH,
            data={
                "period": period,
                "message": f"Leaderboard refreshed: {period}",
                "refresh_timestamp": datetime.utcnow().isoformat()
            },
            priority=UpdatePriority.LOW
            # Broadcast to all users
        )
        
        self._queue_update(update)
    
    def get_live_leaderboard(self, period: str = "all_time", limit: int = 10) -> Dict[str, Any]:
        """
        Get current leaderboard with real-time update metadata.
        
        Args:
            period: Leaderboard period
            limit: Number of entries to return
            
        Returns:
            Leaderboard data with update metadata
        """
        if not self.leaderboard_service:
            return {"error": "Leaderboard service not available"}
        
        # Get current leaderboard
        request = GetLeaderboardRequest(period=period, limit=limit)
        response = self.leaderboard_service.get_leaderboard(request)
        
        if not response.success:
            return {"error": response.error}
        
        # Add real-time metadata
        live_data = {
            "leaderboard": response.leaderboard_entries,
            "metadata": {
                "period": period,
                "total_participants": response.total_participants,
                "last_update": self.last_leaderboard_update.isoformat(),
                "realtime_subscribers": len(self.subscribers),
                "updates_pending": len(self.update_queue)
            },
            "realtime_info": {
                "update_interval": self.update_interval,
                "service_status": "running" if self.is_running else "stopped",
                "stats": self.stats
            }
        }
        
        return live_data
    
    def get_user_update_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent updates for a specific user.
        
        Args:
            user_id: User ID to get updates for
            limit: Maximum number of updates to return
            
        Returns:
            List of recent updates for the user
        """
        user_updates = []
        
        for update in reversed(self.update_history):
            # Include if it's targeted to this user or is a broadcast
            if not update.target_users or user_id in update.target_users:
                user_updates.append(update.to_dict())
                
                if len(user_updates) >= limit:
                    break
        
        return user_updates
    
    def _queue_update(self, update: RealtimeUpdate) -> None:
        """Add update to processing queue"""
        self.update_queue.append(update)
        
        # Maintain history
        self.update_history.append(update)
        if len(self.update_history) > self.max_history_size:
            self.update_history = self.update_history[-self.max_history_size:]
    
    def _process_updates_loop(self) -> None:
        """Main update processing loop (runs in background thread)"""
        while self.is_running:
            try:
                self._process_pending_updates()
                self._update_stats()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in update processing loop: {e}")
                time.sleep(self.update_interval)
    
    def _process_pending_updates(self) -> None:
        """Process all pending updates in the queue"""
        if not self.update_queue:
            return
        
        # Process updates in batches
        batch = self.update_queue[:self.batch_update_size]
        self.update_queue = self.update_queue[self.batch_update_size:]
        
        for update in batch:
            self._send_update_to_subscribers(update)
            self.stats["total_updates_sent"] += 1
    
    def _send_update_to_subscribers(self, update: RealtimeUpdate) -> None:
        """
        Send update to relevant subscribers.
        
        Args:
            update: Update to send
        """
        sent_count = 0
        
        for connection_id, subscriber in self.subscribers.items():
            if self._should_send_update(update, subscriber):
                # In a real implementation, this would send via WebSocket
                self._simulate_update_delivery(connection_id, update)
                subscriber["updates_received"] += 1
                sent_count += 1
        
        # Update stats
        if sent_count > 0:
            self.stats["last_activity"] = datetime.utcnow().isoformat()
    
    def _should_send_update(self, update: RealtimeUpdate, subscriber: Dict[str, Any]) -> bool:
        """
        Determine if update should be sent to a subscriber.
        
        Args:
            update: Update to check
            subscriber: Subscriber info
            
        Returns:
            True if update should be sent
        """
        filters = subscriber["filters"]
        user_id = subscriber["user_id"]
        
        # Check priority threshold
        if update.priority.value < filters["priority_threshold"]:
            return False
        
        # Check update type filter
        if update.update_type.value not in filters["update_types"]:
            return False
        
        # Check targeting
        if update.target_users:
            # Targeted update
            if user_id not in update.target_users:
                return False
        else:
            # Broadcast update - check global filter
            if not filters["include_global"]:
                return False
        
        return True
    
    def _simulate_update_delivery(self, connection_id: str, update: RealtimeUpdate) -> None:
        """
        Simulate sending update to subscriber.
        
        In a real implementation, this would send via WebSocket or similar.
        """
        # For testing/simulation purposes, we'll just store the update
        # In production, this would be: websocket.send(json.dumps(update.to_dict()))
        pass
    
    def _trigger_social_updates(self, user_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Trigger updates for user's social connections.
        
        Args:
            user_id: User who triggered the event
            event_type: Type of social event
            event_data: Event details
        """
        # In a real implementation, this would look up user's friends/teammates
        # For now, we'll create a generic social update
        social_update = RealtimeUpdate(
            update_type=UpdateType.SOCIAL_UPDATE,
            data={
                "source_user_id": user_id,
                "event_type": event_type,
                "event_data": event_data,
                "message": f"Friend activity: {event_type}"
            },
            priority=UpdatePriority.LOW
            # In production, target_users would be user's social connections
        )
        
        self._queue_update(social_update)
    
    def _update_stats(self) -> None:
        """Update service statistics"""
        now = datetime.utcnow()
        
        # Calculate updates per minute
        minute_ago = now - timedelta(minutes=1)
        recent_updates = [
            update for update in self.update_history
            if update.timestamp >= minute_ago
        ]
        self.stats["updates_per_minute"] = len(recent_updates)
        
        # Clean up old connections (heartbeat simulation)
        expired_connections = []
        for connection_id, subscriber in self.subscribers.items():
            last_ping = datetime.fromisoformat(subscriber["last_ping"])
            if now - last_ping > timedelta(minutes=5):  # 5 minute timeout
                expired_connections.append(connection_id)
        
        for connection_id in expired_connections:
            self.unsubscribe_user(connection_id)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and statistics"""
        return {
            "service_running": self.is_running,
            "subscribers": len(self.subscribers),
            "update_queue_size": len(self.update_queue),
            "update_history_size": len(self.update_history),
            "stats": self.stats,
            "configuration": {
                "update_interval": self.update_interval,
                "ranking_change_threshold": self.ranking_change_threshold,
                "batch_update_size": self.batch_update_size,
                "max_history_size": self.max_history_size
            }
        }