"""
Advanced Social Network System for Leaderboard Platform

This module implements sophisticated social networking features including:
- Multi-layered social connections
- Influence scoring and network analysis
- Friend recommendation engines
- Activity feed generation
- Social proof metrics
- Community detection
"""

from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
from collections import defaultdict, deque


class ConnectionType(Enum):
    """Types of social connections"""
    FRIEND = "friend"
    FOLLOWING = "following"
    FOLLOWER = "follower"
    TEAMMATE = "teammate"
    MENTOR = "mentor"
    MENTEE = "mentee"
    COMPETITOR = "competitor"


class ActivityType(Enum):
    """Types of social activities"""
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    RANK_IMPROVEMENT = "rank_improvement"
    STREAK_MILESTONE = "streak_milestone"
    LEVEL_UP = "level_up"
    TEAM_JOIN = "team_join"
    FRIEND_ADD = "friend_add"
    OPTIMIZATION_SUCCESS = "optimization_success"
    CHALLENGE_COMPLETION = "challenge_completion"


class InfluenceMetric(Enum):
    """Metrics for calculating influence"""
    FOLLOWER_COUNT = "follower_count"
    ACHIEVEMENT_RARITY = "achievement_rarity"
    CONSISTENCY_SCORE = "consistency_score"
    MENTORSHIP_IMPACT = "mentorship_impact"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    COMMUNITY_ENGAGEMENT = "community_engagement"


@dataclass
class SocialConnection:
    """Represents a connection between users"""
    from_user_id: str
    to_user_id: str
    connection_type: ConnectionType
    established_date: datetime
    strength: float = 1.0  # Connection strength (0.0 to 1.0)
    last_interaction: Optional[datetime] = None
    mutual: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and initialize connection"""
        self.strength = max(0.0, min(1.0, self.strength))
        if self.last_interaction is None:
            self.last_interaction = self.established_date
    
    @property
    def connection_age_days(self) -> int:
        """Age of connection in days"""
        return (datetime.utcnow() - self.established_date).days
    
    @property
    def interaction_recency_score(self) -> float:
        """Score based on recency of last interaction"""
        if not self.last_interaction:
            return 0.0
        
        days_since = (datetime.utcnow() - self.last_interaction).days
        # Exponential decay with 30-day half-life
        return math.exp(-days_since / 43.2)  # ln(2) * 30 ≈ 43.2
    
    @property
    def effective_strength(self) -> float:
        """Connection strength adjusted for recency and age"""
        recency_factor = self.interaction_recency_score
        age_factor = min(1.0, self.connection_age_days / 30)  # Stronger after 30 days
        return self.strength * recency_factor * (0.5 + 0.5 * age_factor)


@dataclass
class SocialActivity:
    """Represents a social activity in the feed"""
    activity_id: str
    user_id: str
    activity_type: ActivityType
    title: str
    description: str
    timestamp: datetime
    visibility: str = "public"  # public, friends, private
    engagement_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def activity_age_hours(self) -> int:
        """Age of activity in hours"""
        return int((datetime.utcnow() - self.timestamp).total_seconds() / 3600)
    
    @property
    def freshness_score(self) -> float:
        """Score based on activity freshness"""
        hours_old = self.activity_age_hours
        # Decay over 48 hours
        return max(0.1, math.exp(-hours_old / 24))


@dataclass
class InfluenceScore:
    """User's influence score and components"""
    user_id: str
    total_score: float
    component_scores: Dict[InfluenceMetric, float]
    network_reach: int  # Number of users influenced
    engagement_rate: float
    last_calculated: datetime
    
    @property
    def influence_tier(self) -> str:
        """Determine influence tier"""
        if self.total_score >= 90:
            return "Thought Leader"
        elif self.total_score >= 75:
            return "Influencer"
        elif self.total_score >= 60:
            return "Contributor"
        elif self.total_score >= 40:
            return "Participant"
        else:
            return "Observer"


class SocialNetwork:
    """
    Advanced social network management system.
    
    Manages complex social relationships, influence scoring, and recommendation engines.
    """
    
    def __init__(self):
        # Core data structures
        self.connections: Dict[str, List[SocialConnection]] = defaultdict(list)
        self.activities: List[SocialActivity] = []
        self.user_activities: Dict[str, List[str]] = defaultdict(list)  # user_id -> activity_ids
        self.influence_scores: Dict[str, InfluenceScore] = {}
        
        # Network analysis cache
        self._network_cache: Dict[str, Any] = {}
        self._cache_timestamp = datetime.utcnow()
        self.cache_duration = timedelta(hours=1)
        
        # Configuration
        self.max_feed_size = 100
        self.max_connections_per_type = 1000
        self.influence_decay_factor = 0.95
    
    def add_connection(self, 
                      from_user_id: str, 
                      to_user_id: str,
                      connection_type: ConnectionType,
                      bidirectional: bool = False) -> bool:
        """
        Add a social connection between users.
        
        Args:
            from_user_id: Source user
            to_user_id: Target user
            connection_type: Type of connection
            bidirectional: Whether to create mutual connection
            
        Returns:
            True if connection was added successfully
        """
        if from_user_id == to_user_id:
            return False
        
        # Check if connection already exists
        existing = self.get_connection(from_user_id, to_user_id, connection_type)
        if existing:
            return False
        
        # Check connection limits
        user_connections = [c for c in self.connections[from_user_id] 
                          if c.connection_type == connection_type]
        if len(user_connections) >= self.max_connections_per_type:
            return False
        
        # Create connection
        connection = SocialConnection(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            connection_type=connection_type,
            established_date=datetime.utcnow(),
            mutual=bidirectional
        )
        
        self.connections[from_user_id].append(connection)
        
        # Create reverse connection if bidirectional
        if bidirectional:
            reverse_connection = SocialConnection(
                from_user_id=to_user_id,
                to_user_id=from_user_id,
                connection_type=connection_type,
                established_date=datetime.utcnow(),
                mutual=True
            )
            self.connections[to_user_id].append(reverse_connection)
        
        # Clear cache
        self._clear_network_cache()
        
        # Create activity for friend connections
        if connection_type == ConnectionType.FRIEND:
            self.add_activity(SocialActivity(
                activity_id=f"friend_add_{from_user_id}_{to_user_id}_{datetime.utcnow().timestamp()}",
                user_id=from_user_id,
                activity_type=ActivityType.FRIEND_ADD,
                title="New Friend Connection",
                description=f"Connected with {to_user_id}",
                timestamp=datetime.utcnow(),
                metadata={"friend_user_id": to_user_id}
            ))
        
        return True
    
    def remove_connection(self, 
                         from_user_id: str, 
                         to_user_id: str,
                         connection_type: ConnectionType,
                         bidirectional: bool = False) -> bool:
        """Remove a social connection"""
        # Remove primary connection
        user_connections = self.connections[from_user_id]
        initial_count = len(user_connections)
        
        self.connections[from_user_id] = [
            c for c in user_connections 
            if not (c.to_user_id == to_user_id and c.connection_type == connection_type)
        ]
        
        removed = len(self.connections[from_user_id]) < initial_count
        
        # Remove reverse connection if bidirectional
        if bidirectional and removed:
            target_connections = self.connections[to_user_id]
            self.connections[to_user_id] = [
                c for c in target_connections
                if not (c.to_user_id == from_user_id and c.connection_type == connection_type)
            ]
        
        if removed:
            self._clear_network_cache()
        
        return removed
    
    def get_connection(self, 
                      from_user_id: str, 
                      to_user_id: str,
                      connection_type: ConnectionType) -> Optional[SocialConnection]:
        """Get specific connection between users"""
        for connection in self.connections[from_user_id]:
            if (connection.to_user_id == to_user_id and 
                connection.connection_type == connection_type):
                return connection
        return None
    
    def get_user_connections(self, 
                           user_id: str,
                           connection_type: Optional[ConnectionType] = None,
                           include_strength: bool = False) -> List[SocialConnection]:
        """Get all connections for a user"""
        connections = self.connections[user_id]
        
        if connection_type:
            connections = [c for c in connections if c.connection_type == connection_type]
        
        if include_strength:
            # Sort by effective strength
            connections.sort(key=lambda c: c.effective_strength, reverse=True)
        
        return connections
    
    def get_mutual_connections(self, user1_id: str, user2_id: str) -> List[str]:
        """Find mutual connections between two users"""
        user1_friends = {c.to_user_id for c in self.get_user_connections(user1_id, ConnectionType.FRIEND)}
        user2_friends = {c.to_user_id for c in self.get_user_connections(user2_id, ConnectionType.FRIEND)}
        
        return list(user1_friends.intersection(user2_friends))
    
    def calculate_network_distance(self, user1_id: str, user2_id: str, max_depth: int = 6) -> Optional[int]:
        """
        Calculate shortest path between users (degrees of separation).
        
        Args:
            user1_id: First user
            user2_id: Second user
            max_depth: Maximum search depth
            
        Returns:
            Distance in degrees, or None if not connected
        """
        if user1_id == user2_id:
            return 0
        
        # BFS to find shortest path
        queue = deque([(user1_id, 0)])
        visited = {user1_id}
        
        while queue:
            current_user, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
            
            # Get all friends of current user
            friends = [c.to_user_id for c in self.get_user_connections(current_user, ConnectionType.FRIEND)]
            
            for friend_id in friends:
                if friend_id == user2_id:
                    return depth + 1
                
                if friend_id not in visited:
                    visited.add(friend_id)
                    queue.append((friend_id, depth + 1))
        
        return None  # Not connected within max_depth
    
    def calculate_influence_score(self, user_id: str, user_metrics: Dict[str, Any]) -> InfluenceScore:
        """
        Calculate comprehensive influence score for a user.
        
        Args:
            user_id: User to calculate influence for
            user_metrics: User's performance and achievement metrics
            
        Returns:
            Calculated influence score
        """
        component_scores = {}
        
        # Follower count influence
        followers = [c for c in self.connections.values() 
                    for conn_list in [c] for c in conn_list
                    if c.to_user_id == user_id and c.connection_type == ConnectionType.FOLLOWING]
        follower_count = len(followers)
        component_scores[InfluenceMetric.FOLLOWER_COUNT] = min(20, math.log(follower_count + 1) * 5)
        
        # Achievement rarity influence
        achievement_score = user_metrics.get('rare_achievements_count', 0) * 2
        component_scores[InfluenceMetric.ACHIEVEMENT_RARITY] = min(20, achievement_score)
        
        # Consistency influence
        consistency = user_metrics.get('consistency_score', 0.5)
        component_scores[InfluenceMetric.CONSISTENCY_SCORE] = consistency * 15
        
        # Mentorship impact
        mentees = [c for c in self.get_user_connections(user_id, ConnectionType.MENTEE)]
        mentorship_impact = len(mentees) * 3
        component_scores[InfluenceMetric.MENTORSHIP_IMPACT] = min(15, mentorship_impact)
        
        # Knowledge sharing (based on activities)
        user_activity_count = len(self.user_activities[user_id])
        knowledge_sharing = min(15, math.log(user_activity_count + 1) * 3)
        component_scores[InfluenceMetric.KNOWLEDGE_SHARING] = knowledge_sharing
        
        # Community engagement
        network_reach = self.calculate_network_reach(user_id)
        engagement_rate = self.calculate_engagement_rate(user_id)
        community_engagement = (network_reach / 10) + (engagement_rate * 10)
        component_scores[InfluenceMetric.COMMUNITY_ENGAGEMENT] = min(15, community_engagement)
        
        # Calculate total score
        total_score = sum(component_scores.values())
        
        influence_score = InfluenceScore(
            user_id=user_id,
            total_score=total_score,
            component_scores=component_scores,
            network_reach=network_reach,
            engagement_rate=engagement_rate,
            last_calculated=datetime.utcnow()
        )
        
        self.influence_scores[user_id] = influence_score
        return influence_score
    
    def calculate_network_reach(self, user_id: str) -> int:
        """Calculate how many users this user can reach through their network"""
        cache_key = f"reach_{user_id}"
        if self._is_cache_valid() and cache_key in self._network_cache:
            return self._network_cache[cache_key]
        
        # Use BFS to find all reachable users within 3 degrees
        reachable = set()
        queue = deque([(user_id, 0)])
        visited = {user_id}
        
        while queue:
            current_user, depth = queue.popleft()
            
            if depth >= 3:  # Limit to 3 degrees
                continue
            
            connections = self.get_user_connections(current_user)
            for connection in connections:
                target_id = connection.to_user_id
                if target_id not in visited:
                    visited.add(target_id)
                    reachable.add(target_id)
                    queue.append((target_id, depth + 1))
        
        reach = len(reachable)
        self._network_cache[cache_key] = reach
        return reach
    
    def calculate_engagement_rate(self, user_id: str) -> float:
        """Calculate user's engagement rate based on activities"""
        user_activity_ids = self.user_activities[user_id]
        if not user_activity_ids:
            return 0.0
        
        # Get activities from last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        recent_activities = [
            activity for activity in self.activities
            if activity.activity_id in user_activity_ids and activity.timestamp >= cutoff_date
        ]
        
        if not recent_activities:
            return 0.0
        
        # Calculate average engagement score
        total_engagement = sum(activity.engagement_score for activity in recent_activities)
        return total_engagement / len(recent_activities)
    
    def recommend_friends(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate friend recommendations using multiple algorithms.
        
        Args:
            user_id: User to generate recommendations for
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended users with scores and reasons
        """
        recommendations = {}
        
        # 1. Mutual friends recommendation
        user_friends = {c.to_user_id for c in self.get_user_connections(user_id, ConnectionType.FRIEND)}
        
        for friend_id in user_friends:
            friend_friends = {c.to_user_id for c in self.get_user_connections(friend_id, ConnectionType.FRIEND)}
            
            for potential_friend in friend_friends:
                if potential_friend != user_id and potential_friend not in user_friends:
                    if potential_friend not in recommendations:
                        recommendations[potential_friend] = {
                            'user_id': potential_friend,
                            'score': 0,
                            'reasons': []
                        }
                    
                    recommendations[potential_friend]['score'] += 3
                    recommendations[potential_friend]['reasons'].append(f"Mutual friend: {friend_id}")
        
        # 2. Similar performance level recommendation
        # This would need user performance data - placeholder for now
        
        # 3. Team/organization connection recommendation
        user_teammates = {c.to_user_id for c in self.get_user_connections(user_id, ConnectionType.TEAMMATE)}
        
        for teammate_id in user_teammates:
            teammate_friends = {c.to_user_id for c in self.get_user_connections(teammate_id, ConnectionType.FRIEND)}
            
            for potential_friend in teammate_friends:
                if potential_friend != user_id and potential_friend not in user_friends:
                    if potential_friend not in recommendations:
                        recommendations[potential_friend] = {
                            'user_id': potential_friend,
                            'score': 0,
                            'reasons': []
                        }
                    
                    recommendations[potential_friend]['score'] += 2
                    recommendations[potential_friend]['reasons'].append(f"Teammate connection: {teammate_id}")
        
        # 4. Influence-based recommendations
        for other_user_id, influence_score in self.influence_scores.items():
            if (other_user_id != user_id and 
                other_user_id not in user_friends and 
                influence_score.influence_tier in ["Thought Leader", "Influencer"]):
                
                if other_user_id not in recommendations:
                    recommendations[other_user_id] = {
                        'user_id': other_user_id,
                        'score': 0,
                        'reasons': []
                    }
                
                influence_bonus = 2 if influence_score.influence_tier == "Thought Leader" else 1
                recommendations[other_user_id]['score'] += influence_bonus
                recommendations[other_user_id]['reasons'].append(f"High influence: {influence_score.influence_tier}")
        
        # Sort by score and return top recommendations
        sorted_recommendations = sorted(
            recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return sorted_recommendations[:limit]
    
    def add_activity(self, activity: SocialActivity) -> None:
        """Add a social activity to the feed"""
        self.activities.append(activity)
        self.user_activities[activity.user_id].append(activity.activity_id)
        
        # Keep activities list manageable
        if len(self.activities) > self.max_feed_size * 5:
            # Remove oldest activities
            self.activities = self.activities[-self.max_feed_size * 3:]
            
            # Clean up user activities references
            remaining_activity_ids = {activity.activity_id for activity in self.activities}
            for user_id in self.user_activities:
                self.user_activities[user_id] = [
                    aid for aid in self.user_activities[user_id] 
                    if aid in remaining_activity_ids
                ]
    
    def generate_activity_feed(self, 
                             user_id: str, 
                             limit: int = 20,
                             include_own: bool = False) -> List[SocialActivity]:
        """
        Generate personalized activity feed for a user.
        
        Args:
            user_id: User to generate feed for
            limit: Maximum number of activities
            include_own: Whether to include user's own activities
            
        Returns:
            Personalized activity feed
        """
        # Get user's network
        connections = self.get_user_connections(user_id)
        network_user_ids = {c.to_user_id for c in connections}
        
        if include_own:
            network_user_ids.add(user_id)
        
        # Filter activities from network
        relevant_activities = [
            activity for activity in self.activities
            if activity.user_id in network_user_ids and activity.visibility != "private"
        ]
        
        # Score activities for relevance
        scored_activities = []
        for activity in relevant_activities:
            score = self._calculate_activity_relevance_score(user_id, activity)
            scored_activities.append((activity, score))
        
        # Sort by relevance score
        scored_activities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top activities
        return [activity for activity, _ in scored_activities[:limit]]
    
    def _calculate_activity_relevance_score(self, user_id: str, activity: SocialActivity) -> float:
        """Calculate relevance score for an activity"""
        score = 0.0
        
        # Base score from activity engagement
        score += activity.engagement_score
        
        # Freshness bonus
        score += activity.freshness_score * 5
        
        # Connection strength bonus
        connection = self.get_connection(user_id, activity.user_id, ConnectionType.FRIEND)
        if connection:
            score += connection.effective_strength * 10
        
        # Activity type bonuses
        activity_type_bonuses = {
            ActivityType.ACHIEVEMENT_UNLOCK: 3,
            ActivityType.RANK_IMPROVEMENT: 2,
            ActivityType.STREAK_MILESTONE: 2,
            ActivityType.LEVEL_UP: 1,
            ActivityType.FRIEND_ADD: 0.5
        }
        score += activity_type_bonuses.get(activity.activity_type, 0)
        
        return score
    
    def get_network_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive network analytics for a user"""
        connections = self.get_user_connections(user_id)
        
        # Connection type breakdown
        connection_breakdown = defaultdict(int)
        for connection in connections:
            connection_breakdown[connection.connection_type.value] += 1
        
        # Network reach and influence
        reach = self.calculate_network_reach(user_id)
        influence = self.influence_scores.get(user_id)
        
        # Activity statistics
        user_activity_count = len(self.user_activities[user_id])
        recent_activities = [
            activity for activity in self.activities
            if (activity.user_id == user_id and 
                activity.timestamp >= datetime.utcnow() - timedelta(days=30))
        ]
        
        # Network density (how interconnected the user's network is)
        network_density = self._calculate_network_density(user_id)
        
        return {
            'total_connections': len(connections),
            'connection_breakdown': dict(connection_breakdown),
            'network_reach': reach,
            'network_density': network_density,
            'influence_score': influence.total_score if influence else 0,
            'influence_tier': influence.influence_tier if influence else "Observer",
            'total_activities': user_activity_count,
            'recent_activities': len(recent_activities),
            'engagement_rate': self.calculate_engagement_rate(user_id),
            'mutual_connection_opportunities': len(self.recommend_friends(user_id, 5))
        }
    
    def _calculate_network_density(self, user_id: str) -> float:
        """Calculate how interconnected a user's network is"""
        friends = [c.to_user_id for c in self.get_user_connections(user_id, ConnectionType.FRIEND)]
        
        if len(friends) < 2:
            return 0.0
        
        # Count connections between friends
        interconnections = 0
        for i, friend1 in enumerate(friends):
            for friend2 in friends[i+1:]:
                if self.get_connection(friend1, friend2, ConnectionType.FRIEND):
                    interconnections += 1
        
        # Calculate density (actual connections / possible connections)
        possible_connections = len(friends) * (len(friends) - 1) // 2
        return interconnections / possible_connections if possible_connections > 0 else 0.0
    
    def _is_cache_valid(self) -> bool:
        """Check if network cache is still valid"""
        return datetime.utcnow() - self._cache_timestamp < self.cache_duration
    
    def _clear_network_cache(self) -> None:
        """Clear network analysis cache"""
        self._network_cache = {}
        self._cache_timestamp = datetime.utcnow()