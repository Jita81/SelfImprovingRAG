# Self-Improving RAG Platform: Project Structure

## Repository Organization

```
SelfImprovingRAG/
├── README.md
├── docker-compose.yml
├── .github/
│   └── workflows/
│       ├── orchestrator-ci.yml
│       ├── core-rag-ci.yml
│       └── [module-name]-ci.yml
│
├── docs/
│   ├── architecture/
│   │   ├── modular_architecture_plan.md
│   │   ├── tdd_cycles_self_improving_rag.md
│   │   └── api_contracts.md
│   └── deployment/
│       ├── kubernetes/
│       └── docker/
│
├── shared/
│   ├── contracts/           # Shared interfaces and DTOs
│   ├── events/             # Event definitions
│   ├── testing/            # Shared testing utilities
│   └── monitoring/         # Shared monitoring tools
│
├── modules/
│   │
│   ├── orchestrator/       # ~25k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── WorkflowController.ts
│   │   │   │   │   ├── AuthController.ts
│   │   │   │   │   └── GatewayController.ts
│   │   │   │   ├── middleware/
│   │   │   │   │   ├── AuthMiddleware.ts
│   │   │   │   │   ├── RateLimitMiddleware.ts
│   │   │   │   │   └── LoggingMiddleware.ts
│   │   │   │   └── routes/
│   │   │   │       └── index.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── OrchestratorService.ts
│   │   │   │   │   ├── ModuleDiscoveryService.ts
│   │   │   │   │   └── WorkflowEngineService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── ProcessUserQueryUseCase.ts
│   │   │   │   │   ├── RunOptimizationWorkflowUseCase.ts
│   │   │   │   │   └── HandleUserActionUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IModuleGateway.ts
│   │   │   │       └── IWorkflowEngine.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── Workflow.ts
│   │   │   │   │   ├── Module.ts
│   │   │   │   │   └── UserSession.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── ModuleEndpoint.ts
│   │   │   │   │   └── WorkflowStatus.ts
│   │   │   │   └── services/
│   │   │   │       └── WorkflowOrchestrationService.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── gateways/
│   │   │       │   ├── ModuleHttpGateway.ts
│   │   │       │   └── EventBusGateway.ts
│   │   │       ├── repositories/
│   │   │       │   └── WorkflowRepository.ts
│   │   │       └── config/
│   │   │           └── ModuleConfiguration.ts
│   │   │
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── e2e/
│   │   │
│   │   ├── docs/
│   │   │   └── orchestrator_module_readme.md
│   │   │
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── core-rag/            # ~28k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── ContextBuildController.ts
│   │   │   │   │   ├── OptimizationController.ts
│   │   │   │   │   └── QueryController.ts
│   │   │   │   └── models/
│   │   │   │       ├── CreateContextBuildRequest.ts
│   │   │   │       ├── OptimizationRequest.ts
│   │   │   │       └── QueryRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── ContextBuildService.ts
│   │   │   │   │   ├── OptimizationService.ts
│   │   │   │   │   └── QueryProcessingService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── CreateContextBuildUseCase.ts
│   │   │   │   │   ├── OptimizeBuildUseCase.ts
│   │   │   │   │   └── ProcessQueryUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IContextBuildRepository.ts
│   │   │   │       ├── ILLMGateway.ts
│   │   │   │       └── IOptimizationEngine.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── ContextBuild.ts
│   │   │   │   │   ├── ContextElement.ts
│   │   │   │   │   └── OptimizationResult.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── BuildId.ts
│   │   │   │   │   ├── PerformanceMetrics.ts
│   │   │   │   │   ├── TokenBudget.ts
│   │   │   │   │   └── SuccessRate.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── OptimizationAlgorithm.ts
│   │   │   │   │   └── QueryAnalysisService.ts
│   │   │   │   └── events/
│   │   │   │       ├── ContextBuildCreatedEvent.ts
│   │   │   │       ├── OptimizationCompletedEvent.ts
│   │   │   │       └── QueryProcessedEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   ├── PostgresContextBuildRepository.ts
│   │   │       │   └── RedisOptimizationCache.ts
│   │   │       ├── gateways/
│   │   │       │   ├── OpenAIGateway.ts
│   │   │       │   └── AnthropicGateway.ts
│   │   │       └── config/
│   │   │           └── LLMConfiguration.ts
│   │   │
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   │   ├── domain/
│   │   │   │   ├── application/
│   │   │   │   └── infrastructure/
│   │   │   ├── integration/
│   │   │   │   ├── ContextBuildIntegrationTests.ts
│   │   │   │   └── OptimizationIntegrationTests.ts
│   │   │   └── e2e/
│   │   │       └── CoreRAGEndToEndTests.ts
│   │   │
│   │   ├── docs/
│   │   │   └── core_rag_module_readme.md
│   │   │
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── user-management/     # ~26k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── UserController.ts
│   │   │   │   │   ├── GamificationController.ts
│   │   │   │   │   └── ProfileController.ts
│   │   │   │   └── models/
│   │   │   │       ├── CreateUserRequest.ts
│   │   │   │       ├── UpdateProfileRequest.ts
│   │   │   │       └── AddExperienceRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── UserManagementService.ts
│   │   │   │   │   ├── GamificationService.ts
│   │   │   │   │   └── ProfileService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── CreateUserUseCase.ts
│   │   │   │   │   ├── AddExperienceUseCase.ts
│   │   │   │   │   └── UpdateProfileUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IUserRepository.ts
│   │   │   │       └── IGamificationRepository.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── User.ts
│   │   │   │   │   ├── UserProfile.ts
│   │   │   │   │   └── GamificationStats.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── UserId.ts
│   │   │   │   │   ├── Level.ts
│   │   │   │   │   ├── ExperiencePoints.ts
│   │   │   │   │   └── WinStreak.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── LevelCalculationService.ts
│   │   │   │   │   └── ExperienceCalculationService.ts
│   │   │   │   └── events/
│   │   │   │       ├── UserCreatedEvent.ts
│   │   │   │       ├── LevelUpEvent.ts
│   │   │   │       └── ExperienceGainedEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   ├── PostgresUserRepository.ts
│   │   │       │   └── RedisSessionRepository.ts
│   │   │       ├── services/
│   │   │       │   └── HashingService.ts
│   │   │       └── config/
│   │   │           └── AuthConfiguration.ts
│   │   │
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── achievement-social/  # ~27k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── AchievementController.ts
│   │   │   │   │   ├── LeaderboardController.ts
│   │   │   │   │   └── SocialController.ts
│   │   │   │   └── models/
│   │   │   │       ├── AchievementRequest.ts
│   │   │   │       └── LeaderboardRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── AchievementService.ts
│   │   │   │   │   ├── LeaderboardService.ts
│   │   │   │   │   └── SocialComparisonService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── CheckAchievementUnlocksUseCase.ts
│   │   │   │   │   ├── UpdateLeaderboardUseCase.ts
│   │   │   │   │   └── GetUserRankingUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IAchievementRepository.ts
│   │   │   │       ├── ILeaderboardRepository.ts
│   │   │   │       └── IAchievementTrigger.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── Achievement.ts
│   │   │   │   │   ├── Leaderboard.ts
│   │   │   │   │   └── LeaderboardEntry.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── AchievementId.ts
│   │   │   │   │   ├── AchievementRarity.ts
│   │   │   │   │   ├── Rank.ts
│   │   │   │   │   └── LeaderboardPeriod.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── RankingCalculationService.ts
│   │   │   │   │   ├── AchievementTriggerService.ts
│   │   │   │   │   └── CompetitionService.ts
│   │   │   │   └── events/
│   │   │   │       ├── AchievementUnlockedEvent.ts
│   │   │   │       └── LeaderboardUpdatedEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   ├── PostgresAchievementRepository.ts
│   │   │       │   └── RedisLeaderboardCache.ts
│   │   │       ├── triggers/
│   │   │       │   ├── SuccessRateTrigger.ts
│   │   │       │   ├── WinStreakTrigger.ts
│   │   │       │   └── OptimizationCountTrigger.ts
│   │   │       └── calculators/
│   │   │           └── CompositeScoreCalculator.ts
│   │   │
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── notification/        # ~24k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── NotificationController.ts
│   │   │   │   │   └── PreferencesController.ts
│   │   │   │   ├── websocket/
│   │   │   │   │   └── NotificationWebSocketHandler.ts
│   │   │   │   └── models/
│   │   │   │       ├── SendNotificationRequest.ts
│   │   │   │       └── UpdatePreferencesRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── NotificationService.ts
│   │   │   │   │   ├── DeliveryService.ts
│   │   │   │   │   └── PreferencesService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── SendNotificationUseCase.ts
│   │   │   │   │   ├── UpdatePreferencesUseCase.ts
│   │   │   │   │   └── GetNotificationHistoryUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── INotificationRepository.ts
│   │   │   │       ├── IDeliveryChannel.ts
│   │   │   │       └── IPreferencesRepository.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── Notification.ts
│   │   │   │   │   ├── NotificationPreferences.ts
│   │   │   │   │   └── DeliveryResult.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── NotificationId.ts
│   │   │   │   │   ├── NotificationType.ts
│   │   │   │   │   ├── NotificationPriority.ts
│   │   │   │   │   └── DeliveryChannel.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── NotificationFilterService.ts
│   │   │   │   │   └── DeliveryStrategyService.ts
│   │   │   │   └── events/
│   │   │   │       ├── NotificationSentEvent.ts
│   │   │   │       └── NotificationFailedEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   ├── PostgresNotificationRepository.ts
│   │   │       │   └── RedisPreferencesCache.ts
│   │   │       ├── channels/
│   │   │       │   ├── WebSocketDeliveryChannel.ts
│   │   │       │   ├── EmailDeliveryChannel.ts
│   │   │       │   └── PushNotificationChannel.ts
│   │   │       └── websocket/
│   │   │           └── WebSocketConnectionManager.ts
│   │   │
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── data-integration/    # ~29k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── DataSourceController.ts
│   │   │   │   │   ├── MCPServerController.ts
│   │   │   │   │   └── IngestionController.ts
│   │   │   │   └── models/
│   │   │   │       ├── DataSourceRequest.ts
│   │   │   │       └── SyncRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── DataIngestionService.ts
│   │   │   │   │   ├── MCPServerService.ts
│   │   │   │   │   ├── QualityAssessmentService.ts
│   │   │   │   │   └── KnowledgeExtractionService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── IngestDataFromSourceUseCase.ts
│   │   │   │   │   ├── SyncMCPServerUseCase.ts
│   │   │   │   │   └── AssessDataQualityUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IDataSourceRepository.ts
│   │   │   │       ├── IKnowledgeExtractor.ts
│   │   │   │       ├── IQualityAssessor.ts
│   │   │   │       └── IExternalAPIClient.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── DataSource.ts
│   │   │   │   │   ├── MCPServer.ts
│   │   │   │   │   ├── ExtractedKnowledge.ts
│   │   │   │   │   └── QualityMetrics.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── DataSourceId.ts
│   │   │   │   │   ├── DataSourceType.ts
│   │   │   │   │   ├── QualityScore.ts
│   │   │   │   │   └── SyncStatus.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── DataClassificationService.ts
│   │   │   │   │   ├── QualityCalculationService.ts
│   │   │   │   │   └── KnowledgeDeduplicationService.ts
│   │   │   │   └── events/
│   │   │   │       ├── DataIngestionCompletedEvent.ts
│   │   │   │       ├── MCPServerSyncedEvent.ts
│   │   │   │       └── QualityAssessmentCompletedEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   ├── PostgresDataSourceRepository.ts
│   │   │       │   └── ElasticsearchKnowledgeRepository.ts
│   │   │       ├── clients/
│   │   │       │   ├── SlackAPIClient.ts
│   │   │       │   ├── GitHubAPIClient.ts
│   │   │       │   ├── JiraAPIClient.ts
│   │   │       │   └── ConfluenceAPIClient.ts
│   │   │       ├── extractors/
│   │   │       │   ├── SlackMessageExtractor.ts
│   │   │       │   ├── GitHubCodeExtractor.ts
│   │   │       │   └── JiraTicketExtractor.ts
│   │   │       └── pipelines/
│   │   │           ├── DataIngestionPipeline.ts
│   │   │           └── QualityAssessmentPipeline.ts
│   │   │
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── analytics/           # ~29k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── PerformanceController.ts
│   │   │   │   │   ├── ABTestController.ts
│   │   │   │   │   └── AnalyticsController.ts
│   │   │   │   └── models/
│   │   │   │       ├── CreateABTestRequest.ts
│   │   │   │       └── AnalyticsRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── PerformanceTrackingService.ts
│   │   │   │   │   ├── ABTestingService.ts
│   │   │   │   │   ├── AnalyticsService.ts
│   │   │   │   │   └── TrendAnalysisService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── TrackPerformanceUseCase.ts
│   │   │   │   │   ├── CreateABTestUseCase.ts
│   │   │   │   │   ├── AnalyzeABTestUseCase.ts
│   │   │   │   │   └── GenerateAnalyticsUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IPerformanceRepository.ts
│   │   │   │       ├── IABTestRepository.ts
│   │   │   │       ├── IAnalyticsRepository.ts
│   │   │   │       └── IStatisticalTestingService.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── PerformanceRecord.ts
│   │   │   │   │   ├── ABTest.ts
│   │   │   │   │   ├── AnalyticsReport.ts
│   │   │   │   │   └── TrendAnalysis.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── ABTestId.ts
│   │   │   │   │   ├── TrafficAllocation.ts
│   │   │   │   │   ├── SignificanceLevel.ts
│   │   │   │   │   └── AnalyticsTimeWindow.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── StatisticalTestingService.ts
│   │   │   │   │   ├── TrendDetectionService.ts
│   │   │   │   │   └── ROICalculationService.ts
│   │   │   │   └── events/
│   │   │   │       ├── ABTestStartedEvent.ts
│   │   │   │       ├── ABTestCompletedEvent.ts
│   │   │   │       └── PerformanceRecordedEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   ├── PostgresPerformanceRepository.ts
│   │   │       │   ├── InfluxDBTimeSeriesRepository.ts
│   │   │       │   └── RedisABTestCache.ts
│   │   │       ├── statistics/
│   │   │       │   ├── TTestCalculator.ts
│   │   │       │   ├── ChiSquareCalculator.ts
│   │   │       │   └── BayesianABTestCalculator.ts
│   │   │       └── analytics/
│   │   │           ├── GoogleAnalyticsIntegration.ts
│   │   │           └── PrometheusMetricsExporter.ts
│   │   │
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── comparison/          # ~23k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   └── ComparisonController.ts
│   │   │   │   └── models/
│   │   │   │       └── ComparisonRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── BuildComparisonService.ts
│   │   │   │   │   └── StatisticalTestingService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── CompareBuildsUseCase.ts
│   │   │   │   │   └── GenerateRecommendationsUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IComparisonRepository.ts
│   │   │   │       └── IBuildRepository.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── BuildComparison.ts
│   │   │   │   │   ├── PerformanceDifference.ts
│   │   │   │   │   └── ComparisonRecommendation.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── StatisticalSignificance.ts
│   │   │   │   │   ├── ConfidenceInterval.ts
│   │   │   │   │   └── EffectSize.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── DifferenceCalculationService.ts
│   │   │   │   │   └── RecommendationGenerationService.ts
│   │   │   │   └── events/
│   │   │   │       └── ComparisonCompletedEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   └── PostgresComparisonRepository.ts
│   │   │       └── calculators/
│   │   │           ├── EffectSizeCalculator.ts
│   │   │           └── PowerAnalysisCalculator.ts
│   │   │
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── token-betting/       # ~22k tokens
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── BettingController.ts
│   │   │   │   │   └── WalletController.ts
│   │   │   │   └── models/
│   │   │   │       ├── PlaceBetRequest.ts
│   │   │   │       └── WalletRequest.ts
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── TokenBettingService.ts
│   │   │   │   │   ├── WalletService.ts
│   │   │   │   │   └── OddsCalculationService.ts
│   │   │   │   ├── usecases/
│   │   │   │   │   ├── PlaceBetUseCase.ts
│   │   │   │   │   ├── ResolveBetUseCase.ts
│   │   │   │   │   └── ManageWalletUseCase.ts
│   │   │   │   └── interfaces/
│   │   │   │       ├── IBetRepository.ts
│   │   │   │       └── IWalletRepository.ts
│   │   │   │
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── TokenBet.ts
│   │   │   │   │   ├── TokenWallet.ts
│   │   │   │   │   └── BetResult.ts
│   │   │   │   ├── valueobjects/
│   │   │   │   │   ├── BetId.ts
│   │   │   │   │   ├── TokenAmount.ts
│   │   │   │   │   ├── BettingOdds.ts
│   │   │   │   │   └── BetStatus.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── OddsCalculationService.ts
│   │   │   │   │   └── PayoutCalculationService.ts
│   │   │   │   └── events/
│   │   │   │       ├── BetPlacedEvent.ts
│   │   │   │       ├── BetResolvedEvent.ts
│   │   │   │       └── TokensTransferredEvent.ts
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── repositories/
│   │   │       │   ├── PostgresBetRepository.ts
│   │   │       │   └── RedisWalletCache.ts
│   │   │       └── calculators/
│   │   │           └── MarketOddsCalculator.ts
│   │   │
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── statistical/         # ~29k tokens
│       ├── src/
│       │   ├── api/
│       │   │   ├── controllers/
│       │   │   │   ├── UncertaintyController.ts
│       │   │   │   └── CausalInferenceController.ts
│       │   │   └── models/
│       │   │       ├── UncertaintyAnalysisRequest.ts
│       │   │       └── CausalAnalysisRequest.ts
│       │   │
│       │   ├── application/
│       │   │   ├── services/
│       │   │   │   ├── UncertaintyQuantificationService.ts
│       │   │   │   ├── CausalInferenceService.ts
│       │   │   │   └── BayesianAnalysisService.ts
│       │   │   ├── usecases/
│       │   │   │   ├── QuantifyUncertaintyUseCase.ts
│       │   │   │   ├── PerformCausalAnalysisUseCase.ts
│       │   │   │   └── CalculatePACBoundsUseCase.ts
│       │   │   └── interfaces/
│       │   │       ├── IBayesianInferenceEngine.ts
│       │   │       ├── ICausalDiscoveryAlgorithm.ts
│       │   │       └── IStatisticalModelRepository.ts
│       │   │
│       │   ├── domain/
│       │   │   ├── entities/
│       │   │   │   ├── UncertaintyAnalysis.ts
│       │   │   │   ├── CausalGraph.ts
│       │   │   │   ├── CausalEffect.ts
│       │   │   │   └── BayesianModel.ts
│       │   │   ├── valueobjects/
│       │   │   │   ├── UncertaintyType.ts
│       │   │   │   ├── ConfidenceInterval.ts
│       │   │   │   ├── CausalNode.ts
│       │   │   │   ├── CausalEdge.ts
│       │   │   │   └── PACBounds.ts
│       │   │   ├── services/
│       │   │   │   ├── UncertaintyDecompositionService.ts
│       │   │   │   ├── CausalDiscoveryService.ts
│       │   │   │   └── InterventionEstimationService.ts
│       │   │   └── events/
│       │   │       ├── UncertaintyAnalysisCompletedEvent.ts
│       │   │       └── CausalAnalysisCompletedEvent.ts
│       │   │
│       │   └── infrastructure/
│       │       ├── repositories/
│       │       │   ├── PostgresStatisticalModelRepository.ts
│       │       │   └── NumpyArrayRepository.ts
│       │       ├── engines/
│       │       │   ├── PyMCBayesianEngine.ts
│       │       │   ├── CausalMLEngine.ts
│       │       │   └── SklearnModelEngine.ts
│       │       ├── algorithms/
│       │       │   ├── PCAlgorithm.ts
│       │       │   ├── GESAlgorithm.ts
│       │       │   └── DoWhydAlgorithm.ts
│       │       └── calculators/
│       │           ├── PACBayesianCalculator.ts
│       │           ├── MonteCarloDropoutCalculator.ts
│       │           └── PropensityScoreCalculator.ts
│       │
│       ├── tests/
│       ├── docs/
│       ├── Dockerfile
│       ├── package.json
│       ├── requirements.txt  # Python dependencies for statistical libraries
│       └── tsconfig.json
│
├── infrastructure/
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── orchestrator/
│   │   ├── core-rag/
│   │   └── [module-name]/
│   │
│   ├── docker/
│   │   ├── base/
│   │   │   ├── node.Dockerfile
│   │   │   └── python.Dockerfile
│   │   └── monitoring/
│   │       ├── prometheus.yml
│   │       └── grafana/
│   │
│   ├── terraform/
│   │   ├── aws/
│   │   ├── gcp/
│   │   └── azure/
│   │
│   └── scripts/
│       ├── deploy.sh
│       ├── test-all-modules.sh
│       └── health-check.sh
│
├── tools/
│   ├── cli/
│   │   └── selfrag-cli/
│   ├── monitoring/
│   │   ├── dashboard/
│   │   └── alerts/
│   └── testing/
│       ├── integration-test-runner/
│       └── load-testing/
│
└── examples/
    ├── postman/
    │   └── SelfRAG-API-Collection.json
    ├── sample-data/
    │   ├── context-builds.json
    │   └── test-users.json
    └── tutorials/
        ├── getting-started.md
        ├── creating-custom-modules.md
        └── deployment-guide.md
```

## Key Structure Features

### **1. Module Independence**
- Each module is a complete microservice
- Own `package.json`, `Dockerfile`, and dependencies
- Independent CI/CD pipelines
- Can be deployed and scaled separately

### **2. Standardized Structure**
- All modules follow the same hexagonal architecture
- Consistent folder naming and organization
- Shared interfaces in `/shared/contracts/`
- Common testing patterns

### **3. Documentation Strategy**
- Each module: ~30k token documentation limit
- Shared architecture docs in `/docs/`
- API contracts in `/shared/contracts/`
- Deployment guides in `/infrastructure/`

### **4. Testing Strategy**
- Unit tests within each module
- Integration tests for module interactions
- E2E tests in orchestrator
- Shared testing utilities in `/shared/testing/`

### **5. Deployment Ready**
- Docker containers for each module
- Kubernetes manifests for orchestration
- Terraform for infrastructure as code
- Monitoring and observability built-in

This structure supports the full 19 TDD cycles across 10 independent modules, each designed to be under 30k tokens with comprehensive documentation and testing. 