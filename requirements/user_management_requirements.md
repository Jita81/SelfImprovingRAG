# User Management Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: User Management  
**Size Estimate**: ~26k tokens  
**Priority**: 1 (Foundation)  
**TDD Cycles**: 10  
**Branch**: `module/user-management`  
**Cursor Window**: #3  
**Dependencies**: Orchestrator Module  

### **Purpose**
The User Management Module handles user profiles, authentication, gamification mechanics, and experience point systems. It provides the foundation for user-driven features across the platform, including leveling, achievements, and personalized experiences.

---

## 🎯 **Functional Requirements**

### **FR-1: User Profile Management** (TDD Cycle 10)
- **FR-1.1**: Create user profiles with basic information (name, email, preferences)
- **FR-1.2**: Update user profile information and settings
- **FR-1.3**: Store user preferences for UI, notifications, and features
- **FR-1.4**: Manage user avatar and display customization
- **FR-1.5**: Support user profile visibility settings (public/private)
- **FR-1.6**: Track user account creation and last activity dates
- **FR-1.7**: Handle user account deactivation and data retention

### **FR-2: Gamification System** (TDD Cycle 10)
- **FR-2.1**: Initialize users with Level 1 and 0 experience points
- **FR-2.2**: Award experience points for various platform activities
- **FR-2.3**: Calculate level progression based on XP thresholds
- **FR-2.4**: Track win streaks for successful optimizations
- **FR-2.5**: Maintain total optimization count per user
- **FR-2.6**: Support bonus XP multipliers for premium users
- **FR-2.7**: Handle XP penalties for failed or poor-quality submissions

### **FR-3: Level Progression System**
- **FR-3.1**: Define level thresholds with exponential scaling
- **FR-3.2**: Trigger level-up events and notifications
- **FR-3.3**: Unlock features and capabilities based on user level
- **FR-3.4**: Display level progress and next level requirements
- **FR-3.5**: Support prestige levels for advanced users
- **FR-3.6**: Track level-up history and timestamps

### **FR-4: Activity Tracking**
- **FR-4.1**: Record user activities across all platform modules
- **FR-4.2**: Track login/logout events and session duration
- **FR-4.3**: Monitor feature usage patterns and preferences
- **FR-4.4**: Store activity timestamps for trend analysis
- **FR-4.5**: Support activity filtering and search
- **FR-4.6**: Generate activity summaries and reports

### **FR-5: User Authentication**
- **FR-5.1**: Support email/password authentication
- **FR-5.2**: Implement secure password requirements and validation
- **FR-5.3**: Provide password reset functionality
- **FR-5.4**: Support OAuth integration (Google, GitHub, etc.)
- **FR-5.5**: Handle multi-factor authentication (MFA)
- **FR-5.6**: Manage user sessions and token refresh

### **FR-6: User Preferences**
- **FR-6.1**: Store UI theme preferences (dark/light mode)
- **FR-6.2**: Manage notification preferences per type
- **FR-6.3**: Save dashboard layout and widget preferences
- **FR-6.4**: Support language and localization settings
- **FR-6.5**: Store optimization algorithm preferences
- **FR-6.6**: Handle privacy settings and data sharing preferences

---

## 🔧 **Non-Functional Requirements**

### **NFR-1: Performance**
- **NFR-1.1**: User profile retrieval < 100ms for 95% of requests
- **NFR-1.2**: XP calculation and level updates < 50ms
- **NFR-1.3**: Support 10,000+ concurrent active users
- **NFR-1.4**: Authentication response time < 200ms
- **NFR-1.5**: Activity tracking with minimal latency impact

### **NFR-2: Security**
- **NFR-2.1**: Password encryption with bcrypt (minimum 12 rounds)
- **NFR-2.2**: Secure session management with JWT tokens
- **NFR-2.3**: Protection against brute force attacks
- **NFR-2.4**: PII data encryption at rest and in transit
- **NFR-2.5**: GDPR compliance for user data handling

### **NFR-3: Scalability**
- **NFR-3.1**: Horizontal scaling for user read operations
- **NFR-3.2**: Database partitioning for large user datasets
- **NFR-3.3**: Caching for frequently accessed user data
- **NFR-3.4**: Activity log archiving for historical data
- **NFR-3.5**: Support for 1M+ registered users

### **NFR-4: Reliability**
- **NFR-4.1**: 99.9% uptime for authentication services
- **NFR-4.2**: Graceful degradation when external auth providers fail
- **NFR-4.3**: Data consistency for XP updates across transactions
- **NFR-4.4**: Automatic backup of user profile data
- **NFR-4.5**: User data recovery mechanisms

### **NFR-5: Usability**
- **NFR-5.1**: Intuitive profile management interface
- **NFR-5.2**: Clear level progression visualization
- **NFR-5.3**: Responsive design for mobile devices
- **NFR-5.4**: Accessibility compliance (WCAG 2.1)
- **NFR-5.5**: Multi-language support for global users

---

## 🏗️ **Technical Architecture**

### **Architecture Pattern**: Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │    User     │ │Gamification │ │    Auth     │       │
│  │ Controller  │ │ Controller  │ │ Controller  │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│              Application Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │    User     │ │Gamification │ │    Auth     │       │
│  │ Management  │ │   Service   │ │   Service   │       │
│  │  Service    │ │             │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                Domain Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │    User     │ │Gamification │ │ Activity    │       │
│  │  Aggregate  │ │    Stats    │ │   Record    │       │
│  │             │ │             │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│            Infrastructure Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ PostgreSQL  │ │    Redis    │ │   OAuth     │       │
│  │ Repository  │ │    Cache    │ │  Provider   │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### **Core Components**

#### **1. Domain Layer**

```typescript
// User Aggregate Root
export class User {
    constructor(
        public readonly id: UserId,
        private profile: UserProfile,
        private gamification: GamificationStats,
        private preferences: UserPreferences,
        private activities: ActivityRecord[] = []
    ) {}

    updateProfile(changes: ProfileUpdate): void {
        this.profile = this.profile.update(changes);
        this.recordActivity(new ProfileUpdatedActivity(this.id, changes));
    }

    gainExperience(points: ExperiencePoints, reason: string): LevelUpResult {
        const oldLevel = this.gamification.level;
        this.gamification = this.gamification.addExperience(points);
        
        this.recordActivity(new ExperienceGainedActivity(this.id, points, reason));

        if (this.gamification.level.value > oldLevel.value) {
            const levelUpResult = new LevelUpResult(
                oldLevel,
                this.gamification.level,
                this.gamification.getUnlockedFeatures()
            );
            this.recordActivity(new LevelUpActivity(this.id, levelUpResult));
            return levelUpResult;
        }

        return LevelUpResult.noLevelUp();
    }

    incrementWinStreak(): void {
        this.gamification = this.gamification.incrementWinStreak();
        this.recordActivity(new WinStreakIncrementedActivity(this.id, this.gamification.winStreak));
    }

    resetWinStreak(): void {
        this.gamification = this.gamification.resetWinStreak();
        this.recordActivity(new WinStreakResetActivity(this.id));
    }

    updatePreferences(preferences: Partial<UserPreferences>): void {
        this.preferences = this.preferences.update(preferences);
        this.recordActivity(new PreferencesUpdatedActivity(this.id, preferences));
    }

    recordOptimization(success: boolean): void {
        this.gamification = this.gamification.recordOptimization();
        
        if (success) {
            this.incrementWinStreak();
            const xpGained = this.calculateOptimizationXP();
            this.gainExperience(xpGained, 'Successful optimization');
        } else {
            this.resetWinStreak();
        }
    }

    private calculateOptimizationXP(): ExperiencePoints {
        // Base XP + streak bonus + level multiplier
        const baseXP = 50;
        const streakBonus = Math.min(this.gamification.winStreak.value * 5, 100);
        const levelMultiplier = 1 + (this.gamification.level.value * 0.1);
        
        return new ExperiencePoints(Math.floor((baseXP + streakBonus) * levelMultiplier));
    }

    private recordActivity(activity: ActivityRecord): void {
        this.activities.push(activity);
        
        // Keep only last 100 activities in memory
        if (this.activities.length > 100) {
            this.activities = this.activities.slice(-100);
        }
    }
}

// Gamification Stats Value Object
export class GamificationStats {
    constructor(
        public readonly level: Level,
        public readonly experiencePoints: ExperiencePoints,
        public readonly nextLevelThreshold: ExperiencePoints,
        public readonly winStreak: WinStreak,
        public readonly totalOptimizations: number,
        public readonly unlockedAchievements: AchievementId[] = []
    ) {}

    addExperience(points: ExperiencePoints): GamificationStats {
        const newXP = this.experiencePoints.add(points);
        const newLevel = this.calculateLevel(newXP);
        const newThreshold = this.calculateNextThreshold(newLevel);

        return new GamificationStats(
            newLevel,
            newXP,
            newThreshold,
            this.winStreak,
            this.totalOptimizations,
            this.unlockedAchievements
        );
    }

    incrementWinStreak(): GamificationStats {
        return new GamificationStats(
            this.level,
            this.experiencePoints,
            this.nextLevelThreshold,
            this.winStreak.increment(),
            this.totalOptimizations,
            this.unlockedAchievements
        );
    }

    resetWinStreak(): GamificationStats {
        return new GamificationStats(
            this.level,
            this.experiencePoints,
            this.nextLevelThreshold,
            WinStreak.zero(),
            this.totalOptimizations,
            this.unlockedAchievements
        );
    }

    recordOptimization(): GamificationStats {
        return new GamificationStats(
            this.level,
            this.experiencePoints,
            this.nextLevelThreshold,
            this.winStreak,
            this.totalOptimizations + 1,
            this.unlockedAchievements
        );
    }

    getProgressToNextLevel(): number {
        if (this.level.value >= 100) return 1.0; // Max level
        
        const currentLevelXP = this.calculateLevelXP(this.level);
        const progressXP = this.experiencePoints.value - currentLevelXP;
        const requiredXP = this.nextLevelThreshold.value - currentLevelXP;
        
        return Math.min(progressXP / requiredXP, 1.0);
    }

    getUnlockedFeatures(): Feature[] {
        const features: Feature[] = [];
        
        if (this.level.value >= 5) features.push(Feature.ADVANCED_OPTIMIZATION);
        if (this.level.value >= 10) features.push(Feature.CUSTOM_ALGORITHMS);
        if (this.level.value >= 15) features.push(Feature.API_ACCESS);
        if (this.level.value >= 20) features.push(Feature.BETA_FEATURES);
        if (this.level.value >= 25) features.push(Feature.PREMIUM_SUPPORT);
        
        return features;
    }

    private calculateLevel(xp: ExperiencePoints): Level {
        // Exponential leveling: level = floor(sqrt(xp / 100))
        const levelValue = Math.floor(Math.sqrt(xp.value / 100));
        return new Level(Math.min(levelValue, 100)); // Cap at level 100
    }

    private calculateNextThreshold(level: Level): ExperiencePoints {
        // XP required for next level: (level + 1)^2 * 100
        const nextLevel = level.value + 1;
        return new ExperiencePoints(nextLevel * nextLevel * 100);
    }

    private calculateLevelXP(level: Level): number {
        // XP required to reach this level: level^2 * 100
        return level.value * level.value * 100;
    }
}

// User Profile Value Object
export class UserProfile {
    constructor(
        public readonly name: string,
        public readonly email: string,
        public readonly avatar: string | null = null,
        public readonly bio: string | null = null,
        public readonly company: string | null = null,
        public readonly location: string | null = null,
        public readonly website: string | null = null,
        public readonly isPublic: boolean = true,
        public readonly createdAt: Date,
        public readonly lastActiveAt: Date
    ) {}

    update(changes: ProfileUpdate): UserProfile {
        return new UserProfile(
            changes.name ?? this.name,
            changes.email ?? this.email,
            changes.avatar ?? this.avatar,
            changes.bio ?? this.bio,
            changes.company ?? this.company,
            changes.location ?? this.location,
            changes.website ?? this.website,
            changes.isPublic ?? this.isPublic,
            this.createdAt,
            new Date() // Update lastActiveAt
        );
    }

    updateLastActive(): UserProfile {
        return new UserProfile(
            this.name,
            this.email,
            this.avatar,
            this.bio,
            this.company,
            this.location,
            this.website,
            this.isPublic,
            this.createdAt,
            new Date()
        );
    }
}

// Activity Record
export abstract class ActivityRecord {
    constructor(
        public readonly id: ActivityId,
        public readonly userId: UserId,
        public readonly timestamp: Date,
        public readonly type: ActivityType
    ) {}

    abstract getDescription(): string;
    abstract getMetadata(): Record<string, any>;
}

export class ExperienceGainedActivity extends ActivityRecord {
    constructor(
        userId: UserId,
        public readonly points: ExperiencePoints,
        public readonly reason: string
    ) {
        super(ActivityId.generate(), userId, new Date(), ActivityType.EXPERIENCE_GAINED);
    }

    getDescription(): string {
        return `Gained ${this.points.value} XP for ${this.reason}`;
    }

    getMetadata(): Record<string, any> {
        return {
            points: this.points.value,
            reason: this.reason
        };
    }
}
```

#### **2. Application Layer**

```typescript
// User Management Service
@Injectable()
export class UserManagementService {
    constructor(
        private readonly userRepository: IUserRepository,
        private readonly passwordService: IPasswordService,
        private readonly eventBus: IEventBus
    ) {}

    async createUser(command: CreateUserCommand): Promise<User> {
        // Validate email uniqueness
        const existingUser = await this.userRepository.findByEmail(command.email);
        if (existingUser) {
            throw new UserAlreadyExistsError(command.email);
        }

        // Create user with initial gamification stats
        const userId = UserId.generate();
        const profile = new UserProfile(
            command.name,
            command.email,
            null, // avatar
            null, // bio
            command.company || null,
            null, // location
            null, // website
            true, // isPublic
            new Date(),
            new Date()
        );

        const gamification = new GamificationStats(
            Level.one(),
            ExperiencePoints.zero(),
            new ExperiencePoints(100), // Level 2 threshold
            WinStreak.zero(),
            0, // totalOptimizations
            []
        );

        const preferences = UserPreferences.default();
        const user = new User(userId, profile, gamification, preferences);

        await this.userRepository.save(user);
        await this.eventBus.publish(new UserCreatedEvent(userId, command.email));

        return user;
    }

    async updateProfile(command: UpdateProfileCommand): Promise<void> {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new UserNotFoundError(command.userId);
        }

        user.updateProfile(command.changes);
        await this.userRepository.save(user);
        await this.eventBus.publish(new ProfileUpdatedEvent(command.userId, command.changes));
    }

    async recordActivity(command: RecordActivityCommand): Promise<void> {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new UserNotFoundError(command.userId);
        }

        // Update last active timestamp
        user.updateProfile({}); // This updates lastActiveAt
        await this.userRepository.save(user);
    }

    async getUserStats(userId: UserId): Promise<UserStatsDto> {
        const user = await this.userRepository.findById(userId);
        if (!user) {
            throw new UserNotFoundError(userId);
        }

        const recentActivities = await this.userRepository.getRecentActivities(userId, 20);
        
        return new UserStatsDto(
            user.gamification.level.value,
            user.gamification.experiencePoints.value,
            user.gamification.nextLevelThreshold.value,
            user.gamification.getProgressToNextLevel(),
            user.gamification.winStreak.value,
            user.gamification.totalOptimizations,
            user.gamification.getUnlockedFeatures(),
            recentActivities
        );
    }
}

// Gamification Service
@Injectable()
export class GamificationService {
    constructor(
        private readonly userRepository: IUserRepository,
        private readonly eventBus: IEventBus
    ) {}

    async awardExperience(command: AwardExperienceCommand): Promise<LevelUpResult> {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new UserNotFoundError(command.userId);
        }

        const levelUpResult = user.gainExperience(command.points, command.reason);
        await this.userRepository.save(user);

        if (levelUpResult.hasLeveledUp()) {
            await this.eventBus.publish(new LevelUpEvent(
                command.userId,
                levelUpResult.oldLevel,
                levelUpResult.newLevel,
                levelUpResult.unlockedFeatures
            ));
        }

        await this.eventBus.publish(new ExperienceGainedEvent(
            command.userId,
            command.points,
            command.reason
        ));

        return levelUpResult;
    }

    async recordOptimizationResult(command: RecordOptimizationCommand): Promise<void> {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new UserNotFoundError(command.userId);
        }

        user.recordOptimization(command.success);
        await this.userRepository.save(user);

        if (command.success) {
            await this.eventBus.publish(new WinStreakIncrementedEvent(
                command.userId,
                user.gamification.winStreak.value
            ));
        } else {
            await this.eventBus.publish(new WinStreakResetEvent(command.userId));
        }
    }

    async calculateLevelProgress(userId: UserId): Promise<LevelProgressDto> {
        const user = await this.userRepository.findById(userId);
        if (!user) {
            throw new UserNotFoundError(userId);
        }

        return new LevelProgressDto(
            user.gamification.level.value,
            user.gamification.experiencePoints.value,
            user.gamification.nextLevelThreshold.value,
            user.gamification.getProgressToNextLevel(),
            user.gamification.getUnlockedFeatures()
        );
    }

    async getLeaderboard(limit: number = 10): Promise<LeaderboardDto[]> {
        const topUsers = await this.userRepository.getTopUsersByLevel(limit);
        
        return topUsers.map((user, index) => new LeaderboardDto(
            index + 1,
            user.id,
            user.profile.name,
            user.profile.avatar,
            user.gamification.level.value,
            user.gamification.experiencePoints.value,
            user.gamification.winStreak.value,
            user.gamification.totalOptimizations
        ));
    }
}

// Authentication Service
@Injectable()
export class AuthService {
    constructor(
        private readonly userRepository: IUserRepository,
        private readonly passwordService: IPasswordService,
        private readonly jwtService: IJWTService,
        private readonly oauthService: IOAuthService
    ) {}

    async authenticate(command: AuthenticateCommand): Promise<AuthResult> {
        const user = await this.userRepository.findByEmail(command.email);
        if (!user) {
            throw new InvalidCredentialsError();
        }

        const isValidPassword = await this.passwordService.verify(
            command.password,
            user.passwordHash
        );
        if (!isValidPassword) {
            throw new InvalidCredentialsError();
        }

        const tokens = await this.jwtService.generateTokens(user.id);
        
        // Update last active
        user.updateProfile({});
        await this.userRepository.save(user);

        return new AuthResult(
            user.id,
            tokens.accessToken,
            tokens.refreshToken,
            tokens.expiresAt
        );
    }

    async refreshToken(command: RefreshTokenCommand): Promise<AuthResult> {
        const payload = await this.jwtService.verifyRefreshToken(command.refreshToken);
        const user = await this.userRepository.findById(new UserId(payload.sub));
        
        if (!user) {
            throw new InvalidTokenError();
        }

        const tokens = await this.jwtService.generateTokens(user.id);
        
        return new AuthResult(
            user.id,
            tokens.accessToken,
            tokens.refreshToken,
            tokens.expiresAt
        );
    }
}
```

#### **3. Infrastructure Layer**

```typescript
// PostgreSQL User Repository
@Injectable()
export class PostgreSQLUserRepository implements IUserRepository {
    constructor(
        private readonly dataSource: DataSource,
        private readonly mapper: UserMapper
    ) {}

    async save(user: User): Promise<void> {
        const queryRunner = this.dataSource.createQueryRunner();
        await queryRunner.connect();
        await queryRunner.startTransaction();

        try {
            // Save user profile
            await queryRunner.manager.upsert(UserEntity, {
                id: user.id.value,
                name: user.profile.name,
                email: user.profile.email,
                avatar: user.profile.avatar,
                bio: user.profile.bio,
                company: user.profile.company,
                location: user.profile.location,
                website: user.profile.website,
                isPublic: user.profile.isPublic,
                createdAt: user.profile.createdAt,
                lastActiveAt: user.profile.lastActiveAt
            }, ['id']);

            // Save gamification stats
            await queryRunner.manager.upsert(GamificationStatsEntity, {
                userId: user.id.value,
                level: user.gamification.level.value,
                experiencePoints: user.gamification.experiencePoints.value,
                nextLevelThreshold: user.gamification.nextLevelThreshold.value,
                winStreak: user.gamification.winStreak.value,
                totalOptimizations: user.gamification.totalOptimizations,
                unlockedAchievements: user.gamification.unlockedAchievements.map(a => a.value)
            }, ['userId']);

            // Save preferences
            await queryRunner.manager.upsert(UserPreferencesEntity, {
                userId: user.id.value,
                theme: user.preferences.theme,
                language: user.preferences.language,
                notifications: user.preferences.notifications,
                privacy: user.preferences.privacy
            }, ['userId']);

            // Save recent activities
            for (const activity of user.activities.slice(-10)) { // Save last 10 activities
                await queryRunner.manager.insert(ActivityRecordEntity, {
                    id: activity.id.value,
                    userId: user.id.value,
                    type: activity.type,
                    description: activity.getDescription(),
                    metadata: activity.getMetadata(),
                    timestamp: activity.timestamp
                });
            }

            await queryRunner.commitTransaction();
        } catch (error) {
            await queryRunner.rollbackTransaction();
            throw error;
        } finally {
            await queryRunner.release();
        }
    }

    async findById(id: UserId): Promise<User | null> {
        const userEntity = await this.dataSource
            .getRepository(UserEntity)
            .findOne({
                where: { id: id.value },
                relations: ['gamificationStats', 'preferences']
            });

        if (!userEntity) return null;

        const recentActivities = await this.dataSource
            .getRepository(ActivityRecordEntity)
            .find({
                where: { userId: id.value },
                order: { timestamp: 'DESC' },
                take: 100
            });

        return this.mapper.toDomain(userEntity, recentActivities);
    }

    async findByEmail(email: string): Promise<User | null> {
        const userEntity = await this.dataSource
            .getRepository(UserEntity)
            .findOne({
                where: { email },
                relations: ['gamificationStats', 'preferences']
            });

        if (!userEntity) return null;

        const recentActivities = await this.dataSource
            .getRepository(ActivityRecordEntity)
            .find({
                where: { userId: userEntity.id },
                order: { timestamp: 'DESC' },
                take: 100
            });

        return this.mapper.toDomain(userEntity, recentActivities);
    }

    async getTopUsersByLevel(limit: number): Promise<User[]> {
        const userEntities = await this.dataSource
            .getRepository(UserEntity)
            .createQueryBuilder('user')
            .leftJoinAndSelect('user.gamificationStats', 'stats')
            .leftJoinAndSelect('user.preferences', 'preferences')
            .where('user.isPublic = :isPublic', { isPublic: true })
            .orderBy('stats.level', 'DESC')
            .addOrderBy('stats.experiencePoints', 'DESC')
            .limit(limit)
            .getMany();

        return Promise.all(userEntities.map(async entity => {
            const activities = await this.dataSource
                .getRepository(ActivityRecordEntity)
                .find({
                    where: { userId: entity.id },
                    order: { timestamp: 'DESC' },
                    take: 10
                });
            return this.mapper.toDomain(entity, activities);
        }));
    }
}

// Redis Cache Service
@Injectable()
export class UserCacheService {
    constructor(private readonly redis: Redis) {}

    async cacheUser(user: User, ttl: number = 3600): Promise<void> {
        const cacheKey = `user:${user.id.value}`;
        const userData = {
            id: user.id.value,
            name: user.profile.name,
            email: user.profile.email,
            level: user.gamification.level.value,
            xp: user.gamification.experiencePoints.value,
            lastActive: user.profile.lastActiveAt.toISOString()
        };

        await this.redis.setex(cacheKey, ttl, JSON.stringify(userData));
    }

    async getCachedUser(userId: UserId): Promise<CachedUserData | null> {
        const cacheKey = `user:${userId.value}`;
        const data = await this.redis.get(cacheKey);
        
        return data ? JSON.parse(data) : null;
    }

    async invalidateUser(userId: UserId): Promise<void> {
        const cacheKey = `user:${userId.value}`;
        await this.redis.del(cacheKey);
    }
}
```

---

## 📊 **Database Schema**

### **PostgreSQL Tables**

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    avatar VARCHAR(500),
    bio TEXT,
    company VARCHAR(255),
    location VARCHAR(255),
    website VARCHAR(500),
    is_public BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_last_active ON users(last_active_at DESC);

-- Gamification Stats
CREATE TABLE gamification_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    level INTEGER NOT NULL DEFAULT 1,
    experience_points INTEGER NOT NULL DEFAULT 0,
    next_level_threshold INTEGER NOT NULL DEFAULT 100,
    win_streak INTEGER NOT NULL DEFAULT 0,
    total_optimizations INTEGER NOT NULL DEFAULT 0,
    unlocked_achievements UUID[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_gamification_level ON gamification_stats(level DESC);
CREATE INDEX idx_gamification_xp ON gamification_stats(experience_points DESC);
CREATE INDEX idx_gamification_streak ON gamification_stats(win_streak DESC);

-- User Preferences
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme preference_theme DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    notifications JSONB DEFAULT '{}',
    privacy JSONB DEFAULT '{}',
    dashboard_layout JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE preference_theme AS ENUM ('light', 'dark', 'auto');

-- Activity Records
CREATE TABLE activity_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type activity_type NOT NULL,
    description TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TYPE activity_type AS ENUM (
    'profile_updated',
    'experience_gained',
    'level_up',
    'win_streak_incremented',
    'win_streak_reset',
    'optimization_completed',
    'achievement_unlocked',
    'preferences_updated',
    'login',
    'logout'
);

CREATE INDEX idx_activity_records_user_id ON activity_records(user_id);
CREATE INDEX idx_activity_records_type ON activity_records(type);
CREATE INDEX idx_activity_records_timestamp ON activity_records(timestamp DESC);

-- User Sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    refresh_token_hash VARCHAR(64) NOT NULL UNIQUE,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    last_accessed TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(token_hash);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

-- OAuth Connections
CREATE TABLE oauth_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider oauth_provider NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    provider_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(provider, provider_user_id)
);

CREATE TYPE oauth_provider AS ENUM ('google', 'github', 'microsoft', 'apple');

CREATE INDEX idx_oauth_connections_user_id ON oauth_connections(user_id);
CREATE INDEX idx_oauth_connections_provider ON oauth_connections(provider, provider_user_id);

-- Password Reset Tokens
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token_hash);
CREATE INDEX idx_password_reset_tokens_expires ON password_reset_tokens(expires_at);
```

---

## 🔌 **API Specifications**

### **REST API Endpoints**

```yaml
# OpenAPI 3.0 Specification
openapi: 3.0.0
info:
  title: User Management Module API
  version: 1.0.0

paths:
  /users:
    post:
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  maxLength: 255
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
                  pattern: '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
                company:
                  type: string
                  maxLength: 255
              required: [name, email, password]
      responses:
        201:
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        400:
          description: Invalid request data
        409:
          description: User with email already exists

    get:
      summary: List users (admin only)
      security:
        - bearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: offset
          in: query
          schema:
            type: integer
            minimum: 0
            default: 0
        - name: search
          in: query
          schema:
            type: string
      responses:
        200:
          description: List of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  total:
                    type: integer

  /users/{id}:
    get:
      summary: Get user profile
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: User profile
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserProfile'
        404:
          description: User not found

    put:
      summary: Update user profile
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateProfileRequest'
      responses:
        200:
          description: Profile updated
        404:
          description: User not found

  /users/{id}/stats:
    get:
      summary: Get user gamification stats
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: User stats
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserStats'

  /users/{id}/experience:
    post:
      summary: Award experience points (internal)
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                points:
                  type: integer
                  minimum: 1
                  maximum: 1000
                reason:
                  type: string
                  maxLength: 255
              required: [points, reason]
      responses:
        200:
          description: Experience awarded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LevelUpResult'

  /users/{id}/preferences:
    get:
      summary: Get user preferences
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: User preferences
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserPreferences'

    put:
      summary: Update user preferences
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdatePreferencesRequest'
      responses:
        200:
          description: Preferences updated

  /users/{id}/activities:
    get:
      summary: Get user activity history
      security:
        - bearerAuth: []
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
            minimum: 1
            maximum: 100
            default: 20
        - name: type
          in: query
          schema:
            type: string
            enum: [profile_updated, experience_gained, level_up, optimization_completed]
      responses:
        200:
          description: Activity history
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ActivityRecord'

  /leaderboard:
    get:
      summary: Get user leaderboard
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
        - name: timeframe
          in: query
          schema:
            type: string
            enum: [daily, weekly, monthly, all_time]
            default: all_time
      responses:
        200:
          description: Leaderboard
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/LeaderboardEntry'

  /auth/login:
    post:
      summary: User login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
              required: [email, password]
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResult'
        401:
          description: Invalid credentials

  /auth/refresh:
    post:
      summary: Refresh access token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                refreshToken:
                  type: string
              required: [refreshToken]
      responses:
        200:
          description: Token refreshed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResult'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        email:
          type: string
        avatar:
          type: string
        bio:
          type: string
        company:
          type: string
        location:
          type: string
        website:
          type: string
        isPublic:
          type: boolean
        createdAt:
          type: string
          format: date-time
        lastActiveAt:
          type: string
          format: date-time

    UserStats:
      type: object
      properties:
        level:
          type: integer
        experiencePoints:
          type: integer
        nextLevelThreshold:
          type: integer
        progressToNextLevel:
          type: number
          minimum: 0
          maximum: 1
        winStreak:
          type: integer
        totalOptimizations:
          type: integer
        unlockedFeatures:
          type: array
          items:
            type: string

    LevelUpResult:
      type: object
      properties:
        hasLeveledUp:
          type: boolean
        oldLevel:
          type: integer
        newLevel:
          type: integer
        unlockedFeatures:
          type: array
          items:
            type: string
```

---

## 🧪 **Testing Requirements**

### **Unit Tests** (TDD Cycle 10)

```typescript
// TDD Cycle 10: User Management & Gamification
describe('UserManagementService', () => {
    let service: UserManagementService;
    let mockRepository: jest.Mocked<IUserRepository>;

    beforeEach(() => {
        mockRepository = createMockUserRepository();
        service = new UserManagementService(mockRepository);
    });

    describe('createUser', () => {
        it('should create user with initial gamification stats', async () => {
            // RED: Test fails initially
            const command = new CreateUserCommand(
                'John Developer',
                'john@company.com',
                'SecurePass123!'
            );

            mockRepository.findByEmail.mockResolvedValue(null);

            const user = await service.createUser(command);

            expect(user.profile.name).toBe('John Developer');
            expect(user.profile.email).toBe('john@company.com');
            expect(user.gamification.level.value).toBe(1);
            expect(user.gamification.experiencePoints.value).toBe(0);
            expect(user.gamification.nextLevelThreshold.value).toBe(100);
            expect(user.gamification.winStreak.value).toBe(0);
            expect(user.gamification.totalOptimizations).toBe(0);
            expect(user.gamification.unlockedAchievements).toHaveLength(0);
        });

        it('should throw error when email already exists', async () => {
            // RED: Test fails initially
            const command = new CreateUserCommand(
                'John Developer',
                'existing@company.com',
                'SecurePass123!'
            );

            const existingUser = createMockUser();
            mockRepository.findByEmail.mockResolvedValue(existingUser);

            await expect(service.createUser(command))
                .rejects.toThrow(UserAlreadyExistsError);
        });
    });
});

describe('GamificationService', () => {
    describe('awardExperience', () => {
        it('should level up user when threshold reached', async () => {
            // RED: Test fails initially
            const user = createMockUser({
                level: 1,
                experiencePoints: 95, // Close to level 2 threshold (100)
                nextLevelThreshold: 100
            });

            mockRepository.findById.mockResolvedValue(user);

            const command = new AwardExperienceCommand(
                user.id,
                new ExperiencePoints(10),
                'Test completion'
            );

            const result = await service.awardExperience(command);

            expect(result.hasLeveledUp()).toBe(true);
            expect(result.newLevel.value).toBe(2);
            expect(user.gamification.experiencePoints.value).toBe(105);
        });

        it('should not level up when threshold not reached', async () => {
            // RED: Test fails initially
            const user = createMockUser({
                level: 1,
                experiencePoints: 50,
                nextLevelThreshold: 100
            });

            const command = new AwardExperienceCommand(
                user.id,
                new ExperiencePoints(25),
                'Test completion'
            );

            const result = await service.awardExperience(command);

            expect(result.hasLeveledUp()).toBe(false);
            expect(user.gamification.level.value).toBe(1);
            expect(user.gamification.experiencePoints.value).toBe(75);
        });
    });
});

describe('User', () => {
    describe('recordOptimization', () => {
        it('should increment win streak on success', () => {
            // RED: Test fails initially
            const user = createMockUser({
                winStreak: 3,
                totalOptimizations: 10
            });

            user.recordOptimization(true);

            expect(user.gamification.winStreak.value).toBe(4);
            expect(user.gamification.totalOptimizations).toBe(11);
        });

        it('should reset win streak on failure', () => {
            // RED: Test fails initially
            const user = createMockUser({
                winStreak: 5,
                totalOptimizations: 10
            });

            user.recordOptimization(false);

            expect(user.gamification.winStreak.value).toBe(0);
            expect(user.gamification.totalOptimizations).toBe(11);
        });
    });
});
```

### **Integration Tests**

```typescript
describe('User Management Integration', () => {
    let app: INestApplication;
    let repository: IUserRepository;

    beforeAll(async () => {
        const moduleRef = await Test.createTestingModule({
            imports: [UserManagementModule],
        }).compile();

        app = moduleRef.createNestApplication();
        repository = app.get(IUserRepository);
        await app.init();
    });

    describe('User Lifecycle', () => {
        it('should create, authenticate, and track user activities', async () => {
            // Create user
            const createResponse = await request(app.getHttpServer())
                .post('/users')
                .send({
                    name: 'Integration Test User',
                    email: 'integration@test.com',
                    password: 'SecurePass123!'
                });

            expect(createResponse.status).toBe(201);
            const userId = createResponse.body.id;

            // Authenticate user
            const loginResponse = await request(app.getHttpServer())
                .post('/auth/login')
                .send({
                    email: 'integration@test.com',
                    password: 'SecurePass123!'
                });

            expect(loginResponse.status).toBe(200);
            const token = loginResponse.body.accessToken;

            // Get user stats
            const statsResponse = await request(app.getHttpServer())
                .get(`/users/${userId}/stats`)
                .set('Authorization', `Bearer ${token}`);

            expect(statsResponse.status).toBe(200);
            expect(statsResponse.body.level).toBe(1);
            expect(statsResponse.body.experiencePoints).toBe(0);

            // Award experience
            const xpResponse = await request(app.getHttpServer())
                .post(`/users/${userId}/experience`)
                .set('Authorization', `Bearer ${token}`)
                .send({
                    points: 150,
                    reason: 'Integration test'
                });

            expect(xpResponse.status).toBe(200);
            expect(xpResponse.body.hasLeveledUp).toBe(true);
            expect(xpResponse.body.newLevel).toBe(2);
        });
    });
});
```

---

## 🚀 **Deployment Requirements**

### **Environment Configuration**

```bash
# .env.production
NODE_ENV=production
PORT=3000

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/selfrag_users
DATABASE_SSL=true
DATABASE_POOL_SIZE=20

# Authentication
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRES_IN=15m
REFRESH_TOKEN_EXPIRES_IN=7d
BCRYPT_ROUNDS=12

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@selfrag.com
SMTP_PASS=your-email-password

# Caching
REDIS_URL=redis://redis:6379
USER_CACHE_TTL=3600

# Rate Limiting
LOGIN_ATTEMPTS_LIMIT=5
LOGIN_ATTEMPTS_WINDOW=900

# Monitoring
LOG_LEVEL=info
METRICS_PORT=9090
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Create users with initial gamification stats (Level 1, 0 XP)
- [ ] Award experience points and trigger level-ups
- [ ] Track win streaks and reset on failures
- [ ] Authenticate users with email/password and OAuth
- [ ] Store and retrieve user preferences
- [ ] Generate user activity logs and history

### **Performance Acceptance**
- [ ] User profile retrieval < 100ms for 95% of requests
- [ ] Support 10,000+ concurrent active users
- [ ] Authentication response time < 200ms
- [ ] XP calculation and updates < 50ms

### **Security Acceptance**
- [ ] Password encryption with bcrypt (12+ rounds)
- [ ] Secure JWT token management
- [ ] Protection against brute force attacks
- [ ] GDPR-compliant data handling

This User Management Module provides the foundation for user-driven features and gamification mechanics across the entire Self-Improving RAG Platform. 