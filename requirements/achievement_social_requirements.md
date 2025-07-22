# Achievement & Social Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: Achievement & Social  
**Size Estimate**: ~27k tokens  
**Priority**: 2 (Engagement)  
**TDD Cycles**: 11, 12  
**Branch**: `module/achievement-social`  
**Cursor Window**: #7  
**Dependencies**: Orchestrator, User Management Modules  

### **Purpose**
Manages achievements, leaderboards, and social features that drive user engagement through recognition, competition, and community interaction.

---

## 🎯 **Functional Requirements**

### **FR-1: Achievement System** (TDD Cycle 11)
- **FR-1.1**: Define achievements with unlock criteria and XP rewards
- **FR-1.2**: Track user progress toward achievement completion
- **FR-1.3**: Unlock achievements when criteria are met
- **FR-1.4**: Support different achievement types (progress, milestone, hidden)
- **FR-1.5**: Award XP and unlock new features upon achievement
- **FR-1.6**: Support time-limited and seasonal achievements

### **FR-2: Leaderboard System** (TDD Cycle 12)
- **FR-2.1**: Maintain real-time leaderboards for various metrics
- **FR-2.2**: Support different leaderboard periods (daily, weekly, monthly, all-time)
- **FR-2.3**: Calculate composite scores and rankings
- **FR-2.4**: Handle leaderboard privacy settings and opt-outs
- **FR-2.5**: Support filtered leaderboards by domain/category
- **FR-2.6**: Provide historical leaderboard snapshots

### **FR-3: Social Comparison**
- **FR-3.1**: Compare user performance with peers
- **FR-3.2**: Show progress relative to community averages
- **FR-3.3**: Support friend/follower system for closer comparisons
- **FR-3.4**: Provide social motivation through gentle competition
- **FR-3.5**: Show achievement galleries and profiles

---

## 🏗️ **Technical Architecture**

```typescript
// Domain Layer
export class Achievement {
    constructor(
        public readonly id: AchievementId,
        public readonly name: string,
        public readonly description: string,
        public readonly category: AchievementCategory,
        public readonly rarity: AchievementRarity,
        private trigger: AchievementTrigger,
        private xpReward: ExperiencePoints,
        private requirements: AchievementRequirement[],
        public readonly isHidden: boolean = false
    ) {}

    checkUnlock(stats: UserStatistics): boolean {
        return this.trigger.isTriggered(stats) && 
               this.requirements.every(req => req.isMet(stats));
    }

    unlock(userId: UserId): AchievementUnlock {
        return new AchievementUnlock(
            this.id,
            userId,
            this.xpReward,
            new Date()
        );
    }
}

export class Leaderboard {
    constructor(
        public readonly id: LeaderboardId,
        public readonly name: string,
        public readonly metric: LeaderboardMetric,
        public readonly period: LeaderboardPeriod,
        private rankings: LeaderboardEntry[],
        private readonly updatedAt: Date = new Date()
    ) {}

    updateRankings(performances: UserPerformance[]): void {
        this.rankings = performances
            .sort((a, b) => this.comparePerformances(a, b))
            .map((perf, index) => new LeaderboardEntry(
                perf.userId,
                index + 1,
                perf.score,
                perf.metadata
            ));
    }

    getRanking(userId: UserId): LeaderboardPosition | null {
        const entry = this.rankings.find(r => r.userId.equals(userId));
        return entry ? new LeaderboardPosition(entry.rank, entry.score) : null;
    }

    getTopRankings(limit: number = 10): LeaderboardEntry[] {
        return this.rankings.slice(0, limit);
    }

    private comparePerformances(a: UserPerformance, b: UserPerformance): number {
        return this.metric.compareDescending ? 
            b.score - a.score : a.score - b.score;
    }
}

// Application Services
@Injectable()
export class AchievementService {
    constructor(
        private readonly repository: IAchievementRepository,
        private readonly userStatsService: IUserStatisticsService,
        private readonly gamificationService: IGamificationService,
        private readonly eventBus: IEventBus
    ) {}

    async checkAchievements(userId: UserId): Promise<AchievementUnlock[]> {
        const userStats = await this.userStatsService.getUserStatistics(userId);
        const availableAchievements = await this.repository.getAvailableForUser(userId);
        
        const unlocked: AchievementUnlock[] = [];
        
        for (const achievement of availableAchievements) {
            if (achievement.checkUnlock(userStats)) {
                const unlock = achievement.unlock(userId);
                await this.repository.recordUnlock(unlock);
                
                // Award XP
                await this.gamificationService.awardExperience(
                    userId,
                    unlock.xpReward,
                    `Achievement: ${achievement.name}`
                );
                
                unlocked.push(unlock);
                
                await this.eventBus.publish(new AchievementUnlockedEvent(
                    unlock.achievementId,
                    userId,
                    achievement.name,
                    unlock.xpReward
                ));
            }
        }
        
        return unlocked;
    }

    async getUserAchievements(userId: UserId): Promise<UserAchievementSummary> {
        const unlocked = await this.repository.getUserUnlocked(userId);
        const available = await this.repository.getAvailableForUser(userId);
        const progress = await this.calculateProgress(userId, available);
        
        return new UserAchievementSummary(
            unlocked,
            available,
            progress,
            this.calculateCompletionRate(unlocked, available)
        );
    }

    private async calculateProgress(
        userId: UserId, 
        achievements: Achievement[]
    ): Promise<Map<AchievementId, number>> {
        const userStats = await this.userStatsService.getUserStatistics(userId);
        const progress = new Map<AchievementId, number>();
        
        achievements.forEach(achievement => {
            const progressValue = achievement.trigger.calculateProgress(userStats);
            progress.set(achievement.id, progressValue);
        });
        
        return progress;
    }
}

@Injectable()
export class LeaderboardService {
    constructor(
        private readonly repository: ILeaderboardRepository,
        private readonly performanceService: IPerformanceService,
        private readonly userService: IUserService
    ) {}

    async updateLeaderboard(
        leaderboardId: LeaderboardId, 
        period: LeaderboardPeriod
    ): Promise<void> {
        const leaderboard = await this.repository.findById(leaderboardId);
        if (!leaderboard) return;
        
        const timeframe = period.getTimeframe();
        const performances = await this.performanceService.getUserPerformances(
            leaderboard.metric,
            timeframe
        );
        
        leaderboard.updateRankings(performances);
        await this.repository.save(leaderboard);
    }

    async getUserRanking(
        userId: UserId, 
        leaderboardId: LeaderboardId
    ): Promise<UserRankingInfo> {
        const leaderboard = await this.repository.findById(leaderboardId);
        if (!leaderboard) {
            throw new LeaderboardNotFoundError(leaderboardId);
        }
        
        const position = leaderboard.getRanking(userId);
        const totalParticipants = leaderboard.getTotalParticipants();
        
        return new UserRankingInfo(
            position?.rank || null,
            position?.score || 0,
            totalParticipants,
            this.calculatePercentile(position?.rank, totalParticipants)
        );
    }

    async getLeaderboardData(
        leaderboardId: LeaderboardId,
        limit: number = 10
    ): Promise<LeaderboardData> {
        const leaderboard = await this.repository.findById(leaderboardId);
        if (!leaderboard) {
            throw new LeaderboardNotFoundError(leaderboardId);
        }
        
        const topEntries = leaderboard.getTopRankings(limit);
        const enrichedEntries = await this.enrichWithUserData(topEntries);
        
        return new LeaderboardData(
            leaderboard.name,
            leaderboard.period,
            enrichedEntries,
            leaderboard.updatedAt
        );
    }

    private async enrichWithUserData(
        entries: LeaderboardEntry[]
    ): Promise<EnrichedLeaderboardEntry[]> {
        const userIds = entries.map(e => e.userId);
        const users = await this.userService.getUsersByIds(userIds);
        
        return entries.map(entry => {
            const user = users.find(u => u.id.equals(entry.userId));
            return new EnrichedLeaderboardEntry(
                entry.rank,
                user?.profile.name || 'Unknown',
                user?.profile.avatar || null,
                entry.score,
                entry.metadata
            );
        });
    }
}
```

---

## 📊 **Database Schema**

```sql
-- Achievements
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category achievement_category NOT NULL,
    rarity achievement_rarity NOT NULL,
    xp_reward INTEGER NOT NULL DEFAULT 0,
    trigger_config JSONB NOT NULL,
    requirements JSONB DEFAULT '[]',
    is_hidden BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE achievement_category AS ENUM ('optimization', 'social', 'milestone', 'special', 'seasonal');
CREATE TYPE achievement_rarity AS ENUM ('common', 'uncommon', 'rare', 'epic', 'legendary');

-- User Achievement Unlocks
CREATE TABLE user_achievement_unlocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    xp_awarded INTEGER NOT NULL,
    UNIQUE(user_id, achievement_id)
);

-- Leaderboards
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    period leaderboard_period NOT NULL,
    is_active BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE leaderboard_period AS ENUM ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'all_time');

-- Leaderboard Entries
CREATE TABLE leaderboard_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leaderboard_id UUID REFERENCES leaderboards(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    score DECIMAL(12,4) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_leaderboard_entries_leaderboard_rank ON leaderboard_entries(leaderboard_id, rank);
CREATE INDEX idx_leaderboard_entries_user_period ON leaderboard_entries(user_id, period_start, period_end);

-- Social Comparisons
CREATE TABLE social_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    comparison_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    user_value DECIMAL(12,4) NOT NULL,
    peer_average DECIMAL(12,4) NOT NULL,
    percentile DECIMAL(5,2) NOT NULL,
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 **API Specifications**

```yaml
paths:
  /achievements:
    get:
      summary: Get available achievements
      responses:
        200:
          description: List of achievements
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Achievement'

  /achievements/user/{userId}:
    get:
      summary: Get user's achievements
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: User achievement summary

  /leaderboards:
    get:
      summary: Get available leaderboards
      responses:
        200:
          description: List of leaderboards

  /leaderboards/{id}:
    get:
      summary: Get leaderboard data
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
      responses:
        200:
          description: Leaderboard data

components:
  schemas:
    Achievement:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        description:
          type: string
        category:
          type: string
        rarity:
          type: string
        xpReward:
          type: integer
```

---

## 🧪 **Testing Requirements**

### **Unit Tests** (TDD Cycles 11, 12)

```typescript
// TDD Cycle 11: Achievement System
describe('AchievementService', () => {
    describe('checkAchievements', () => {
        it('should unlock achievement when criteria met', async () => {
            // RED: Test fails initially
            const userId = UserId.generate();
            const achievement = createMockAchievement({
                name: 'First Optimization',
                trigger: new OptimizationCountTrigger(1),
                xpReward: new ExperiencePoints(100)
            });
            
            const userStats = createMockUserStatistics({
                totalOptimizations: 1
            });
            
            mockUserStatsService.getUserStatistics.mockResolvedValue(userStats);
            mockRepository.getAvailableForUser.mockResolvedValue([achievement]);

            const unlocked = await service.checkAchievements(userId);

            expect(unlocked).toHaveLength(1);
            expect(unlocked[0].achievementId).toBe(achievement.id);
            expect(mockGamificationService.awardExperience).toHaveBeenCalledWith(
                userId,
                new ExperiencePoints(100),
                'Achievement: First Optimization'
            );
        });
    });
});

// TDD Cycle 12: Leaderboards
describe('LeaderboardService', () => {
    describe('updateLeaderboard', () => {
        it('should update rankings based on performance', async () => {
            // RED: Test fails initially
            const leaderboard = createMockLeaderboard({
                metric: LeaderboardMetric.SUCCESS_RATE
            });
            const performances = [
                createUserPerformance(UserId.generate(), 0.85),
                createUserPerformance(UserId.generate(), 0.92),
                createUserPerformance(UserId.generate(), 0.78)
            ];
            
            mockRepository.findById.mockResolvedValue(leaderboard);
            mockPerformanceService.getUserPerformances.mockResolvedValue(performances);

            await service.updateLeaderboard(leaderboard.id, LeaderboardPeriod.WEEKLY);

            expect(leaderboard.rankings[0].score).toBe(0.92); // Highest score first
            expect(leaderboard.rankings[0].rank).toBe(1);
            expect(mockRepository.save).toHaveBeenCalledWith(leaderboard);
        });
    });
});
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Unlock achievements when criteria are met
- [ ] Award XP and trigger level-ups for achievements  
- [ ] Maintain real-time leaderboards with accurate rankings
- [ ] Support multiple leaderboard periods and metrics
- [ ] Provide social comparison with peer averages
- [ ] Handle achievement progress tracking

### **Performance Acceptance**
- [ ] Achievement checks complete within 500ms
- [ ] Leaderboard updates finish within 30 seconds
- [ ] Support 10,000+ users in leaderboards
- [ ] Real-time ranking updates within 5 seconds

This Achievement & Social Module drives user engagement through recognition, competition, and community features essential for platform retention and motivation. 