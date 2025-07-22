# Core RAG Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: Core RAG  
**Size Estimate**: ~28k tokens  
**Priority**: 1 (Foundation)  
**TDD Cycles**: 1, 2, 7  
**Branch**: `module/core-rag`  
**Cursor Window**: #2  
**Dependencies**: Orchestrator Module  

### **Purpose**
The Core RAG Module implements an **Agentic RAG** architecture following proven patterns for intelligent query handling. It features an LLM agent that autonomously analyzes queries, rewrites them for optimization, retrieves relevant data from MCP servers, reranks results, generates answers, and validates responses through iterative feedback loops.

---

## 🎯 **Functional Requirements**

### **FR-1: Agentic Query Analysis** (TDD Cycle 1)
- **FR-1.1**: LLM agent analyzes incoming queries for clarity and completeness
- **FR-1.2**: Determine autonomously whether external knowledge retrieval is required
- **FR-1.3**: Classify query types and complexity for appropriate handling
- **FR-1.4**: Assess query ambiguity and identify missing context
- **FR-1.5**: Route queries to appropriate processing paths based on analysis
- **FR-1.6**: Track query classification accuracy and agent decision quality
- **FR-1.7**: Support multi-intent query detection and decomposition

### **FR-2: Dynamic Query Rewriting** 
- **FR-2.1**: Agent rewrites queries for improved clarity and retrieval effectiveness
- **FR-2.2**: Expand abbreviated queries with domain-specific context
- **FR-2.3**: Decompose complex queries into focused sub-queries
- **FR-2.4**: Generate multiple query variations for comprehensive retrieval
- **FR-2.5**: Optimize queries for specific MCP server capabilities
- **FR-2.6**: Learn from rewriting effectiveness to improve future rewrites
- **FR-2.7**: Preserve original user intent while enhancing query precision

### **FR-3: Agentic Query Processing** (TDD Cycle 2)
- **FR-3.1**: Agent orchestrates entire query processing pipeline autonomously
- **FR-3.2**: Make intelligent decisions about when to trigger external retrieval
- **FR-3.3**: Coordinate parallel retrieval from multiple MCP servers
- **FR-3.4**: Interface with multiple LLM providers with agent-driven selection
- **FR-3.5**: Handle streaming responses with real-time decision making
- **FR-3.6**: Track query performance and adapt processing strategies
- **FR-3.7**: Support iterative query refinement based on partial results

### **FR-4: MCP Server Integration**
- **FR-4.1**: Connect to multiple MCP (Multi-Component Processing) servers in parallel
- **FR-4.2**: Route queries to appropriate MCP servers based on content type and domain
- **FR-4.3**: Aggregate and normalize responses from different MCP server types
- **FR-4.4**: Handle MCP server failures and implement fallback strategies
- **FR-4.5**: Support dynamic MCP server discovery and registration
- **FR-4.6**: Monitor MCP server performance and response quality
- **FR-4.7**: Implement load balancing across multiple MCP server instances

### **FR-5: Intelligent Result Reranking**
- **FR-5.1**: Agent performs LLM-based reranking of retrieved results
- **FR-5.2**: Prioritize most relevant documents/data for query context
- **FR-5.3**: Consider semantic similarity and relevance scoring
- **FR-5.4**: Apply domain-specific ranking criteria and user preferences
- **FR-5.5**: Support custom reranking models and algorithms
- **FR-5.6**: Track reranking effectiveness and continuously improve
- **FR-5.7**: Filter out low-quality or irrelevant results autonomously

### **FR-6: Answer Generation & Validation** (TDD Cycle 7)
- **FR-6.1**: Generate answers using curated context from reranked results
- **FR-6.2**: Agent validates generated answers for correctness and relevance
- **FR-6.3**: Implement iterative feedback loops for answer improvement
- **FR-6.4**: Detect and handle hallucinations and factual errors
- **FR-6.5**: Support multi-step reasoning and complex question answering
- **FR-6.6**: Generate confidence scores and uncertainty estimates
- **FR-6.7**: Provide source attribution and evidence for claims

### **FR-7: Agentic Feedback Loop**
- **FR-7.1**: Agent autonomously evaluates answer quality and completeness
- **FR-7.2**: Trigger query rewriting and re-retrieval when answers are insufficient
- **FR-7.3**: Learn from user feedback to improve future query handling
- **FR-7.4**: Adapt retrieval and generation strategies based on success patterns
- **FR-7.5**: Support human-in-the-loop validation for critical queries
- **FR-7.6**: Implement automated quality gates and escalation triggers
- **FR-7.7**: Track improvement cycles and measure learning effectiveness

### **FR-8: Context Build Management**
- **FR-8.1**: Create and manage context builds for different domains and use cases
- **FR-8.2**: Support versioning and A/B testing of context configurations
- **FR-8.3**: Automatically optimize context builds based on agent performance
- **FR-8.4**: Handle context build templates and reusable components
- **FR-8.5**: Track context build effectiveness and usage patterns
- **FR-8.6**: Support collaborative context build development

### **FR-9: LLM Agent Orchestration**
- **FR-9.1**: Orchestrate multiple LLM agents for specialized tasks
- **FR-9.2**: Support agent specialization (analysis, rewriting, validation, etc.)
- **FR-9.3**: Handle agent-to-agent communication and coordination
- **FR-9.4**: Implement agent task delegation and load balancing
- **FR-9.5**: Monitor agent performance and resource utilization
- **FR-9.6**: Support agent model selection and fine-tuning

---

## 🔧 **Non-Functional Requirements**

### **NFR-1: Performance**
- **NFR-1.1**: Agentic pipeline processing time < 5 seconds for 95% of requests
- **NFR-1.2**: Query analysis by agent completes within 500ms
- **NFR-1.3**: MCP server parallel retrieval completes within 2 seconds
- **NFR-1.4**: Agent-driven reranking completes within 1 second
- **NFR-1.5**: Answer validation feedback loop < 3 iterations for 90% of queries
- **NFR-1.6**: Support 1,000 concurrent agentic query pipelines
- **NFR-1.7**: LLM agent API response time < 10 seconds per agent call

### **NFR-2: Scalability**
- **NFR-2.1**: Handle 100,000+ agentic query pipelines per instance
- **NFR-2.2**: Support horizontal scaling for MCP server connections
- **NFR-2.3**: Optimize database queries for pipeline state management
- **NFR-2.4**: Implement caching for agent analysis results and MCP responses
- **NFR-2.5**: Support sharding for pipeline and answer storage
- **NFR-2.6**: Auto-scale agent pool based on query volume

### **NFR-3: Reliability**
- **NFR-3.1**: 99.5% uptime for agentic query processing
- **NFR-3.2**: Graceful degradation when MCP servers are unavailable
- **NFR-3.3**: Agent fallback strategies when primary LLM providers fail
- **NFR-3.4**: Automatic retry with exponential backoff for failed agent calls
- **NFR-3.5**: Data consistency for pipeline state transitions
- **NFR-3.6**: Backup and recovery for pipeline history and validated answers
- **NFR-3.7**: Circuit breaker patterns for MCP server connections

### **NFR-4: Quality & Intelligence**
- **NFR-4.1**: Answer quality improvement of 25%+ through agentic validation
- **NFR-4.2**: Agent confidence scores of 85%+ for validated answers
- **NFR-4.3**: Hallucination detection accuracy of 95%+ through agent validation
- **NFR-4.4**: Source attribution for all generated content via MCP servers
- **NFR-4.5**: Query rewriting effectiveness of 80%+ clarity improvement
- **NFR-4.6**: MCP server selection accuracy of 90%+ for relevant data
- **NFR-4.7**: Reranking precision improvement of 30%+ over baseline ranking
- **NFR-4.5**: Bias detection and mitigation

---

## 🏗️ **Technical Architecture**

### **Architecture Pattern**: Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   Agentic   │ │    Query    │ │   Answer    │       │
│  │    RAG      │ │   Analysis  │ │ Validation  │       │
│  │ Controller  │ │ Controller  │ │ Controller  │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│              Application Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  LLM Agent  │ │    Query    │ │    MCP      │       │
│  │Orchestrator │ │ Rewriting   │ │Coordinator  │       │
│  │   Service   │ │  Service    │ │  Service    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Reranking   │ │   Answer    │ │  Feedback   │       │
│  │  Service    │ │Generation   │ │    Loop     │       │
│  │             │ │  Service    │ │  Service    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                Domain Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Agent Query │ │ MCP Server  │ │ Validated   │       │
│  │  Analysis   │ │  Response   │ │   Answer    │       │
│  │   Result    │ │  Aggregate  │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│            Infrastructure Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ MCP Server  │ │ LLM Agent   │ │  Context    │       │
│  │ Connection  │ │  Gateway    │ │  Store      │       │
│  │    Pool     │ │(Multi-Model)│ │(Vector+SQL) │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### **Core Components**

#### **1. Domain Layer**

```typescript
// Agentic Query Analysis Result
export class AgentQueryAnalysis {
    constructor(
        public readonly originalQuery: string,
        public readonly queryType: QueryType,
        public readonly complexity: QueryComplexity,
        public readonly requiresExternalData: boolean,
        public readonly suggestedMCPServers: string[],
        public readonly rewriteRecommendations: QueryRewrite[],
        public readonly confidence: number,
        public readonly timestamp: Date = new Date()
    ) {}

    needsRewriting(): boolean {
        return this.rewriteRecommendations.length > 0;
    }

    shouldUseMultipleMCPServers(): boolean {
        return this.suggestedMCPServers.length > 1;
    }

    getOptimalRewrite(): QueryRewrite | null {
        return this.rewriteRecommendations
            .sort((a, b) => b.confidence - a.confidence)[0] || null;
    }
}

// Agentic Query Processing Pipeline
export class AgenticQueryPipeline {
    constructor(
        public readonly id: PipelineId,
        public readonly originalQuery: string,
        public readonly userId: UserId,
        private analysis: AgentQueryAnalysis,
        private rewrittenQueries: RewrittenQuery[] = [],
        private mcpResponses: MCPResponse[] = [],
        private rerankedResults: RerankedResult[] = [],
        private generatedAnswer: GeneratedAnswer | null = null,
        private validationResult: ValidationResult | null = null,
        private feedbackLoops: FeedbackLoop[] = [],
        private status: PipelineStatus = PipelineStatus.ANALYZING
    ) {}

    static create(query: string, userId: UserId): AgenticQueryPipeline {
        return new AgenticQueryPipeline(
            PipelineId.generate(),
            query,
            userId,
            null as any // Will be set by analysis
        );
    }

    setAnalysis(analysis: AgentQueryAnalysis): void {
        this.analysis = analysis;
        this.status = PipelineStatus.REWRITING;
    }

    addRewrittenQuery(rewritten: RewrittenQuery): void {
        this.rewrittenQueries.push(rewritten);
        if (this.allRewritesComplete()) {
            this.status = PipelineStatus.RETRIEVING;
        }
    }

    addMCPResponse(response: MCPResponse): void {
        this.mcpResponses.push(response);
        if (this.allMCPResponsesReceived()) {
            this.status = PipelineStatus.RERANKING;
        }
    }

    setRerankedResults(results: RerankedResult[]): void {
        this.rerankedResults = results;
        this.status = PipelineStatus.GENERATING;
    }

    setGeneratedAnswer(answer: GeneratedAnswer): void {
        this.generatedAnswer = answer;
        this.status = PipelineStatus.VALIDATING;
    }

    setValidationResult(validation: ValidationResult): void {
        this.validationResult = validation;
        
        if (validation.isValid && validation.isComplete) {
            this.status = PipelineStatus.COMPLETED;
        } else {
            this.status = PipelineStatus.NEEDS_IMPROVEMENT;
            this.createFeedbackLoop(validation);
        }
    }

    createFeedbackLoop(validation: ValidationResult): void {
        const feedback = new FeedbackLoop(
            FeedbackLoopId.generate(),
            validation.issues,
            validation.suggestedImprovements,
            new Date()
        );
        this.feedbackLoops.push(feedback);
    }

    shouldRetry(): boolean {
        return this.status === PipelineStatus.NEEDS_IMPROVEMENT && 
               this.feedbackLoops.length < 3; // Max 3 retry attempts
    }

    getLatestFeedback(): FeedbackLoop | null {
        return this.feedbackLoops[this.feedbackLoops.length - 1] || null;
    }

    private allRewritesComplete(): boolean {
        return this.rewrittenQueries.length >= this.analysis.rewriteRecommendations.length;
    }

    private allMCPResponsesReceived(): boolean {
        return this.mcpResponses.length >= this.analysis.suggestedMCPServers.length;
    }
}

// MCP Server Response Aggregate
export class MCPServerResponseAggregate {
    constructor(
        public readonly serverId: string,
        public readonly serverType: MCPServerType,
        public readonly query: string,
        private responses: MCPDocument[],
        private metadata: MCPResponseMetadata,
        private status: MCPResponseStatus
    ) {}

    addDocument(document: MCPDocument): void {
        this.responses.push(document);
    }

    getTopDocuments(limit: number = 10): MCPDocument[] {
        return this.responses
            .sort((a, b) => b.relevanceScore - a.relevanceScore)
            .slice(0, limit);
    }

    calculateAggregateRelevance(): number {
        if (this.responses.length === 0) return 0;
        return this.responses.reduce((sum, doc) => sum + doc.relevanceScore, 0) / this.responses.length;
    }

    isHighQuality(): boolean {
        return this.calculateAggregateRelevance() > 0.7 && 
               this.responses.length >= 3;
    }
}

// Validated Answer with Sources
export class ValidatedAnswer {
    constructor(
        public readonly id: AnswerId,
        public readonly content: string,
        public readonly confidence: number,
        public readonly sources: AnswerSource[],
        public readonly validationChecks: ValidationCheck[],
        public readonly isFactuallyCorrect: boolean,
        public readonly isRelevant: boolean,
        public readonly isComplete: boolean,
        public readonly improvementSuggestions: string[] = [],
        public readonly generatedAt: Date = new Date()
    ) {}

    isHighQuality(): boolean {
        return this.confidence > 0.8 && 
               this.isFactuallyCorrect && 
               this.isRelevant && 
               this.isComplete;
    }

    needsImprovement(): boolean {
        return !this.isHighQuality() || this.improvementSuggestions.length > 0;
    }

    getQualityScore(): number {
        let score = this.confidence * 0.4;
        score += this.isFactuallyCorrect ? 0.25 : 0;
        score += this.isRelevant ? 0.2 : 0;
        score += this.isComplete ? 0.15 : 0;
        return Math.min(score, 1.0);
    }
}

// Context Element Value Object
export class ContextElement {
    constructor(
        public readonly id: ElementId,
        public readonly name: string,
        public readonly content: string,
        public readonly type: ElementType,
        public readonly tokenCount: number,
        public readonly causalImpact: number,
        public readonly tags: string[] = [],
        public readonly metadata: Record<string, any> = {}
    ) {}

    isRelevantTo(query: Query): boolean {
        const queryEmbedding = query.getEmbedding();
        const elementEmbedding = this.getEmbedding();
        const similarity = cosineSimilarity(queryEmbedding, elementEmbedding);
        return similarity > 0.7; // Relevance threshold
    }

    updateCausalImpact(newImpact: number): ContextElement {
        return new ContextElement(
            this.id,
            this.name,
            this.content,
            this.type,
            this.tokenCount,
            newImpact,
            this.tags,
            this.metadata
        );
    }
}

// Query Processing
export class Query {
    constructor(
        public readonly id: QueryId,
        public readonly text: string,
        public readonly userId: UserId,
        public readonly contextBuildId: BuildId,
        public readonly timestamp: Date,
        public readonly parameters: QueryParameters = {}
    ) {}

    getEmbedding(): number[] {
        // Generate embedding for semantic similarity
        return this.parameters.embedding || [];
    }

    preprocess(): Query {
        // Clean and enhance query text
        const processedText = this.text
            .trim()
            .toLowerCase()
            .replace(/[^\w\s]/g, '');
        
        return new Query(
            this.id,
            processedText,
            this.userId,
            this.contextBuildId,
            this.timestamp,
            this.parameters
        );
    }
}

// Optimization Engine
export class OptimizationResult {
    constructor(
        public readonly buildId: BuildId,
        public readonly originalMetrics: PerformanceMetrics,
        public readonly optimizedMetrics: PerformanceMetrics,
        public readonly changes: OptimizationChange[],
        public readonly confidence: number,
        public readonly timestamp: Date
    ) {}

    getImprovement(): number {
        return this.optimizedMetrics.overallScore - this.originalMetrics.overallScore;
    }

    isSignificant(): boolean {
        return this.getImprovement() > 0.05 && this.confidence > 0.8;
    }
}
```

#### **2. Application Layer**

```typescript
// LLM Agent Orchestrator Service - Main Agentic RAG Controller
@Injectable()
export class LLMAgentOrchestratorService {
    constructor(
        private readonly queryAnalysisAgent: IQueryAnalysisAgent,
        private readonly queryRewritingAgent: IQueryRewritingAgent,
        private readonly mcpCoordinator: IMCPCoordinatorService,
        private readonly rerankingService: IReankingService,
        private readonly answerGenerationAgent: IAnswerGenerationAgent,
        private readonly validationAgent: IValidationAgent,
        private readonly feedbackLoopService: IFeedbackLoopService,
        private readonly pipelineRepository: IPipelineRepository,
        private readonly performanceMonitor: IPerformanceMonitor,
        private readonly eventBus: IEventBus
    ) {}

    async processQuery(command: ProcessAgenticQueryCommand): Promise<ValidatedAnswer> {
        const startTime = Date.now();
        
        try {
            // Step 1: Create pipeline and analyze query
            const pipeline = AgenticQueryPipeline.create(command.query, command.userId);
            await this.pipelineRepository.save(pipeline);

            const analysis = await this.queryAnalysisAgent.analyzeQuery(command.query);
            pipeline.setAnalysis(analysis);
            
            await this.eventBus.publish(new QueryAnalyzedEvent(pipeline.id, analysis));

            // Step 2: Rewrite query if needed (following agentic pattern)
            if (analysis.needsRewriting()) {
                const rewrittenQueries = await this.queryRewritingAgent.rewriteQuery(
                    command.query, 
                    analysis.rewriteRecommendations
                );
                rewrittenQueries.forEach(rq => pipeline.addRewrittenQuery(rq));
                await this.eventBus.publish(new QueryRewrittenEvent(pipeline.id, rewrittenQueries));
            }

            // Step 3: Retrieve from MCP servers if external data needed (parallel processing)
            if (analysis.requiresExternalData) {
                const mcpResponses = await this.mcpCoordinator.retrieveFromServers(
                    analysis.suggestedMCPServers,
                    pipeline.rewrittenQueries.length > 0 ? 
                        pipeline.rewrittenQueries.map(rq => rq.text) : [command.query]
                );
                mcpResponses.forEach(response => pipeline.addMCPResponse(response));
                await this.eventBus.publish(new MCPDataRetrievedEvent(pipeline.id, mcpResponses));
            }

            // Step 4: Agent-driven reranking
            const rerankedResults = await this.rerankingService.rerank(
                pipeline.mcpResponses,
                analysis.originalQuery
            );
            pipeline.setRerankedResults(rerankedResults);

            // Step 5: Generate answer with context
            const generatedAnswer = await this.answerGenerationAgent.generateAnswer(
                analysis.originalQuery,
                rerankedResults
            );
            pipeline.setGeneratedAnswer(generatedAnswer);

            // Step 6: Agent validation (following agentic pattern)
            let validationResult = await this.validationAgent.validateAnswer(
                generatedAnswer,
                analysis.originalQuery,
                rerankedResults
            );
            pipeline.setValidationResult(validationResult);

            // Step 7: Agentic feedback loop for improvement
            let finalAnswer = generatedAnswer;
            while (pipeline.shouldRetry()) {
                const feedback = pipeline.getLatestFeedback();
                finalAnswer = await this.feedbackLoopService.improveAnswer(
                    finalAnswer,
                    feedback,
                    pipeline
                );
                
                validationResult = await this.validationAgent.validateAnswer(
                    finalAnswer,
                    analysis.originalQuery,
                    rerankedResults
                );
                pipeline.setValidationResult(validationResult);
                
                await this.eventBus.publish(new AnswerImprovedEvent(pipeline.id, finalAnswer));
            }

            const duration = Date.now() - startTime;
            await this.pipelineRepository.save(pipeline);
            await this.performanceMonitor.recordPipelineExecution(pipeline, duration);

            const validatedAnswer = new ValidatedAnswer(
                AnswerId.generate(),
                finalAnswer.content,
                validationResult.confidence,
                finalAnswer.sources,
                validationResult.checks,
                validationResult.isFactuallyCorrect,
                validationResult.isRelevant,
                validationResult.isComplete,
                validationResult.improvementSuggestions
            );

            await this.eventBus.publish(new AgenticQueryCompletedEvent(pipeline.id, validatedAnswer));
            return validatedAnswer;

        } catch (error) {
            const duration = Date.now() - startTime;
            await this.performanceMonitor.recordError(command.query, error, duration);
            throw error;
        }
    }
}

// Query Analysis Agent Service
@Injectable()
export class QueryAnalysisAgentService implements IQueryAnalysisAgent {
    constructor(
        private readonly llmGateway: ILLMGateway,
        private readonly mcpRegistry: IMCPServerRegistry,
        private readonly queryClassifier: IQueryClassifier,
        private readonly complexityAnalyzer: IComplexityAnalyzer
    ) {}

    async analyzeQuery(query: string): Promise<AgentQueryAnalysis> {
        const analysisPrompt = this.buildAnalysisPrompt(query);
        const llmResponse = await this.llmGateway.analyze(analysisPrompt);
        
        const queryType = await this.queryClassifier.classify(query);
        const complexity = await this.complexityAnalyzer.analyze(query, llmResponse);
        const requiresExternalData = this.determineDataRequirement(query, llmResponse);
        const suggestedServers = await this.mcpRegistry.getSuggestedServers(query, queryType);
        const rewriteRecommendations = this.generateRewriteRecommendations(query, llmResponse);
        
        return new AgentQueryAnalysis(
            query,
            queryType,
            complexity,
            requiresExternalData,
            suggestedServers,
            rewriteRecommendations,
            llmResponse.confidence
        );
    }

    private buildAnalysisPrompt(query: string): string {
        return `
As an AI agent, analyze this user query following the Agentic RAG pattern:

QUERY: "${query}"

Analyze for:
1. CLARITY: Is the query clear and unambiguous?
2. COMPLETENESS: Does it have enough context?
3. DATA REQUIREMENTS: Does it need external knowledge retrieval?
4. COMPLEXITY: Simple, moderate, or complex reasoning required?
5. AMBIGUITIES: Any unclear or multiple interpretations?
6. IMPROVEMENTS: How could this query be enhanced?

Provide structured analysis with confidence scores (0-1).
Format: JSON with clarity_score, completeness_score, requires_external_data, complexity_level, improvements_suggested.
        `.trim();
    }

    private determineDataRequirement(query: string, llmResponse: any): boolean {
        // Agent logic to determine if external data is needed
        const indicators = [
            'what is', 'tell me about', 'latest', 'current', 'recent',
            'statistics', 'data', 'facts', 'information about'
        ];
        
        const hasDataIndicators = indicators.some(indicator => 
            query.toLowerCase().includes(indicator)
        );
        
        return hasDataIndicators || llmResponse.requiresExternalData || false;
    }
}

// MCP Coordinator Service
@Injectable()
export class MCPCoordinatorService implements IMCPCoordinatorService {
    constructor(
        private readonly mcpServerPool: IMCPServerConnectionPool,
        private readonly loadBalancer: IMCPLoadBalancer,
        private readonly failureHandler: IMCPFailureHandler,
        private readonly responseAggregator: IMCPResponseAggregator
    ) {}

    async retrieveFromServers(
        serverIds: string[], 
        queries: string[]
    ): Promise<MCPResponse[]> {
        // Parallel retrieval following agentic pattern
        const retrievalTasks = serverIds.map(async serverId => {
            try {
                const connection = await this.mcpServerPool.getConnection(serverId);
                const results = await Promise.all(
                    queries.map(query => connection.search(query))
                );
                
                const aggregatedResults = await this.responseAggregator.aggregate(
                    results.flat(),
                    serverId
                );

                return new MCPResponse(
                    serverId,
                    aggregatedResults,
                    MCPResponseStatus.SUCCESS,
                    new Date()
                );
            } catch (error) {
                return await this.failureHandler.handleFailure(serverId, error);
            }
        });

        return await Promise.all(retrievalTasks);
    }
}

// Intelligent Reranking Service
@Injectable()
export class ReankingService implements IReankingService {
    constructor(
        private readonly llmGateway: ILLMGateway,
        private readonly semanticSimilarity: ISemanticSimilarityCalculator,
        private readonly relevanceScorer: IRelevanceScorer,
        private readonly qualityFilter: IQualityFilter
    ) {}

    async rerank(mcpResponses: MCPResponse[], originalQuery: string): Promise<RerankedResult[]> {
        const allDocuments = mcpResponses.flatMap(response => response.documents);
        
        if (allDocuments.length === 0) {
            return [];
        }

        // Step 1: Filter out low-quality results
        const qualityFiltered = await this.qualityFilter.filter(allDocuments);

        // Step 2: LLM-agent driven relevance scoring
        const rerankingPrompt = this.buildRerankingPrompt(originalQuery, qualityFiltered);
        const llmReranking = await this.llmGateway.rerank(rerankingPrompt);

        // Step 3: Combine semantic similarity with LLM ranking
        const rerankedResults = await Promise.all(
            qualityFiltered.map(async (doc, index) => {
                const semanticScore = await this.semanticSimilarity.calculate(originalQuery, doc.content);
                const llmScore = llmReranking.scores[index] || 0;
                const combinedScore = (semanticScore * 0.4) + (llmScore * 0.6);
                
                return new RerankedResult(
                    doc,
                    combinedScore,
                    semanticScore,
                    llmScore,
                    doc.serverId
                );
            })
        );

        return rerankedResults
            .sort((a, b) => b.combinedScore - a.combinedScore)
            .slice(0, 10); // Top 10 most relevant results
    }

    private buildRerankingPrompt(query: string, documents: MCPDocument[]): string {
        const docSummaries = documents.map((doc, i) => 
            `${i + 1}. ${doc.title}: ${doc.content.substring(0, 200)}...`
        ).join('\n');

        return `
As an AI agent, rerank these documents by relevance to the query.

QUERY: "${query}"

DOCUMENTS:
${docSummaries}

Rank documents 1-${documents.length} by relevance (1 = most relevant).
Consider: semantic relevance, factual accuracy, completeness, recency.
Provide: ranking_scores as array of numbers 0-1.
        `.trim();
    }
}

// Optimization Engine Service
@Injectable()
export class OptimizationEngineService {
    constructor(
        private readonly contextBuildRepository: IContextBuildRepository,
        private readonly experimentRunner: IExperimentRunner,
        private readonly statisticalAnalyzer: IStatisticalAnalyzer
    ) {}

    async runOptimizationCycle(buildId: BuildId): Promise<OptimizationResult> {
        const build = await this.contextBuildRepository.findById(buildId);
        if (!build) {
            throw new ContextBuildNotFoundError(buildId);
        }

        // Generate optimization candidates
        const candidates = this.generateOptimizationCandidates(build);
        
        // Run experiments
        const experiments = await Promise.all(
            candidates.map(candidate => this.experimentRunner.run(candidate))
        );

        // Analyze results
        const analysis = await this.statisticalAnalyzer.analyze(experiments);
        
        // Apply best optimization if significant
        if (analysis.bestCandidate && analysis.isSignificant) {
            this.applyOptimization(build, analysis.bestCandidate);
            await this.contextBuildRepository.save(build);
        }

        return new OptimizationResult(
            buildId,
            build.metrics,
            analysis.bestCandidate?.metrics || build.metrics,
            analysis.changes,
            analysis.confidence,
            new Date()
        );
    }

    private generateOptimizationCandidates(build: ContextBuild): OptimizationCandidate[] {
        const candidates: OptimizationCandidate[] = [];
        
        // Element removal candidates
        build.elements.forEach(element => {
            if (element.causalImpact < 0.1) {
                candidates.push(new RemoveElementCandidate(element.id));
            }
        });

        // Element reordering candidates
        candidates.push(new ReorderElementsCandidate(
            build.elements.sort((a, b) => b.causalImpact - a.causalImpact)
        ));

        // Token budget optimization
        candidates.push(new TokenBudgetCandidate(build.configuration.maxTokens * 0.9));
        candidates.push(new TokenBudgetCandidate(build.configuration.maxTokens * 1.1));

        return candidates;
    }
}
```

#### **3. Infrastructure Layer**

```typescript
// PostgreSQL Repository
@Injectable()
export class PostgreSQLContextBuildRepository implements IContextBuildRepository {
    constructor(
        private readonly dataSource: DataSource,
        private readonly mapper: ContextBuildMapper
    ) {}

    async save(build: ContextBuild): Promise<void> {
        const queryRunner = this.dataSource.createQueryRunner();
        await queryRunner.connect();
        await queryRunner.startTransaction();

        try {
            // Save context build
            await queryRunner.manager.upsert(ContextBuildEntity, {
                id: build.id.value,
                name: build.name,
                domain: build.domain,
                configuration: build.configuration,
                metrics: build.metrics,
                updatedAt: new Date()
            }, ['id']);

            // Save elements
            for (const element of build.elements) {
                await queryRunner.manager.upsert(ContextElementEntity, {
                    id: element.id.value,
                    buildId: build.id.value,
                    name: element.name,
                    content: element.content,
                    type: element.type,
                    tokenCount: element.tokenCount,
                    causalImpact: element.causalImpact,
                    tags: element.tags,
                    metadata: element.metadata
                }, ['id']);
            }

            await queryRunner.commitTransaction();
        } catch (error) {
            await queryRunner.rollbackTransaction();
            throw error;
        } finally {
            await queryRunner.release();
        }
    }

    async findById(id: BuildId): Promise<ContextBuild | null> {
        const buildEntity = await this.dataSource
            .getRepository(ContextBuildEntity)
            .findOne({
                where: { id: id.value },
                relations: ['elements']
            });

        return buildEntity ? this.mapper.toDomain(buildEntity) : null;
    }

    async findByDomain(domain: string): Promise<ContextBuild[]> {
        const entities = await this.dataSource
            .getRepository(ContextBuildEntity)
            .find({
                where: { domain },
                relations: ['elements'],
                order: { createdAt: 'DESC' }
            });

        return entities.map(entity => this.mapper.toDomain(entity));
    }
}

// LLM Gateway
@Injectable()
export class LLMGateway implements ILLMGateway {
    constructor(
        private readonly openAIClient: OpenAIClient,
        private readonly anthropicClient: AnthropicClient,
        private readonly circuitBreaker: CircuitBreaker,
        private readonly rateLimiter: RateLimiter
    ) {}

    async complete(request: LLMCompletionRequest): Promise<LLMCompletionResponse> {
        await this.rateLimiter.checkLimit(request.provider || 'openai');

        const provider = this.getProvider(request.provider || 'openai');
        
        return this.circuitBreaker.execute(async () => {
            const response = await provider.complete({
                prompt: request.prompt,
                model: request.model,
                maxTokens: request.maxTokens,
                temperature: request.temperature,
                stopSequences: request.stopSequences
            });

            return {
                content: response.content,
                tokenCount: response.tokenCount,
                confidence: this.calculateConfidence(response),
                provider: request.provider || 'openai',
                model: request.model,
                finishReason: response.finishReason
            };
        });
    }

    private getProvider(providerName: string): ILLMProvider {
        switch (providerName) {
            case 'openai':
                return this.openAIClient;
            case 'anthropic':
                return this.anthropicClient;
            default:
                throw new UnsupportedProviderError(providerName);
        }
    }

    private calculateConfidence(response: ProviderResponse): number {
        // Calculate confidence based on response characteristics
        let confidence = 0.8; // Base confidence

        // Adjust based on finish reason
        if (response.finishReason === 'stop') {
            confidence += 0.1;
        } else if (response.finishReason === 'length') {
            confidence -= 0.2;
        }

        // Adjust based on response length and coherence
        const responseLength = response.content.length;
        if (responseLength > 100 && responseLength < 2000) {
            confidence += 0.05;
        }

        return Math.max(0, Math.min(1, confidence));
    }
}
```

---

## 📊 **Database Schema**

### **PostgreSQL Tables - Agentic RAG Architecture**

```sql
-- Agentic Query Pipelines
CREATE TABLE agentic_query_pipelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_query TEXT NOT NULL,
    user_id UUID NOT NULL,
    status pipeline_status DEFAULT 'analyzing',
    analysis_result JSONB,
    rewritten_queries JSONB DEFAULT '[]',
    mcp_responses JSONB DEFAULT '[]',
    reranked_results JSONB DEFAULT '[]',
    generated_answer JSONB,
    validation_result JSONB,
    feedback_loops JSONB DEFAULT '[]',
    final_confidence DECIMAL(3,2),
    total_duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TYPE pipeline_status AS ENUM (
    'analyzing', 'rewriting', 'retrieving', 'reranking', 
    'generating', 'validating', 'needs_improvement', 'completed', 'failed'
);

CREATE INDEX idx_pipelines_user_id ON agentic_query_pipelines(user_id);
CREATE INDEX idx_pipelines_status ON agentic_query_pipelines(status);
CREATE INDEX idx_pipelines_created_at ON agentic_query_pipelines(created_at DESC);
CREATE INDEX idx_pipelines_completed ON agentic_query_pipelines(completed_at DESC) WHERE completed_at IS NOT NULL;

-- Agent Analysis Results
CREATE TABLE agent_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES agentic_query_pipelines(id) ON DELETE CASCADE,
    original_query TEXT NOT NULL,
    query_type query_analysis_type NOT NULL,
    complexity query_complexity NOT NULL,
    requires_external_data BOOLEAN DEFAULT false,
    suggested_mcp_servers TEXT[] DEFAULT '{}',
    rewrite_recommendations JSONB DEFAULT '[]',
    confidence DECIMAL(3,2) NOT NULL,
    agent_reasoning TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE query_analysis_type AS ENUM ('factual', 'analytical', 'creative', 'procedural', 'comparative');
CREATE TYPE query_complexity AS ENUM ('simple', 'moderate', 'complex', 'multi_step');

CREATE INDEX idx_analysis_pipeline_id ON agent_analysis_results(pipeline_id);
CREATE INDEX idx_analysis_query_type ON agent_analysis_results(query_type);
CREATE INDEX idx_analysis_complexity ON agent_analysis_results(complexity);

-- MCP Server Registry & Responses
CREATE TABLE mcp_servers (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    server_type mcp_server_type NOT NULL,
    endpoint_url TEXT NOT NULL,
    capabilities TEXT[] DEFAULT '{}',
    domain_specializations TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    health_status mcp_health_status DEFAULT 'unknown',
    last_health_check TIMESTAMP,
    avg_response_time_ms INTEGER,
    success_rate DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE mcp_server_type AS ENUM (
    'document_store', 'code_repository', 'database', 'api_service', 
    'knowledge_base', 'search_engine', 'file_system'
);
CREATE TYPE mcp_health_status AS ENUM ('healthy', 'degraded', 'unhealthy', 'unknown');

CREATE INDEX idx_mcp_servers_type ON mcp_servers(server_type);
CREATE INDEX idx_mcp_servers_active ON mcp_servers(is_active) WHERE is_active = true;
CREATE INDEX idx_mcp_servers_health ON mcp_servers(health_status);

-- MCP Responses
CREATE TABLE mcp_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES agentic_query_pipelines(id) ON DELETE CASCADE,
    server_id VARCHAR(100) REFERENCES mcp_servers(id),
    query_text TEXT NOT NULL,
    documents JSONB NOT NULL DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    status mcp_response_status DEFAULT 'success',
    response_time_ms INTEGER NOT NULL,
    document_count INTEGER DEFAULT 0,
    avg_relevance_score DECIMAL(3,2),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE mcp_response_status AS ENUM ('success', 'partial', 'failed', 'timeout');

CREATE INDEX idx_mcp_responses_pipeline_id ON mcp_responses(pipeline_id);
CREATE INDEX idx_mcp_responses_server_id ON mcp_responses(server_id);
CREATE INDEX idx_mcp_responses_status ON mcp_responses(status);

-- Reranked Results
CREATE TABLE reranked_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES agentic_query_pipelines(id) ON DELETE CASCADE,
    document_content TEXT NOT NULL,
    document_title VARCHAR(500),
    document_source VARCHAR(255),
    server_id VARCHAR(100),
    combined_score DECIMAL(4,3) NOT NULL,
    semantic_score DECIMAL(4,3),
    llm_relevance_score DECIMAL(4,3),
    rank_position INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reranked_pipeline_id ON reranked_results(pipeline_id);
CREATE INDEX idx_reranked_rank ON reranked_results(pipeline_id, rank_position);
CREATE INDEX idx_reranked_score ON reranked_results(combined_score DESC);

-- Validated Answers
CREATE TABLE validated_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES agentic_query_pipelines(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]',
    validation_checks JSONB NOT NULL DEFAULT '[]',
    is_factually_correct BOOLEAN NOT NULL,
    is_relevant BOOLEAN NOT NULL,
    is_complete BOOLEAN NOT NULL,
    improvement_suggestions TEXT[],
    quality_score DECIMAL(3,2),
    generation_model VARCHAR(100),
    validation_model VARCHAR(100),
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_validated_answers_pipeline_id ON validated_answers(pipeline_id);
CREATE INDEX idx_validated_answers_quality ON validated_answers(quality_score DESC);
CREATE INDEX idx_validated_answers_confidence ON validated_answers(confidence DESC);

-- Agent Performance Tracking
CREATE TABLE agent_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type agent_service_type NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    duration_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    confidence DECIMAL(3,2),
    error_message TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE agent_service_type AS ENUM (
    'query_analysis', 'query_rewriting', 'mcp_coordination', 
    'reranking', 'answer_generation', 'validation', 'feedback_loop'
);

CREATE INDEX idx_agent_perf_type ON agent_performance_metrics(agent_type);
CREATE INDEX idx_agent_perf_operation ON agent_performance_metrics(operation_type);
CREATE INDEX idx_agent_perf_success ON agent_performance_metrics(success);
CREATE INDEX idx_agent_perf_created_at ON agent_performance_metrics(created_at DESC);

-- Feedback Loops
CREATE TABLE feedback_loops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES agentic_query_pipelines(id) ON DELETE CASCADE,
    loop_iteration INTEGER NOT NULL,
    issues_identified TEXT[] NOT NULL,
    improvement_suggestions TEXT[] NOT NULL,
    actions_taken JSONB NOT NULL,
    before_quality_score DECIMAL(3,2),
    after_quality_score DECIMAL(3,2),
    improvement_achieved DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feedback_pipeline_id ON feedback_loops(pipeline_id);
CREATE INDEX idx_feedback_iteration ON feedback_loops(pipeline_id, loop_iteration);
```

### **Vector Database Schema** (Pinecone)

```typescript
// Vector embeddings for semantic search
interface ContextElementEmbedding {
    id: string; // element_id
    values: number[]; // 1536-dimensional embedding
    metadata: {
        buildId: string;
        elementName: string;
        elementType: string;
        tokenCount: number;
        causalImpact: number;
        tags: string[];
    };
}

interface QueryEmbedding {
    id: string; // query_id
    values: number[]; // 1536-dimensional embedding
    metadata: {
        queryText: string;
        userId: string;
        buildId: string;
        timestamp: string;
    };
}
```

---

## 🔌 **API Specifications**

### **REST API Endpoints**

```yaml
# OpenAPI 3.0 Specification
openapi: 3.0.0
info:
  title: Core RAG Module API
  version: 1.0.0

paths:
  /context-builds:
    post:
      summary: Create a new context build
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
                domain:
                  type: string
                  maxLength: 100
                configuration:
                  type: object
                  properties:
                    maxTokens:
                      type: integer
                      minimum: 1000
                      maximum: 100000
                    maxElements:
                      type: integer
                      minimum: 1
                      maximum: 50
                    optimizationEnabled:
                      type: boolean
              required: [name, domain]
      responses:
        201:
          description: Context build created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContextBuild'
        400:
          description: Invalid request data

    get:
      summary: List context builds
      parameters:
        - name: domain
          in: query
          schema:
            type: string
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
      responses:
        200:
          description: List of context builds
          content:
            application/json:
              schema:
                type: object
                properties:
                  builds:
                    type: array
                    items:
                      $ref: '#/components/schemas/ContextBuild'
                  total:
                    type: integer
                  limit:
                    type: integer
                  offset:
                    type: integer

  /context-builds/{id}:
    get:
      summary: Get context build by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Context build details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContextBuildDetail'
        404:
          description: Context build not found

    put:
      summary: Update context build
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
              $ref: '#/components/schemas/UpdateContextBuildRequest'
      responses:
        200:
          description: Context build updated
        404:
          description: Context build not found

    delete:
      summary: Delete context build
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        204:
          description: Context build deleted
        404:
          description: Context build not found

  /context-builds/{id}/elements:
    post:
      summary: Add element to context build
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
                name:
                  type: string
                  maxLength: 255
                content:
                  type: string
                  maxLength: 10000
                type:
                  type: string
                  enum: [text, code, data, instruction, example]
                tags:
                  type: array
                  items:
                    type: string
              required: [name, content, type]
      responses:
        201:
          description: Element added
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContextElement'

    get:
      summary: List elements in context build
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: List of context elements
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ContextElement'

  /context-builds/{id}/elements/{elementId}:
    put:
      summary: Update context element
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: elementId
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
              $ref: '#/components/schemas/UpdateElementRequest'
      responses:
        200:
          description: Element updated

    delete:
      summary: Remove element from context build
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: elementId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        204:
          description: Element removed

  /context-builds/{id}/queries:
    post:
      summary: Process query against context build
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
                query:
                  type: string
                  maxLength: 1000
                model:
                  type: string
                  enum: [gpt-4, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet]
                  default: gpt-4
                maxTokens:
                  type: integer
                  minimum: 100
                  maximum: 4000
                  default: 1000
                temperature:
                  type: number
                  minimum: 0
                  maximum: 2
                  default: 0.7
              required: [query]
      responses:
        200:
          description: Query processed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QueryResult'
        400:
          description: Invalid query
        500:
          description: LLM processing error

  /context-builds/{id}/optimize:
    post:
      summary: Run optimization on context build
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
                optimizationType:
                  type: string
                  enum: [performance, cost, quality]
                  default: performance
                maxDuration:
                  type: integer
                  minimum: 300
                  maximum: 3600
                  default: 1800
      responses:
        202:
          description: Optimization started
          content:
            application/json:
              schema:
                type: object
                properties:
                  optimizationId:
                    type: string
                    format: uuid
                  estimatedDuration:
                    type: integer

  /context-builds/{id}/optimize/{optimizationId}:
    get:
      summary: Get optimization status
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: optimizationId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Optimization status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OptimizationResult'

components:
  schemas:
    ContextBuild:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        domain:
          type: string
        configuration:
          type: object
        metrics:
          type: object
        version:
          type: integer
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
      
    ContextElement:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        content:
          type: string
        type:
          type: string
        tokenCount:
          type: integer
        causalImpact:
          type: number
        tags:
          type: array
          items:
            type: string
        position:
          type: integer
        
    QueryResult:
      type: object
      properties:
        queryId:
          type: string
          format: uuid
        response:
          type: string
        selectedElements:
          type: array
          items:
            type: string
            format: uuid
        tokenCount:
          type: integer
        duration:
          type: integer
        confidence:
          type: number
        provider:
          type: string
        model:
          type: string
```

---

## 🧪 **Testing Requirements**

### **Unit Tests** (TDD Cycles 1, 2, 7)

```typescript
// TDD Cycle 1: Context Build Management
describe('ContextBuild', () => {
    describe('addElement', () => {
        it('should add element when within token budget', () => {
            // RED: Test fails initially
            const build = new ContextBuild(
                BuildId.generate(),
                'Test Build',
                'testing',
                [],
                new BuildConfiguration(1000, 10),
                new PerformanceMetrics()
            );
            
            const element = new ContextElement(
                ElementId.generate(),
                'Test Element',
                'Test content',
                ElementType.TEXT,
                100,
                0.5
            );
            
            build.addElement(element);
            
            expect(build.elements).toHaveLength(1);
            expect(build.elements[0]).toBe(element);
        });

        it('should throw error when token budget exceeded', () => {
            // RED: Test fails initially
            const build = new ContextBuild(
                BuildId.generate(),
                'Test Build',
                'testing',
                [],
                new BuildConfiguration(100, 10), // Small budget
                new PerformanceMetrics()
            );
            
            const element = new ContextElement(
                ElementId.generate(),
                'Large Element',
                'Very long content that exceeds budget',
                ElementType.TEXT,
                200, // Exceeds budget
                0.5
            );
            
            expect(() => build.addElement(element))
                .toThrow(TokenBudgetExceededError);
        });
    });
});

// TDD Cycle 2: Query Processing
describe('QueryProcessingService', () => {
    let service: QueryProcessingService;
    let mockRepository: jest.Mocked<IContextBuildRepository>;
    let mockLLMGateway: jest.Mocked<ILLMGateway>;

    beforeEach(() => {
        mockRepository = createMockRepository();
        mockLLMGateway = createMockLLMGateway();
        service = new QueryProcessingService(mockRepository, mockLLMGateway);
    });

    describe('processQuery', () => {
        it('should process query successfully', async () => {
            // RED: Test fails initially
            const buildId = BuildId.generate();
            const mockBuild = createMockContextBuild(buildId);
            mockRepository.findById.mockResolvedValue(mockBuild);
            mockLLMGateway.complete.mockResolvedValue({
                content: 'Test response',
                tokenCount: 50,
                confidence: 0.9
            });

            const command = new ProcessQueryCommand(
                buildId,
                'test query',
                UserId.generate()
            );

            const result = await service.processQuery(command);

            expect(result.response).toBe('Test response');
            expect(result.tokenCount).toBe(50);
            expect(result.confidence).toBe(0.9);
        });
    });
});

// TDD Cycle 7: Optimization Engine
describe('OptimizationEngineService', () => {
    describe('runOptimizationCycle', () => {
        it('should improve performance metrics', async () => {
            // RED: Test fails initially
            const buildId = BuildId.generate();
            const mockBuild = createMockContextBuild(buildId);
            const originalScore = mockBuild.metrics.overallScore;
            
            const result = await service.runOptimizationCycle(buildId);
            
            expect(result.optimizedMetrics.overallScore)
                .toBeGreaterThan(originalScore);
            expect(result.isSignificant()).toBe(true);
        });
    });
});
```

### **Integration Tests**

```typescript
describe('Core RAG Integration', () => {
    let app: INestApplication;
    let repository: IContextBuildRepository;

    beforeAll(async () => {
        const moduleRef = await Test.createTestingModule({
            imports: [CoreRAGModule],
        }).compile();

        app = moduleRef.createNestApplication();
        repository = app.get(IContextBuildRepository);
        await app.init();
    });

    describe('Context Build Lifecycle', () => {
        it('should create, modify, and optimize context build', async () => {
            // Create context build
            const createResponse = await request(app.getHttpServer())
                .post('/context-builds')
                .send({
                    name: 'Integration Test Build',
                    domain: 'testing',
                    configuration: {
                        maxTokens: 2000,
                        maxElements: 10
                    }
                });

            expect(createResponse.status).toBe(201);
            const buildId = createResponse.body.id;

            // Add elements
            await request(app.getHttpServer())
                .post(`/context-builds/${buildId}/elements`)
                .send({
                    name: 'Test Element 1',
                    content: 'First test element content',
                    type: 'text'
                });

            // Process query
            const queryResponse = await request(app.getHttpServer())
                .post(`/context-builds/${buildId}/queries`)
                .send({
                    query: 'What is this about?'
                });

            expect(queryResponse.status).toBe(200);
            expect(queryResponse.body.response).toBeDefined();

            // Run optimization
            const optimizeResponse = await request(app.getHttpServer())
                .post(`/context-builds/${buildId}/optimize`)
                .send({
                    optimizationType: 'performance'
                });

            expect(optimizeResponse.status).toBe(202);
        });
    });
});
```

---

## 🚀 **Deployment Requirements**

### **Docker Configuration**

```dockerfile
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

USER nestjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "dist/main.js"]
```

### **Environment Configuration**

```bash
# .env.production
NODE_ENV=production
PORT=3000

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/selfrag_core
DATABASE_SSL=true
DATABASE_POOL_SIZE=20

# Vector Database
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=production
PINECONE_INDEX_NAME=context-elements

# LLM Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Rate Limiting
OPENAI_REQUESTS_PER_MINUTE=3000
ANTHROPIC_REQUESTS_PER_MINUTE=1000

# Optimization
OPTIMIZATION_MAX_DURATION=1800
OPTIMIZATION_EXPERIMENT_TIMEOUT=300
BAYESIAN_OPTIMIZATION_ITERATIONS=50

# Caching
REDIS_URL=redis://redis:6379
CACHE_TTL_SECONDS=3600

# Monitoring
LOG_LEVEL=info
METRICS_PORT=9090
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Create context builds with name, domain, and configuration
- [ ] Add, update, and remove context elements
- [ ] Process queries with < 2 second response time
- [ ] Integrate with OpenAI and Anthropic LLM providers
- [ ] Run optimization cycles that improve performance by 15%+
- [ ] Track and report performance metrics

### **Performance Acceptance**
- [ ] Support 1,000 concurrent query requests
- [ ] Query processing time < 2 seconds for 95% of requests
- [ ] Optimization cycle completes within 30 minutes
- [ ] Token efficiency improvement of 15%+ through optimization

### **Quality Acceptance**
- [ ] Response quality improvement of 20%+ through optimization
- [ ] 99.5% uptime for query processing
- [ ] Confidence scores calculated for all responses
- [ ] Proper error handling for LLM provider failures

This Core RAG Module serves as the foundation for all RAG functionality in the platform, providing robust context management, query processing, and continuous optimization capabilities. 