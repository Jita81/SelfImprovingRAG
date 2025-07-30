# Leaderboard & Social Features Module

## Overview
The Leaderboard & Social Features module provides comprehensive ranking, social comparison, and competitive elements for the Self-Improving RAG Platform. It implements real-time leaderboards with multiple time periods, privacy controls, social connections, team-based rankings, and historical tracking functionality.

## Features
- **Multi-Period Leaderboards**: Daily, weekly, monthly, and all-time rankings
- **Composite Ranking System**: Weighted scoring based on success rate, optimization count, streaks, and level
- **Privacy Controls**: User visibility settings and opt-out capabilities
- **Social Comparisons**: Friend networks, team rankings, and peer comparisons  
- **Category-Based Rankings**: Specialized leaderboards for different optimization types
- **Historical Snapshots**: Point-in-time leaderboard state preservation
- **Real-Time Updates**: Dynamic ranking recalculation on user stat changes
- **Streak Tracking**: Consecutive success monitoring and win streak management

## Architecture

### Domain Layer
- **Entities**: `LeaderboardEntry` (user ranking data), `SocialConnection` (user relationships)
- **Value Objects**: `LeaderboardPeriod` (time-based filtering), `RankingCriteria` (scoring algorithms)
- **Domain Services**: Composite scoring logic and ranking calculations

### Application Layer
- **Services**: `LeaderboardService` (orchestrates all leaderboard operations)
- **DTOs**: Request/response objects for all leaderboard and social operations
- **Use Cases**: Ranking updates, social comparisons, historical snapshots, team analytics

### Infrastructure Layer
- **Repositories**: `LeaderboardRepository`, `UserStatsRepository` with in-memory and file implementations
- **External Services**: JSON configuration loading for test data and social connections
- **Configuration**: Ranking criteria and social relationship data from test fixtures

### API Layer
- **Controllers**: (Future implementation for HTTP endpoints)
- **Routes**: (Future API endpoint definitions)
- **Middleware**: (Future cross-cutting concerns)

## Dependencies

### Internal Dependencies
- **User Management**: Integrates with user statistics and gamification data
- **Achievement System**: Social achievements and team-based unlocks

### External Dependencies
- **Python Standard Library**: `dataclasses`, `datetime`, `json`, `uuid`, `typing`, `enum`
- **File System**: JSON configuration files for leaderboard test data

## Configuration

### Test Data Files
```bash
tests/test_data/leaderboard_test_data.json  # Comprehensive leaderboard and social test data
```

### Ranking Criteria Types
The module supports multiple ranking algorithms:

| Criteria Type | Primary Metric | Weights | Use Case |
|---------------|----------------|---------|----------|
| **default** | success_rate (40%) | optimizations (30%), streak (20%), level (10%) | Balanced performance |
| **streak_focused** | current_streak (50%) | success_rate (30%), optimizations (20%) | Consistency emphasis |
| **volume_focused** | total_optimizations (50%) | success_rate (40%), streak (10%) | Activity emphasis |

### Time Periods
- **Daily**: Current day (00:00 to 23:59)
- **Weekly**: Monday to Sunday of current week
- **Monthly**: First to last day of current month  
- **All-Time**: Complete user history

## Usage Examples

### Basic Leaderboard Retrieval
```python
# Create leaderboard service
from leaderboard_social.infrastructure.repositories.leaderboard_repository import InMemoryLeaderboardRepository
from leaderboard_social.infrastructure.repositories.user_stats_repository import InMemoryUserStatsRepository
from leaderboard_social.application.services.leaderboard_service import LeaderboardService

leaderboard_repo = InMemoryLeaderboardRepository()
user_stats_repo = InMemoryUserStatsRepository()
service = LeaderboardService(leaderboard_repo, user_stats_repo)

# Get weekly leaderboard
from leaderboard_social.application.dtos.leaderboard_requests import GetLeaderboardRequest

request = GetLeaderboardRequest(
    period="weekly",
    limit=10,
    ranking_criteria="default",
    respect_privacy=True
)
response = service.get_leaderboard(request)

for entry in response.leaderboard_entries:
    print(f"#{entry['rank']}: {entry['user_name']} - {entry['success_rate']:.1f}%")
```

### User Statistics Updates
```python
# Update user performance and recalculate rankings
from leaderboard_social.application.dtos.leaderboard_requests import UpdateUserStatsRequest

update_request = UpdateUserStatsRequest(
    user_id="user-001",
    success_rate=98.5,
    total_optimizations=160,
    current_streak=15,
    optimization_result=True  # Success - increments streak
)
update_response = service.update_user_stats(update_request)

print(f"New rank: {update_response.new_rank}")
print(f"Streak updated to: {update_response.new_streak}")
```

### Social Comparisons
```python
# Compare user performance with friends
from leaderboard_social.application.dtos.leaderboard_requests import GetSocialComparisonRequest

social_request = GetSocialComparisonRequest(
    user_id="user-001",
    comparison_type="friends",
    metric="success_rate"
)
social_response = service.get_social_comparison(social_request)

comparison = social_response.comparison_data
print(f"Your success rate: {comparison['user_value']:.1f}%")
print(f"Friends average: {comparison['friends_average']:.1f}%")
print(f"Rank among friends: #{comparison['user_rank_among_friends']}")
```

### Team Leaderboards
```python
# Get team-specific rankings
team_request = GetLeaderboardRequest(
    period="monthly",
    team_name="Engineering",
    limit=5
)
team_response = service.get_leaderboard(team_request)

print(f"Engineering Team Leaderboard:")
print(f"Team average success rate: {team_response.team_statistics['average_success_rate']:.1f}%")
```

## API Reference

### Core Services
- `LeaderboardService`: Main service class
  - `get_leaderboard()`: Retrieve ranked user listings with filtering
  - `update_user_stats()`: Update user performance and recalculate rankings
  - `get_user_ranking()`: Get specific user's rank and composite score
  - `get_social_comparison()`: Compare user with friends/team members
  - `create_historical_snapshot()`: Save point-in-time leaderboard state

### DTOs

#### Request DTOs
- `GetLeaderboardRequest`: Leaderboard retrieval with filtering options
- `UpdateUserStatsRequest`: User performance updates and streak tracking
- `GetUserRankingRequest`: Individual user ranking queries
- `GetSocialComparisonRequest`: Social comparison requests
- `CreateHistoricalSnapshotRequest`: Historical snapshot creation

#### Response DTOs
- `GetLeaderboardResponse`: Leaderboard data with entries and metadata
- `UpdateUserStatsResponse`: User update results with ranking changes
- `GetUserRankingResponse`: User ranking details with composite scores
- `GetSocialComparisonResponse`: Social comparison analytics
- `CreateHistoricalSnapshotResponse`: Snapshot creation confirmation

For detailed API documentation, see [API.md](./API.md).

## Testing

### Running Tests
```bash
# Run all tests for this module
cd modules/leaderboard_social
python3 manual_test.py

# Run with debug output (optional)
export MODULE_DEBUG=true
python3 manual_test.py
```

### Test Coverage
- **Unit Tests**: 100% coverage (10 test scenarios)
- **Integration Tests**: Service-repository integration
- **End-to-End Tests**: Complete leaderboard workflows

### Test Scenarios
1. **Ranking Updates**: User statistics changes reflect in leaderboard positions
2. **Time Period Filtering**: Weekly/daily leaderboards filter correctly
3. **Streak Tracking**: Consecutive wins/losses update streak counters
4. **Privacy Filtering**: Hidden users are excluded from public leaderboards
5. **Composite Scoring**: Weighted ranking calculations work correctly
6. **Historical Snapshots**: Point-in-time leaderboard state preservation
7. **Category Filtering**: Category-specific leaderboards function properly
8. **Social Comparisons**: Friend network comparison calculations
9. **Team Analytics**: Team-based leaderboards and statistics
10. **Daily Updates**: Daily leaderboard creation and maintenance

For detailed testing information, see [TESTING.md](./TESTING.md).

## Data Management

### Data Models

#### LeaderboardEntry Entity (Aggregate Root)
- **Core Metrics**: success_rate, total_optimizations, current_streak, level, total_xp
- **Period Stats**: period_optimizations, period_successes, period_success_rate
- **Category Data**: category_score, category_rank for specialized rankings
- **Composite Scoring**: composite_score and score_breakdown components
- **Social Data**: achievements, badges, team_name for display
- **Privacy Settings**: is_visible, show_stats for user control

#### SocialConnection Entity
- **Relationships**: friends, following, followers lists
- **Team Membership**: team_name for team-based features
- **Metadata**: connection timestamps and relationship tracking

#### LeaderboardPeriod Value Object
- **Time Ranges**: Automatic date range calculation for periods
- **Validation**: Period type validation and date boundary checking
- **Utilities**: Period labeling and date containment checking

#### RankingCriteria Value Object
- **Scoring Algorithms**: Weighted composite score calculation
- **Normalization**: Metric scaling to comparable ranges
- **Comparison Logic**: User ranking comparison with tiebreaking

### Data Flow
1. **User Update**: Statistics update → Ranking recalculation → Leaderboard refresh
2. **Period Filtering**: Time range calculation → Entry filtering → Ranked results
3. **Social Comparison**: Relationship lookup → Metric aggregation → Comparison analytics
4. **Historical Snapshot**: Current state capture → Serialization → Storage

### Persistence
- **Repository Pattern**: Abstract data access with multiple implementations
- **In-Memory Implementation**: Fast access for testing and development with test data loading
- **File-Based Implementation**: JSON persistence for development environments
- **Database Implementation**: Future PostgreSQL/MongoDB integration for production

## Integration

### Event Publishing
This module will publish the following events:
- `LeaderboardUpdated`: When rankings change significantly
- `UserRankChanged`: When individual user rank changes
- `StreakAchieved`: When users reach notable streak milestones
- `TeamStatisticsUpdated`: When team performance metrics change

### Event Subscription
This module subscribes to:
- `UserStatsUpdated`: From User Management module for ranking updates
- `AchievementUnlocked`: From Achievement System for bonus recognition
- `OptimizationCompleted`: From Core RAG module for real-time updates

### API Integration
- **APIs Provided**: Leaderboard data, social comparisons, team analytics
- **APIs Consumed**: User Management for user data, Achievement System for unlocks

## Social Features

### Friend Networks
- **Mutual Connections**: Two-way friend relationships
- **Following System**: One-way follow relationships for public figures
- **Social Comparisons**: Performance comparison with social connections
- **Privacy Respect**: Honors user privacy settings in all social features

### Team Functionality
- **Team Leaderboards**: Isolated rankings within teams
- **Team Statistics**: Aggregate performance metrics
- **Team Comparisons**: Inter-team performance analysis

### Privacy Controls
- **Leaderboard Visibility**: Users can opt out of public leaderboards
- **Statistics Sharing**: Users can hide detailed stats while remaining visible
- **Achievement Privacy**: Users can control achievement visibility

## Error Handling

### Common Errors
- `ValueError`: Invalid period types, negative metrics, malformed ranking criteria
- `KeyError`: User not found, missing leaderboard entries
- `TypeError`: Invalid data types in requests or responses

### Error Response Format
```json
{
  "success": false,
  "error": "User not found in leaderboard",
  "timestamp": "2023-12-07T10:30:00Z"
}
```

## Performance Considerations

### Optimization Notes
- **Composite Scoring**: O(n log n) sorting with efficient scoring algorithms
- **Period Filtering**: Optimized date range calculations
- **Privacy Filtering**: Pre-filtered datasets reduce processing overhead
- **Caching Strategy**: In-memory caching of frequently accessed rankings

### Monitoring
- **Ranking Calculation Time**: Performance monitoring for large user bases
- **Update Frequency**: Rate limiting for excessive ranking updates
- **Memory Usage**: Monitoring in-memory repository size
- **Cache Hit Rates**: Effectiveness of ranking caches

## Security Considerations

### Data Protection
- **Privacy Enforcement**: Server-side privacy setting enforcement
- **Input Validation**: All request parameters validated before processing
- **Access Control**: Future role-based access for admin functions

### Privacy Features
- **Granular Controls**: Multiple levels of privacy settings
- **Data Minimization**: Only necessary data exposed in leaderboards
- **User Consent**: Clear privacy controls and user consent mechanisms

## Troubleshooting

### Common Issues
1. **Import Errors**: Module import resolution issues
   - **Cause**: Python path configuration or relative import problems
   - **Solution**: Use manual_test.py script which handles import paths correctly

2. **Ranking Inconsistencies**: Users appearing in wrong positions
   - **Cause**: Stale data or incorrect composite score calculation
   - **Solution**: Verify ranking criteria weights and trigger full recalculation

3. **Privacy Violations**: Hidden users appearing in leaderboards
   - **Cause**: Privacy filtering not applied correctly
   - **Solution**: Ensure respect_privacy=True in requests and verify user settings

4. **Streak Tracking Errors**: Incorrect streak counts
   - **Cause**: Conflicting streak update logic
   - **Solution**: Use either optimization_result OR current_streak in requests, not both

### Debug Mode
```bash
# Enable debug logging for detailed tracing
export MODULE_DEBUG=true
python3 manual_test.py
```

## Development Guidelines

### Adding New Features
1. Update domain entities/value objects in `domain/`
2. Implement application services in `application/services/`
3. Add infrastructure support in `infrastructure/`
4. Create API endpoints in `api/` (future)
5. Write comprehensive tests in `manual_test.py`
6. Update test data in `tests/test_data/leaderboard_test_data.json`
7. Update all documentation

### Code Style
- Follow PEP 8 for Python code
- Use type hints consistently (`typing` module)
- Write descriptive docstrings for all public methods
- Use dataclasses for DTOs, entities, and value objects
- Use Enums for fixed value sets (ranking types, period types)
- Follow Repository pattern for data access
- Implement comprehensive error handling with meaningful messages

### Adding New Ranking Criteria
1. Define new criteria type in `RankingType` enum
2. Add weights and metrics in `RankingCriteria.from_dict()`
3. Create factory method for new criteria type
4. Add test cases covering new ranking behavior
5. Update documentation with new criteria description

## Changelog

### Version 1.0.0 - 2023-12-07
#### Added
- Initial implementation of Leaderboard & Social Features module (TDD Cycle 12)
- Multi-period leaderboard system (daily, weekly, monthly, all-time)
- Composite ranking system with weighted scoring algorithms
- Privacy controls with granular user visibility settings
- Social comparison features with friend networks and team analytics
- Category-based leaderboards for specialized rankings
- Historical snapshot system for point-in-time leaderboard preservation
- Real-time ranking updates with automatic recalculation
- Streak tracking with consecutive win/loss monitoring
- Hexagonal architecture with domain/application/infrastructure separation
- Repository pattern with in-memory and file-based implementations
- Comprehensive manual testing framework with 10 test scenarios
- JSON-based test data with realistic user scenarios

#### Core Features
- **Ranking System**: Multi-criteria weighted scoring with 3 preset algorithms
- **Time Periods**: Automatic date range calculation for all period types
- **Social Features**: Friend networks, team leaderboards, social comparisons
- **Privacy System**: User-controlled visibility and statistics sharing
- **Historical Tracking**: Snapshot creation and retrieval functionality
- **Data Management**: Complete CRUD operations for leaderboard entries

#### Test Coverage
- Unit tests for all domain entities and value objects
- Integration tests for service-repository interactions
- End-to-End tests for complete leaderboard workflows
- Manual test script with comprehensive scenarios
- Test data fixtures with realistic multi-user scenarios

#### Documentation
- Comprehensive README with usage examples and architecture overview
- API documentation with request/response schemas
- Testing documentation with scenario descriptions
- Inline code documentation for all public methods

For detailed changelog, see [CHANGELOG.md](./CHANGELOG.md).

## Contributing

### Development Setup
1. Navigate to `modules/leaderboard_social/`
2. Ensure Python 3.8+ is available
3. Verify test data file exists: `../../tests/test_data/leaderboard_test_data.json`
4. Run manual tests to verify functionality: `python3 manual_test.py`

### Pull Request Process
1. Update documentation (README, API, TESTING, CHANGELOG)
2. Add/update tests for new functionality
3. Ensure all manual tests pass (10/10 success rate)
4. Update test data if new scenarios are added
5. Verify integration with User Management and Achievement System modules

## Related Documentation
- [Main Project README](../../README.md)
- [Architecture Overview](../../docs/architecture/)
- [API Documentation](./API.md)
- [Testing Guide](./TESTING.md)
- [Module Implementation Summary](../../module_implementation_summary.md)
- [TDD Cycles Documentation](../../tdd_cycles_self_improving_rag.md)
- [Leaderboard Test Data](../../tests/test_data/leaderboard_test_data.json)
- [User Management Module](../user_management/README.md)
- [Achievement System Module](../achievement_system/README.md)
- [Documentation Standards](../../docs/DOCUMENTATION_STANDARDS.md)