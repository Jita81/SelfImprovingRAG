# Notification Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: Notification  
**Size Estimate**: ~24k tokens  
**Priority**: 2 (Engagement)  
**TDD Cycles**: 13  
**Branch**: `module/notification`  
**Cursor Window**: #6  
**Dependencies**: Orchestrator, User Management Modules  

### **Purpose**
The Notification Module handles real-time notifications, user preferences, and multi-channel delivery. It provides instant feedback for optimization results, achievements, and system events to maintain user engagement and awareness.

---

## 🎯 **Functional Requirements**

### **FR-1: Notification Management** (TDD Cycle 13)
- **FR-1.1**: Create notifications with type, content, priority, and targeting
- **FR-1.2**: Support different notification types (success, warning, info, error)
- **FR-1.3**: Handle notification templating with dynamic content
- **FR-1.4**: Queue notifications for batch delivery and rate limiting
- **FR-1.5**: Track notification delivery status and read receipts
- **FR-1.6**: Support notification expiration and cleanup
- **FR-1.7**: Handle notification grouping and deduplication

### **FR-2: Real-time Delivery**
- **FR-2.1**: Deliver notifications via WebSocket connections
- **FR-2.2**: Support Server-Sent Events (SSE) as fallback
- **FR-2.3**: Handle connection management and reconnection
- **FR-2.4**: Maintain notification order and delivery guarantees
- **FR-2.5**: Support selective notification subscriptions
- **FR-2.6**: Handle offline users with notification persistence

### **FR-3: Multi-channel Support**
- **FR-3.1**: Support in-app notifications with rich content
- **FR-3.2**: Send email notifications for important events
- **FR-3.3**: Support push notifications for mobile devices
- **FR-3.4**: Integration with Slack/Teams for team notifications
- **FR-3.5**: SMS notifications for critical alerts (optional)
- **FR-3.6**: Support webhook notifications for external systems

### **FR-4: User Preferences**
- **FR-4.1**: Allow users to configure notification preferences per type
- **FR-4.2**: Support "Do Not Disturb" modes and quiet hours
- **FR-4.3**: Enable/disable specific notification channels
- **FR-4.4**: Set notification frequency and batching preferences
- **FR-4.5**: Support notification filtering based on criteria
- **FR-4.6**: Handle global notification settings and overrides

### **FR-5: Notification Analytics**
- **FR-5.1**: Track notification delivery rates and failures
- **FR-5.2**: Monitor user engagement with notifications
- **FR-5.3**: Analyze notification effectiveness and conversion
- **FR-5.4**: Support A/B testing for notification content
- **FR-5.5**: Generate reports on notification performance
- **FR-5.6**: Identify and handle notification fatigue

---

## 🏗️ **Technical Architecture**

```typescript
// Domain Layer
export class Notification {
    constructor(
        public readonly id: NotificationId,
        public readonly userId: UserId,
        public readonly type: NotificationType,
        public readonly content: NotificationContent,
        public readonly priority: NotificationPriority,
        private status: DeliveryStatus = DeliveryStatus.PENDING,
        private channels: DeliveryChannel[] = [],
        private readonly createdAt: Date = new Date(),
        private expiresAt?: Date,
        private deliveredAt?: Date
    ) {}

    static create(data: CreateNotificationData): Notification {
        return new Notification(
            NotificationId.generate(),
            data.userId,
            data.type,
            data.content,
            data.priority,
            DeliveryStatus.PENDING,
            data.channels,
            new Date(),
            data.expiresAt
        );
    }

    deliver(channel: DeliveryChannel): DeliveryResult {
        if (this.isExpired()) {
            return DeliveryResult.expired(this.id, channel);
        }

        if (!this.channels.includes(channel)) {
            return DeliveryResult.channelNotAllowed(this.id, channel);
        }

        this.status = DeliveryStatus.DELIVERED;
        this.deliveredAt = new Date();

        return DeliveryResult.success(this.id, channel, this.deliveredAt);
    }

    markAsRead(): void {
        if (this.status === DeliveryStatus.DELIVERED) {
            this.status = DeliveryStatus.READ;
        }
    }

    isExpired(): boolean {
        return this.expiresAt ? new Date() > this.expiresAt : false;
    }

    isPending(): boolean {
        return this.status === DeliveryStatus.PENDING;
    }

    canBeDeliveredTo(channel: DeliveryChannel): boolean {
        return this.channels.includes(channel) && !this.isExpired();
    }
}

export class NotificationPreferences {
    constructor(
        public readonly userId: UserId,
        private channelPreferences: Map<NotificationType, DeliveryChannel[]>,
        private quietHours: QuietHours | null = null,
        private isDoNotDisturb: boolean = false,
        private batchingEnabled: boolean = true,
        private readonly updatedAt: Date = new Date()
    ) {}

    static defaultFor(userId: UserId): NotificationPreferences {
        const defaults = new Map<NotificationType, DeliveryChannel[]>();
        defaults.set(NotificationType.OPTIMIZATION_COMPLETE, [DeliveryChannel.IN_APP, DeliveryChannel.EMAIL]);
        defaults.set(NotificationType.ACHIEVEMENT_UNLOCKED, [DeliveryChannel.IN_APP]);
        defaults.set(NotificationType.LEVEL_UP, [DeliveryChannel.IN_APP]);
        defaults.set(NotificationType.BET_RESOLVED, [DeliveryChannel.IN_APP]);
        defaults.set(NotificationType.SYSTEM_ALERT, [DeliveryChannel.IN_APP, DeliveryChannel.EMAIL]);

        return new NotificationPreferences(userId, defaults);
    }

    allowsNotification(type: NotificationType, channel: DeliveryChannel): boolean {
        if (this.isDoNotDisturb && channel !== DeliveryChannel.SYSTEM) {
            return false;
        }

        if (this.quietHours?.isActive()) {
            return channel === DeliveryChannel.IN_APP; // Only in-app during quiet hours
        }

        const allowedChannels = this.channelPreferences.get(type) || [];
        return allowedChannels.includes(channel);
    }

    updateChannelPreference(type: NotificationType, channels: DeliveryChannel[]): void {
        this.channelPreferences.set(type, channels);
    }

    setQuietHours(startTime: string, endTime: string, timezone: string): void {
        this.quietHours = new QuietHours(startTime, endTime, timezone);
    }

    enableDoNotDisturb(): void {
        this.isDoNotDisturb = true;
    }

    disableDoNotDisturb(): void {
        this.isDoNotDisturb = false;
    }
}

export class NotificationTemplate {
    constructor(
        public readonly id: TemplateId,
        public readonly type: NotificationType,
        public readonly name: string,
        private subject: string,
        private content: string,
        private variables: TemplateVariable[],
        private readonly createdAt: Date = new Date()
    ) {}

    render(data: TemplateData): RenderedNotification {
        let renderedSubject = this.subject;
        let renderedContent = this.content;

        this.variables.forEach(variable => {
            const value = data.get(variable.name) || variable.defaultValue;
            const placeholder = `{{${variable.name}}}`;
            
            renderedSubject = renderedSubject.replace(new RegExp(placeholder, 'g'), value);
            renderedContent = renderedContent.replace(new RegExp(placeholder, 'g'), value);
        });

        return new RenderedNotification(
            renderedSubject,
            renderedContent,
            this.type
        );
    }

    validate(): ValidationResult {
        const errors: string[] = [];

        if (!this.subject.trim()) {
            errors.push('Subject cannot be empty');
        }

        if (!this.content.trim()) {
            errors.push('Content cannot be empty');
        }

        // Check for undefined variables
        const subjectVars = this.extractVariables(this.subject);
        const contentVars = this.extractVariables(this.content);
        const definedVars = this.variables.map(v => v.name);
        
        const undefinedVars = [...subjectVars, ...contentVars].filter(
            v => !definedVars.includes(v)
        );

        if (undefinedVars.length > 0) {
            errors.push(`Undefined variables: ${undefinedVars.join(', ')}`);
        }

        return new ValidationResult(errors.length === 0, errors);
    }

    private extractVariables(text: string): string[] {
        const matches = text.match(/\{\{(\w+)\}\}/g);
        return matches ? matches.map(m => m.slice(2, -2)) : [];
    }
}

// Application Services
@Injectable()
export class NotificationService {
    constructor(
        private readonly repository: INotificationRepository,
        private readonly preferencesRepository: INotificationPreferencesRepository,
        private readonly deliveryService: IDeliveryService,
        private readonly templateService: ITemplateService,
        private readonly eventBus: IEventBus
    ) {}

    async sendNotification(command: SendNotificationCommand): Promise<Notification> {
        // Get user preferences
        const preferences = await this.preferencesRepository.findByUserId(command.userId);
        
        // Check if notification is allowed
        const allowedChannels = command.channels.filter(channel =>
            preferences.allowsNotification(command.type, channel)
        );

        if (allowedChannels.length === 0) {
            throw new NotificationNotAllowedError(command.userId, command.type);
        }

        // Create notification
        const notification = Notification.create({
            userId: command.userId,
            type: command.type,
            content: command.content,
            priority: command.priority,
            channels: allowedChannels,
            expiresAt: command.expiresAt
        });

        // Save to repository
        await this.repository.save(notification);

        // Queue for delivery
        await this.deliveryService.queueNotification(notification);

        // Publish event
        await this.eventBus.publish(new NotificationCreatedEvent(
            notification.id,
            notification.userId,
            notification.type
        ));

        return notification;
    }

    async sendTemplatedNotification(command: SendTemplatedNotificationCommand): Promise<Notification> {
        // Get template
        const template = await this.templateService.getTemplate(command.templateId);
        if (!template) {
            throw new TemplateNotFoundError(command.templateId);
        }

        // Render template
        const rendered = template.render(command.templateData);

        // Send notification
        return this.sendNotification(new SendNotificationCommand(
            command.userId,
            command.type,
            new NotificationContent(rendered.subject, rendered.content),
            command.priority,
            command.channels,
            command.expiresAt
        ));
    }

    async markAsRead(command: MarkAsReadCommand): Promise<void> {
        const notification = await this.repository.findById(command.notificationId);
        if (!notification) {
            throw new NotificationNotFoundError(command.notificationId);
        }

        if (notification.userId.value !== command.userId.value) {
            throw new UnauthorizedNotificationAccessError(command.notificationId, command.userId);
        }

        notification.markAsRead();
        await this.repository.save(notification);

        await this.eventBus.publish(new NotificationReadEvent(
            notification.id,
            notification.userId
        ));
    }

    async getUserNotifications(query: GetNotificationsQuery): Promise<NotificationList> {
        const notifications = await this.repository.findByUserId(
            query.userId,
            query.limit,
            query.offset,
            query.includeRead
        );

        const unreadCount = await this.repository.countUnreadByUserId(query.userId);

        return new NotificationList(
            notifications,
            unreadCount,
            query.limit,
            query.offset
        );
    }

    async updatePreferences(command: UpdatePreferencesCommand): Promise<void> {
        let preferences = await this.preferencesRepository.findByUserId(command.userId);
        
        if (!preferences) {
            preferences = NotificationPreferences.defaultFor(command.userId);
        }

        // Apply updates
        if (command.channelPreferences) {
            Object.entries(command.channelPreferences).forEach(([type, channels]) => {
                preferences.updateChannelPreference(type as NotificationType, channels);
            });
        }

        if (command.quietHours) {
            preferences.setQuietHours(
                command.quietHours.startTime,
                command.quietHours.endTime,
                command.quietHours.timezone
            );
        }

        if (command.doNotDisturb !== undefined) {
            if (command.doNotDisturb) {
                preferences.enableDoNotDisturb();
            } else {
                preferences.disableDoNotDisturb();
            }
        }

        await this.preferencesRepository.save(preferences);

        await this.eventBus.publish(new NotificationPreferencesUpdatedEvent(
            command.userId,
            preferences
        ));
    }
}

@Injectable()
export class DeliveryService {
    constructor(
        private readonly webSocketChannel: IWebSocketChannel,
        private readonly emailChannel: IEmailChannel,
        private readonly pushChannel: IPushNotificationChannel,
        private readonly queue: INotificationQueue,
        private readonly rateLimiter: IRateLimiter
    ) {}

    async queueNotification(notification: Notification): Promise<void> {
        // Add to delivery queue with appropriate priority
        const queueItem = new QueuedNotification(
            notification,
            this.calculateDeliveryDelay(notification.priority),
            new Date()
        );

        await this.queue.enqueue(queueItem);
    }

    async deliverNotification(notification: Notification): Promise<DeliveryResults> {
        const results: DeliveryResult[] = [];

        for (const channel of notification.channels) {
            // Check rate limits
            const canDeliver = await this.rateLimiter.checkLimit(
                notification.userId,
                channel
            );

            if (!canDeliver) {
                results.push(DeliveryResult.rateLimited(notification.id, channel));
                continue;
            }

            try {
                const result = await this.deliverToChannel(notification, channel);
                results.push(result);
            } catch (error) {
                results.push(DeliveryResult.failed(notification.id, channel, error.message));
            }
        }

        return new DeliveryResults(notification.id, results);
    }

    private async deliverToChannel(
        notification: Notification,
        channel: DeliveryChannel
    ): Promise<DeliveryResult> {
        switch (channel) {
            case DeliveryChannel.IN_APP:
                return this.webSocketChannel.deliver(notification);
            
            case DeliveryChannel.EMAIL:
                return this.emailChannel.deliver(notification);
            
            case DeliveryChannel.PUSH:
                return this.pushChannel.deliver(notification);
            
            default:
                throw new UnsupportedChannelError(channel);
        }
    }

    private calculateDeliveryDelay(priority: NotificationPriority): number {
        switch (priority) {
            case NotificationPriority.CRITICAL:
                return 0; // Immediate
            case NotificationPriority.HIGH:
                return 1000; // 1 second
            case NotificationPriority.NORMAL:
                return 5000; // 5 seconds
            case NotificationPriority.LOW:
                return 30000; // 30 seconds
            default:
                return 5000;
        }
    }
}

// Real-time WebSocket Channel
@Injectable()
export class WebSocketChannel implements IWebSocketChannel {
    constructor(
        private readonly connectionManager: IWebSocketConnectionManager,
        private readonly logger: ILogger
    ) {}

    async deliver(notification: Notification): Promise<DeliveryResult> {
        const connection = this.connectionManager.getConnection(notification.userId);
        
        if (!connection || !connection.isActive()) {
            // Store for later delivery when user comes online
            await this.storeForOfflineDelivery(notification);
            return DeliveryResult.deferred(notification.id, DeliveryChannel.IN_APP);
        }

        try {
            const message = this.formatWebSocketMessage(notification);
            await connection.send(message);
            
            const result = notification.deliver(DeliveryChannel.IN_APP);
            this.logger.info(`Notification ${notification.id.value} delivered via WebSocket`);
            
            return result;
        } catch (error) {
            this.logger.error(`WebSocket delivery failed for ${notification.id.value}:`, error);
            throw new DeliveryFailedError(notification.id, DeliveryChannel.IN_APP, error.message);
        }
    }

    private formatWebSocketMessage(notification: Notification): WebSocketMessage {
        return {
            type: 'notification',
            data: {
                id: notification.id.value,
                type: notification.type,
                title: notification.content.title,
                message: notification.content.message,
                priority: notification.priority,
                timestamp: notification.createdAt.toISOString()
            }
        };
    }

    private async storeForOfflineDelivery(notification: Notification): Promise<void> {
        // Implementation for storing notifications for offline users
        // These will be delivered when the user next connects
    }
}
```

---

## 📊 **Database Schema**

```sql
-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    priority notification_priority NOT NULL DEFAULT 'normal',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    channels delivery_channel[] NOT NULL,
    status delivery_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TYPE notification_type AS ENUM (
    'optimization_complete',
    'optimization_failed', 
    'achievement_unlocked',
    'level_up',
    'bet_resolved',
    'system_alert',
    'maintenance',
    'welcome',
    'reminder'
);

CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'critical');
CREATE TYPE delivery_channel AS ENUM ('in_app', 'email', 'push', 'slack', 'sms', 'webhook');
CREATE TYPE delivery_status AS ENUM ('pending', 'delivered', 'read', 'failed', 'expired');

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_type ON notifications(type);

-- Notification Preferences
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    channel_preferences JSONB NOT NULL DEFAULT '{}',
    quiet_hours JSONB,
    do_not_disturb BOOLEAN DEFAULT false,
    batching_enabled BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notification Templates
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type notification_type NOT NULL,
    subject_template TEXT NOT NULL,
    content_template TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Delivery Logs
CREATE TABLE notification_delivery_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID REFERENCES notifications(id) ON DELETE CASCADE,
    channel delivery_channel NOT NULL,
    status delivery_status NOT NULL,
    error_message TEXT,
    attempted_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP
);

CREATE INDEX idx_delivery_logs_notification_id ON notification_delivery_logs(notification_id);
CREATE INDEX idx_delivery_logs_status ON notification_delivery_logs(status);

-- WebSocket Connections
CREATE TABLE websocket_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    connection_id VARCHAR(255) NOT NULL UNIQUE,
    connected_at TIMESTAMP DEFAULT NOW(),
    last_ping TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_websocket_connections_user_id ON websocket_connections(user_id);
CREATE INDEX idx_websocket_connections_active ON websocket_connections(is_active) WHERE is_active = true;
```

---

## 🔌 **API Specifications**

```yaml
paths:
  /notifications:
    get:
      summary: Get user notifications
      security:
        - bearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: includeRead
          in: query
          schema:
            type: boolean
            default: false
      responses:
        200:
          description: Notifications list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotificationList'

    post:
      summary: Send notification (admin)
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SendNotificationRequest'
      responses:
        201:
          description: Notification sent

  /notifications/{id}/read:
    post:
      summary: Mark notification as read
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
          description: Notification marked as read

  /notifications/preferences:
    get:
      summary: Get notification preferences
      security:
        - bearerAuth: []
      responses:
        200:
          description: User preferences
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotificationPreferences'

    put:
      summary: Update notification preferences
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdatePreferencesRequest'
      responses:
        200:
          description: Preferences updated

  /notifications/stream:
    get:
      summary: WebSocket endpoint for real-time notifications
      description: Upgrade to WebSocket for real-time notification delivery

components:
  schemas:
    NotificationList:
      type: object
      properties:
        notifications:
          type: array
          items:
            $ref: '#/components/schemas/Notification'
        unreadCount:
          type: integer
        total:
          type: integer

    Notification:
      type: object
      properties:
        id:
          type: string
          format: uuid
        type:
          type: string
        priority:
          type: string
        title:
          type: string
        message:
          type: string
        createdAt:
          type: string
          format: date-time
        readAt:
          type: string
          format: date-time
        
    NotificationPreferences:
      type: object
      properties:
        channelPreferences:
          type: object
        quietHours:
          type: object
        doNotDisturb:
          type: boolean
        batchingEnabled:
          type: boolean
```

---

## 🧪 **Testing Requirements**

### **Unit Tests** (TDD Cycle 13)

```typescript
// TDD Cycle 13: Real-time Notifications
describe('NotificationService', () => {
    describe('sendNotification', () => {
        it('should send notification when user allows channel', async () => {
            // RED: Test fails initially
            const userId = UserId.generate();
            const preferences = createMockPreferences(userId, {
                [NotificationType.OPTIMIZATION_COMPLETE]: [DeliveryChannel.IN_APP, DeliveryChannel.EMAIL]
            });
            
            mockPreferencesRepository.findByUserId.mockResolvedValue(preferences);

            const command = new SendNotificationCommand(
                userId,
                NotificationType.OPTIMIZATION_COMPLETE,
                new NotificationContent('Success!', 'Your optimization completed successfully'),
                NotificationPriority.NORMAL,
                [DeliveryChannel.IN_APP, DeliveryChannel.EMAIL]
            );

            const notification = await service.sendNotification(command);

            expect(notification.userId).toBe(userId);
            expect(notification.channels).toEqual([DeliveryChannel.IN_APP, DeliveryChannel.EMAIL]);
            expect(mockRepository.save).toHaveBeenCalledWith(notification);
            expect(mockDeliveryService.queueNotification).toHaveBeenCalledWith(notification);
        });

        it('should filter disallowed channels', async () => {
            // RED: Test fails initially
            const userId = UserId.generate();
            const preferences = createMockPreferences(userId, {
                [NotificationType.OPTIMIZATION_COMPLETE]: [DeliveryChannel.IN_APP] // Only in-app allowed
            });
            
            mockPreferencesRepository.findByUserId.mockResolvedValue(preferences);

            const command = new SendNotificationCommand(
                userId,
                NotificationType.OPTIMIZATION_COMPLETE,
                new NotificationContent('Success!', 'Your optimization completed'),
                NotificationPriority.NORMAL,
                [DeliveryChannel.IN_APP, DeliveryChannel.EMAIL] // Email not allowed
            );

            const notification = await service.sendNotification(command);

            expect(notification.channels).toEqual([DeliveryChannel.IN_APP]); // Only allowed channel
        });
    });

    describe('markAsRead', () => {
        it('should mark notification as read', async () => {
            // RED: Test fails initially
            const notification = createMockNotification({
                status: DeliveryStatus.DELIVERED
            });
            
            mockRepository.findById.mockResolvedValue(notification);

            const command = new MarkAsReadCommand(notification.id, notification.userId);
            await service.markAsRead(command);

            expect(notification.status).toBe(DeliveryStatus.READ);
            expect(mockRepository.save).toHaveBeenCalledWith(notification);
        });
    });
});

describe('NotificationPreferences', () => {
    describe('allowsNotification', () => {
        it('should allow notification for configured channels', () => {
            // RED: Test fails initially
            const preferences = NotificationPreferences.defaultFor(UserId.generate());

            const allows = preferences.allowsNotification(
                NotificationType.OPTIMIZATION_COMPLETE,
                DeliveryChannel.IN_APP
            );

            expect(allows).toBe(true);
        });

        it('should block notifications during quiet hours', () => {
            // RED: Test fails initially
            const preferences = NotificationPreferences.defaultFor(UserId.generate());
            preferences.setQuietHours('22:00', '08:00', 'UTC');

            // Mock current time to be during quiet hours
            jest.useFakeTimers().setSystemTime(new Date('2024-01-01T23:00:00Z'));

            const allows = preferences.allowsNotification(
                NotificationType.OPTIMIZATION_COMPLETE,
                DeliveryChannel.EMAIL
            );

            expect(allows).toBe(false);
            
            jest.useRealTimers();
        });
    });
});

describe('WebSocketChannel', () => {
    describe('deliver', () => {
        it('should deliver notification via active WebSocket', async () => {
            // RED: Test fails initially
            const notification = createMockNotification();
            const mockConnection = createMockWebSocketConnection(true); // active
            
            mockConnectionManager.getConnection.mockReturnValue(mockConnection);

            const result = await channel.deliver(notification);

            expect(result.isSuccess()).toBe(true);
            expect(mockConnection.send).toHaveBeenCalled();
        });

        it('should defer delivery for offline user', async () => {
            // RED: Test fails initially
            const notification = createMockNotification();
            
            mockConnectionManager.getConnection.mockReturnValue(null); // offline

            const result = await channel.deliver(notification);

            expect(result.isDeferred()).toBe(true);
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
DATABASE_URL=postgresql://user:password@postgres:5432/selfrag_notifications

# WebSocket
WEBSOCKET_PORT=3001
WEBSOCKET_HEARTBEAT_INTERVAL=30000
MAX_WEBSOCKET_CONNECTIONS=10000

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@selfrag.com
SMTP_PASS=your-email-password
FROM_EMAIL=SelfRAG Platform <notifications@selfrag.com>

# Push Notifications
FCM_SERVER_KEY=your-fcm-server-key
APNS_KEY_ID=your-apns-key-id
APNS_TEAM_ID=your-team-id

# Rate Limiting
NOTIFICATION_RATE_LIMIT_PER_MINUTE=60
EMAIL_RATE_LIMIT_PER_HOUR=100

# Queue
REDIS_URL=redis://redis:6379
NOTIFICATION_QUEUE_NAME=notifications
QUEUE_RETRY_ATTEMPTS=3

# Monitoring
LOG_LEVEL=info
METRICS_PORT=9090
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Send real-time notifications via WebSocket
- [ ] Respect user notification preferences and quiet hours
- [ ] Support multiple delivery channels (in-app, email, push)
- [ ] Handle offline users with notification persistence
- [ ] Track delivery status and read receipts
- [ ] Support notification templates with dynamic content

### **Performance Acceptance**
- [ ] Real-time delivery within 1 second for critical notifications
- [ ] Support 10,000+ concurrent WebSocket connections
- [ ] Email delivery within 5 minutes for normal priority
- [ ] Handle notification bursts without degradation

### **Reliability Acceptance**
- [ ] 99.9% delivery success rate for critical notifications
- [ ] Graceful handling of delivery failures with retry logic
- [ ] WebSocket reconnection for network issues
- [ ] Proper cleanup of expired notifications

This Notification Module provides comprehensive real-time communication capabilities essential for maintaining user engagement and providing instant feedback across the Self-Improving RAG Platform. 