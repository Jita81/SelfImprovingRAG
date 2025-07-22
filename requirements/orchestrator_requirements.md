# Orchestrator Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: Orchestrator  
**Size Estimate**: ~25k tokens  
**Priority**: Foundation (Week 1)  
**Branch**: `orchestrator` → `beta`  
**Development Environment**: Fresh Cursor agent cycle  

### **Purpose**
The Orchestrator Module serves as the central API Gateway and coordination hub for the Self-Improving RAG Platform. It manages routing, authentication, module discovery, workflow orchestration, and cross-module communication.

---

## 🎯 **Functional Requirements**

### **FR-1: API Gateway & Routing**
- **FR-1.1**: Route incoming HTTP requests to appropriate modules
- **FR-1.2**: Support dynamic module registration and discovery
- **FR-1.3**: Handle request/response transformation between frontend and modules
- **FR-1.4**: Provide unified API versioning across all modules
- **FR-1.5**: Support load balancing across multiple module instances

### **FR-2: Authentication & Authorization**
- **FR-2.1**: Authenticate users via JWT tokens
- **FR-2.2**: Authorize requests based on user roles and permissions
- **FR-2.3**: Propagate security context to downstream modules
- **FR-2.4**: Support API key authentication for programmatic access
- **FR-2.5**: Implement session management and token refresh

### **FR-3: Module Discovery & Health**
- **FR-3.1**: Discover available modules at startup
- **FR-3.2**: Monitor module health and availability
- **FR-3.3**: Handle graceful degradation when modules are unavailable
- **FR-3.4**: Support hot-swapping of module instances
- **FR-3.5**: Maintain service registry with module metadata

### **FR-4: Workflow Orchestration**
- **FR-4.1**: Execute complex multi-module workflows
- **FR-4.2**: Handle workflow state management and persistence
- **FR-4.3**: Support workflow rollback and error recovery
- **FR-4.4**: Provide workflow status tracking and monitoring
- **FR-4.5**: Enable conditional workflow execution based on results

### **FR-5: Event Management**
- **FR-5.1**: Distribute events between modules
- **FR-5.2**: Support event filtering and routing
- **FR-5.3**: Handle event ordering and guaranteed delivery
- **FR-5.4**: Provide event replay capabilities
- **FR-5.5**: Support event transformation and enrichment

### **FR-6: Rate Limiting & Throttling**
- **FR-6.1**: Implement per-user rate limiting
- **FR-6.2**: Support per-endpoint rate limiting
- **FR-6.3**: Handle burst traffic with token bucket algorithm
- **FR-6.4**: Provide rate limit bypass for premium users
- **FR-6.5**: Return appropriate HTTP status codes and headers

---

## 🔧 **Non-Functional Requirements**

### **NFR-1: Performance**
- **NFR-1.1**: Response time < 50ms for routing decisions
- **NFR-1.2**: Throughput > 10,000 requests per second
- **NFR-1.3**: Support horizontal scaling to handle load
- **NFR-1.4**: Memory usage < 1GB per instance
- **NFR-1.5**: CPU usage < 70% under normal load

### **NFR-2: Reliability**
- **NFR-2.1**: 99.9% uptime availability
- **NFR-2.2**: Graceful handling of module failures
- **NFR-2.3**: Circuit breaker pattern for failing modules
- **NFR-2.4**: Automatic retry with exponential backoff
- **NFR-2.5**: Zero-downtime deployments

### **NFR-3: Security**
- **NFR-3.1**: All communication encrypted with TLS 1.3
- **NFR-3.2**: JWT tokens with 15-minute expiry
- **NFR-3.3**: OWASP Top 10 compliance
- **NFR-3.4**: Rate limiting to prevent DDoS attacks
- **NFR-3.5**: Audit logging for all requests

### **NFR-4: Scalability**
- **NFR-4.1**: Support 1,000+ concurrent users
- **NFR-4.2**: Horizontal scaling with load balancer
- **NFR-4.3**: Stateless design for easy scaling
- **NFR-4.4**: Database connection pooling
- **NFR-4.5**: Caching for frequently accessed data

### **NFR-5: Maintainability**
- **NFR-5.1**: Comprehensive logging with structured format
- **NFR-5.2**: Health check endpoints for monitoring
- **NFR-5.3**: Metrics collection for observability
- **NFR-5.4**: Configuration via environment variables
- **NFR-5.5**: API documentation with OpenAPI 3.0

---

## 🏗️ **Technical Architecture**

### **Architecture Pattern**: Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   Gateway   │ │    Auth     │ │  Workflow   │       │
│  │ Controller  │ │ Controller  │ │ Controller  │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│              Application Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  Gateway    │ │    Auth     │ │  Workflow   │       │
│  │  Service    │ │  Service    │ │   Engine    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                Domain Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   Module    │ │  Workflow   │ │    User     │       │
│  │  Registry   │ │    State    │ │   Session   │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│            Infrastructure Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Module HTTP │ │  Event Bus  │ │ Config      │       │
│  │  Gateway    │ │   Gateway   │ │ Repository  │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### **Core Components**

#### **1. API Layer**
```typescript
// Gateway Controller - Main API entry point
@Controller('/api/v1')
export class GatewayController {
    constructor(
        private readonly gatewayService: GatewayService,
        private readonly authService: AuthService
    ) {}

    @All('*')
    async routeRequest(
        @Req() request: Request,
        @Res() response: Response
    ): Promise<void> {
        // Route to appropriate module
    }
}

// Authentication Controller
@Controller('/auth')
export class AuthController {
    @Post('/login')
    async login(@Body() credentials: LoginDto): Promise<AuthResponseDto> {}
    
    @Post('/refresh')
    async refresh(@Body() token: RefreshTokenDto): Promise<AuthResponseDto> {}
    
    @Post('/logout')
    async logout(@Headers('authorization') token: string): Promise<void> {}
}

// Workflow Controller
@Controller('/workflows')
export class WorkflowController {
    @Post('/')
    async startWorkflow(@Body() request: StartWorkflowDto): Promise<WorkflowResponseDto> {}
    
    @Get('/:id')
    async getWorkflowStatus(@Param('id') id: string): Promise<WorkflowStatusDto> {}
    
    @Post('/:id/abort')
    async abortWorkflow(@Param('id') id: string): Promise<void> {}
}
```

#### **2. Application Layer**
```typescript
// Gateway Service - Core routing logic
export class GatewayService {
    constructor(
        private readonly moduleRegistry: ModuleRegistry,
        private readonly loadBalancer: LoadBalancer,
        private readonly circuitBreaker: CircuitBreaker
    ) {}

    async routeRequest(request: IncomingRequest): Promise<ModuleResponse> {
        const module = await this.moduleRegistry.findModuleForPath(request.path);
        const instance = await this.loadBalancer.selectInstance(module);
        return this.circuitBreaker.execute(() => 
            this.forwardRequest(instance, request)
        );
    }
}

// Authentication Service
export class AuthService {
    async authenticate(token: string): Promise<User> {}
    async authorize(user: User, resource: string, action: string): Promise<boolean> {}
    async generateToken(user: User): Promise<string> {}
    async refreshToken(refreshToken: string): Promise<string> {}
}

// Workflow Engine
export class WorkflowEngine {
    async executeWorkflow(definition: WorkflowDefinition): Promise<WorkflowResult> {}
    async pauseWorkflow(workflowId: string): Promise<void> {}
    async resumeWorkflow(workflowId: string): Promise<void> {}
    async rollbackWorkflow(workflowId: string, stepId: string): Promise<void> {}
}
```

#### **3. Domain Layer**
```typescript
// Module Registry - Service discovery
export class ModuleRegistry {
    private modules: Map<string, ModuleInfo> = new Map();
    
    async registerModule(module: ModuleInfo): Promise<void> {}
    async unregisterModule(moduleId: string): Promise<void> {}
    async findModuleForPath(path: string): Promise<ModuleInfo> {}
    async getHealthyModules(): Promise<ModuleInfo[]> {}
}

// Workflow State
export class WorkflowState {
    constructor(
        public readonly id: WorkflowId,
        public readonly definition: WorkflowDefinition,
        public status: WorkflowStatus,
        public currentStep: WorkflowStep,
        public executionContext: ExecutionContext
    ) {}
    
    nextStep(): WorkflowStep {}
    rollbackTo(stepId: string): void {}
    complete(result: WorkflowResult): void {}
    fail(error: WorkflowError): void {}
}

// User Session
export class UserSession {
    constructor(
        public readonly userId: UserId,
        public readonly token: JWTToken,
        public readonly permissions: Permission[],
        public readonly expiresAt: Date
    ) {}
    
    isValid(): boolean {}
    hasPermission(resource: string, action: string): boolean {}
    refresh(): UserSession {}
}
```

#### **4. Infrastructure Layer**
```typescript
// Module HTTP Gateway
export class ModuleHttpGateway {
    constructor(private readonly httpClient: HttpClient) {}
    
    async forwardRequest(module: ModuleInfo, request: IncomingRequest): Promise<ModuleResponse> {}
    async healthCheck(module: ModuleInfo): Promise<HealthStatus> {}
}

// Event Bus Gateway
export class EventBusGateway {
    async publishEvent(event: DomainEvent): Promise<void> {}
    async subscribeToEvents(eventTypes: string[], handler: EventHandler): Promise<void> {}
    async unsubscribe(subscriptionId: string): Promise<void> {}
}

// Configuration Repository
export class ConfigRepository {
    async getModuleConfig(moduleId: string): Promise<ModuleConfig> {}
    async updateModuleConfig(moduleId: string, config: ModuleConfig): Promise<void> {}
    async getGlobalConfig(): Promise<GlobalConfig> {}
}
```

---

## 📊 **Database Schema**

### **PostgreSQL Tables**

```sql
-- Module Registry
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(20) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    health_check_url VARCHAR(500) NOT NULL,
    status module_status DEFAULT 'healthy',
    last_health_check TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE module_status AS ENUM ('healthy', 'unhealthy', 'disabled');

-- Module Routes
CREATE TABLE module_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
    path_pattern VARCHAR(500) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workflow Definitions
CREATE TABLE workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    definition JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workflow Executions
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    definition_id UUID REFERENCES workflow_definitions(id),
    user_id UUID NOT NULL,
    status workflow_status DEFAULT 'pending',
    current_step VARCHAR(100),
    execution_context JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TYPE workflow_status AS ENUM ('pending', 'running', 'completed', 'failed', 'aborted');

-- User Sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    refresh_token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW()
);

-- API Rate Limits
CREATE TABLE rate_limit_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier VARCHAR(100) NOT NULL, -- user_id, api_key, ip_address
    identifier_type rate_limit_type NOT NULL,
    endpoint_pattern VARCHAR(500),
    requests_per_minute INTEGER NOT NULL,
    requests_per_hour INTEGER NOT NULL,
    requests_per_day INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE rate_limit_type AS ENUM ('user', 'api_key', 'ip_address', 'global');

-- Rate Limit Tracking
CREATE TABLE rate_limit_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID REFERENCES rate_limit_rules(id) ON DELETE CASCADE,
    window_start TIMESTAMP NOT NULL,
    window_type VARCHAR(10) NOT NULL, -- 'minute', 'hour', 'day'
    request_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Redis Cache Schema**

```typescript
// Module Health Status Cache
interface ModuleHealthCache {
    moduleId: string;
    status: 'healthy' | 'unhealthy';
    lastCheck: number; // timestamp
    responseTime: number; // ms
    consecutiveFailures: number;
}

// User Session Cache
interface UserSessionCache {
    userId: string;
    permissions: string[];
    tokenHash: string;
    expiresAt: number; // timestamp
}

// Rate Limit Cache
interface RateLimitCache {
    identifier: string;
    endpoint: string;
    windowStart: number;
    requestCount: number;
    resetTime: number;
}

// Module Route Cache
interface ModuleRouteCache {
    pathPattern: string;
    moduleId: string;
    priority: number;
    lastUpdated: number;
}
```

---

## 🔌 **API Specifications**

### **Main Gateway API**

```yaml
# OpenAPI 3.0 Specification
openapi: 3.0.0
info:
  title: Self-Improving RAG Platform - Orchestrator API
  version: 1.0.0
  description: Central API Gateway for all platform modules

paths:
  # Proxy all module requests
  /api/v1/{module}/{path+}:
    x-swagger-router-controller: GatewayController
    get:
      summary: Route GET requests to modules
      parameters:
        - name: module
          in: path
          required: true
          schema:
            type: string
            enum: [core, users, achievements, notifications, data-sources, analytics, comparisons, bets, statistics]
        - name: path
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Successful response from module
        404:
          description: Module or endpoint not found
        503:
          description: Module unavailable
    
    post:
      summary: Route POST requests to modules
      # Similar structure for PUT, PATCH, DELETE
      
  # Authentication endpoints
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
                  minLength: 8
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                  refreshToken:
                    type: string
                  expiresAt:
                    type: string
                    format: date-time
        401:
          description: Invalid credentials

  /auth/refresh:
    post:
      summary: Refresh authentication token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                refreshToken:
                  type: string
      responses:
        200:
          description: Token refreshed
        401:
          description: Invalid refresh token

  /auth/logout:
    post:
      summary: User logout
      security:
        - bearerAuth: []
      responses:
        200:
          description: Logout successful

  # Workflow endpoints
  /workflows:
    post:
      summary: Start a new workflow
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                workflowType:
                  type: string
                  enum: [optimization, comparison, analysis]
                parameters:
                  type: object
      responses:
        201:
          description: Workflow started
          content:
            application/json:
              schema:
                type: object
                properties:
                  workflowId:
                    type: string
                  status:
                    type: string
                  estimatedDuration:
                    type: integer

  /workflows/{id}:
    get:
      summary: Get workflow status
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Workflow status
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  status:
                    type: string
                  progress:
                    type: number
                  currentStep:
                    type: string
                  result:
                    type: object

  # Health and monitoring
  /health:
    get:
      summary: Orchestrator health check
      responses:
        200:
          description: Healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [healthy]
                  timestamp:
                    type: string
                  modules:
                    type: array
                    items:
                      type: object
                      properties:
                        name:
                          type: string
                        status:
                          type: string
                        responseTime:
                          type: number

  /metrics:
    get:
      summary: Prometheus metrics
      responses:
        200:
          description: Metrics in Prometheus format

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### **Module Registration API** (Internal)

```typescript
// Module registration endpoint for internal use
interface ModuleRegistrationRequest {
    name: string;
    version: string;
    baseUrl: string;
    healthCheckUrl: string;
    routes: ModuleRoute[];
    metadata?: Record<string, any>;
}

interface ModuleRoute {
    pathPattern: string;
    methods: HttpMethod[];
    description?: string;
    priority?: number;
}

interface ModuleRegistrationResponse {
    moduleId: string;
    status: 'registered' | 'updated';
    nextHealthCheck: Date;
}
```

---

## 🔄 **Integration Points**

### **Event-Driven Communication**

```typescript
// Events published by Orchestrator
export class UserLoggedInEvent implements DomainEvent {
    constructor(
        public readonly userId: string,
        public readonly timestamp: Date,
        public readonly sessionId: string
    ) {}
}

export class WorkflowStartedEvent implements DomainEvent {
    constructor(
        public readonly workflowId: string,
        public readonly workflowType: string,
        public readonly userId: string,
        public readonly timestamp: Date
    ) {}
}

export class WorkflowCompletedEvent implements DomainEvent {
    constructor(
        public readonly workflowId: string,
        public readonly result: WorkflowResult,
        public readonly duration: number,
        public readonly timestamp: Date
    ) {}
}

// Events subscribed to by Orchestrator
export class ModuleHealthChangedEvent implements DomainEvent {
    constructor(
        public readonly moduleId: string,
        public readonly status: 'healthy' | 'unhealthy',
        public readonly timestamp: Date
    ) {}
}

export class RateLimitExceededEvent implements DomainEvent {
    constructor(
        public readonly userId: string,
        public readonly endpoint: string,
        public readonly requestCount: number,
        public readonly timestamp: Date
    ) {}
}
```

### **HTTP Integration with Modules**

```typescript
// Standard module communication interface
export interface ModuleHttpClient {
    async get<T>(path: string, params?: any): Promise<T>;
    async post<T>(path: string, body: any): Promise<T>;
    async put<T>(path: string, body: any): Promise<T>;
    async delete<T>(path: string): Promise<T>;
    async healthCheck(): Promise<HealthStatus>;
}

// Circuit breaker for module calls
export class CircuitBreaker {
    constructor(
        private readonly failureThreshold: number = 5,
        private readonly timeout: number = 60000,
        private readonly resetTimeout: number = 30000
    ) {}

    async execute<T>(operation: () => Promise<T>): Promise<T> {
        if (this.state === CircuitBreakerState.OPEN) {
            if (Date.now() - this.lastFailureTime > this.resetTimeout) {
                this.state = CircuitBreakerState.HALF_OPEN;
            } else {
                throw new CircuitBreakerOpenError();
            }
        }

        try {
            const result = await operation();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            throw error;
        }
    }
}
```

---

## 🧪 **Testing Requirements**

### **Unit Tests** (85% coverage minimum)

```typescript
// Example test structure
describe('GatewayService', () => {
    let service: GatewayService;
    let moduleRegistry: jest.Mocked<ModuleRegistry>;
    let loadBalancer: jest.Mocked<LoadBalancer>;

    beforeEach(() => {
        moduleRegistry = createMockModuleRegistry();
        loadBalancer = createMockLoadBalancer();
        service = new GatewayService(moduleRegistry, loadBalancer);
    });

    describe('routeRequest', () => {
        it('should route request to correct module', async () => {
            // Arrange
            const request = createMockRequest('/api/v1/core/context-builds');
            const module = createMockModule('core-rag');
            moduleRegistry.findModuleForPath.mockResolvedValue(module);

            // Act
            const result = await service.routeRequest(request);

            // Assert
            expect(moduleRegistry.findModuleForPath).toHaveBeenCalledWith('/api/v1/core/context-builds');
            expect(result).toBeDefined();
        });

        it('should handle module not found', async () => {
            // Arrange
            const request = createMockRequest('/api/v1/unknown/endpoint');
            moduleRegistry.findModuleForPath.mockRejectedValue(new ModuleNotFoundError());

            // Act & Assert
            await expect(service.routeRequest(request)).rejects.toThrow(ModuleNotFoundError);
        });
    });
});

describe('AuthService', () => {
    // Authentication and authorization tests
});

describe('WorkflowEngine', () => {
    // Workflow execution tests
});
```

### **Integration Tests**

```typescript
describe('Orchestrator Integration', () => {
    let app: INestApplication;
    let moduleRegistry: ModuleRegistry;

    beforeAll(async () => {
        const moduleRef = await Test.createTestingModule({
            imports: [OrchestratorModule],
        }).compile();

        app = moduleRef.createNestApplication();
        moduleRegistry = app.get(ModuleRegistry);
        await app.init();
    });

    describe('Module Registration', () => {
        it('should register a new module', async () => {
            // Test module registration flow
        });

        it('should route requests to registered module', async () => {
            // Test request routing
        });
    });

    describe('Authentication Flow', () => {
        it('should authenticate valid user', async () => {
            // Test authentication
        });

        it('should reject invalid credentials', async () => {
            // Test authentication failure
        });
    });

    describe('Workflow Execution', () => {
        it('should execute multi-step workflow', async () => {
            // Test workflow execution
        });
    });
});
```

### **End-to-End Tests**

```typescript
describe('Complete User Journey', () => {
    it('should complete optimization workflow', async () => {
        // 1. User logs in
        const loginResponse = await request(app.getHttpServer())
            .post('/auth/login')
            .send({ email: 'user@test.com', password: 'password' });

        // 2. Start optimization workflow
        const workflowResponse = await request(app.getHttpServer())
            .post('/workflows')
            .set('Authorization', `Bearer ${loginResponse.body.token}`)
            .send({ workflowType: 'optimization', parameters: {} });

        // 3. Check workflow progress
        const statusResponse = await request(app.getHttpServer())
            .get(`/workflows/${workflowResponse.body.workflowId}`)
            .set('Authorization', `Bearer ${loginResponse.body.token}`);

        // 4. Wait for completion and verify result
        expect(statusResponse.body.status).toBe('completed');
    });
});
```

### **Performance Tests**

```typescript
describe('Performance Requirements', () => {
    it('should handle 10,000 requests per second', async () => {
        // Load testing with 10k RPS
    });

    it('should respond within 50ms for routing', async () => {
        // Response time testing
    });

    it('should scale horizontally', async () => {
        // Scalability testing
    });
});
```

---

## 🚀 **Deployment Requirements**

### **Docker Configuration**

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS runtime

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nestjs -u 1001

WORKDIR /app
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nestjs:nodejs /app/package.json ./package.json

USER nestjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "dist/main.js"]
```

### **Kubernetes Manifests**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator
  labels:
    app: orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orchestrator
  template:
    metadata:
      labels:
        app: orchestrator
    spec:
      containers:
      - name: orchestrator
        image: selfrag/orchestrator:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: orchestrator-service
spec:
  selector:
    app: orchestrator
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orchestrator-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.selfrag.com
    secretName: orchestrator-tls
  rules:
  - host: api.selfrag.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: orchestrator-service
            port:
              number: 80
```

### **Environment Configuration**

```bash
# .env.production
NODE_ENV=production
PORT=3000

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/selfrag
DATABASE_SSL=true
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis:6379
REDIS_PREFIX=orchestrator:

# Authentication
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRES_IN=15m
REFRESH_TOKEN_EXPIRES_IN=7d

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_REQUESTS_PER_HOUR=10000

# Module Discovery
MODULE_DISCOVERY_INTERVAL=30s
MODULE_HEALTH_CHECK_INTERVAL=60s

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60s
CIRCUIT_BREAKER_RESET_TIMEOUT=30s

# Monitoring
METRICS_PORT=9090
LOG_LEVEL=info
STRUCTURED_LOGGING=true

# External Services
EVENT_BUS_URL=amqp://rabbitmq:5672
MONITORING_URL=http://prometheus:9090
```

---

## 📊 **Monitoring & Observability**

### **Metrics Collection**

```typescript
// Prometheus metrics
export const orchestratorMetrics = {
    httpRequestsTotal: new Counter({
        name: 'http_requests_total',
        help: 'Total number of HTTP requests',
        labelNames: ['method', 'route', 'status_code', 'module']
    }),
    
    httpRequestDuration: new Histogram({
        name: 'http_request_duration_seconds',
        help: 'HTTP request duration in seconds',
        labelNames: ['method', 'route', 'module'],
        buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]
    }),
    
    moduleHealthStatus: new Gauge({
        name: 'module_health_status',
        help: 'Module health status (1 = healthy, 0 = unhealthy)',
        labelNames: ['module_name']
    }),
    
    activeWorkflows: new Gauge({
        name: 'active_workflows_total',
        help: 'Number of active workflows',
        labelNames: ['workflow_type']
    }),
    
    circuitBreakerState: new Gauge({
        name: 'circuit_breaker_state',
        help: 'Circuit breaker state (0 = closed, 1 = open, 2 = half-open)',
        labelNames: ['module_name']
    })
};
```

### **Health Check Implementation**

```typescript
@Injectable()
export class HealthService {
    constructor(
        private readonly moduleRegistry: ModuleRegistry,
        private readonly databaseService: DatabaseService,
        private readonly redisService: RedisService
    ) {}

    async checkHealth(): Promise<HealthStatus> {
        const checks = await Promise.allSettled([
            this.checkDatabase(),
            this.checkRedis(),
            this.checkModules()
        ]);

        const isHealthy = checks.every(check => check.status === 'fulfilled');
        
        return {
            status: isHealthy ? 'healthy' : 'unhealthy',
            timestamp: new Date().toISOString(),
            checks: {
                database: this.getCheckResult(checks[0]),
                redis: this.getCheckResult(checks[1]),
                modules: this.getCheckResult(checks[2])
            }
        };
    }
}
```

---

## 🔒 **Security Requirements**

### **Authentication & Authorization**

```typescript
// JWT Token Structure
interface JWTPayload {
    sub: string; // user ID
    email: string;
    roles: string[];
    permissions: string[];
    iat: number; // issued at
    exp: number; // expires at
}

// Role-Based Access Control
enum Role {
    ADMIN = 'admin',
    USER = 'user',
    API_CLIENT = 'api_client'
}

enum Permission {
    READ_CONTEXT_BUILDS = 'context_builds:read',
    WRITE_CONTEXT_BUILDS = 'context_builds:write',
    ADMIN_USERS = 'users:admin',
    VIEW_ANALYTICS = 'analytics:view'
}
```

### **Security Middleware**

```typescript
@Injectable()
export class SecurityMiddleware implements NestMiddleware {
    use(req: Request, res: Response, next: NextFunction) {
        // Add security headers
        res.setHeader('X-Content-Type-Options', 'nosniff');
        res.setHeader('X-Frame-Options', 'DENY');
        res.setHeader('X-XSS-Protection', '1; mode=block');
        res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
        
        next();
    }
}

@Injectable()
export class RateLimitMiddleware implements NestMiddleware {
    constructor(private readonly rateLimitService: RateLimitService) {}
    
    async use(req: Request, res: Response, next: NextFunction) {
        const identifier = this.getIdentifier(req);
        const isAllowed = await this.rateLimitService.checkLimit(identifier, req.path);
        
        if (!isAllowed) {
            throw new TooManyRequestsException('Rate limit exceeded');
        }
        
        next();
    }
}
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Successfully route requests to all 9 modules
- [ ] Authenticate users with JWT tokens
- [ ] Execute multi-step workflows across modules
- [ ] Handle module failures gracefully
- [ ] Distribute events between modules
- [ ] Enforce rate limits per user and endpoint

### **Performance Acceptance**
- [ ] Response time < 50ms for routing decisions
- [ ] Handle 10,000 requests per second
- [ ] Memory usage < 1GB per instance
- [ ] 99.9% uptime availability

### **Security Acceptance**
- [ ] All communication encrypted with TLS 1.3
- [ ] JWT tokens expire after 15 minutes
- [ ] Rate limiting prevents DDoS attacks
- [ ] OWASP Top 10 compliance verified
- [ ] Audit logging for all requests

### **Integration Acceptance**
- [ ] Register and discover all modules
- [ ] Health check all modules every 60 seconds
- [ ] Circuit breaker trips after 5 failures
- [ ] Events delivered with 99.9% success rate
- [ ] Zero-downtime deployments working

### **Documentation Acceptance**
- [ ] OpenAPI 3.0 specification complete
- [ ] Deployment guides for Docker and Kubernetes
- [ ] Monitoring and alerting setup documented
- [ ] Security configuration documented
- [ ] Troubleshooting guide available

This orchestrator module serves as the foundation for the entire Self-Improving RAG Platform, providing the critical infrastructure needed for module coordination, security, and workflow orchestration. 