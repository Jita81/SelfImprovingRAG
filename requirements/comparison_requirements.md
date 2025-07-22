# Comparison Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: Comparison  
**Size Estimate**: ~23k tokens  
**Priority**: 3 (Advanced)  
**TDD Cycles**: 15  
**Branch**: `module/comparison`  
**Cursor Window**: #9  
**Dependencies**: Orchestrator, Core RAG, Analytics Modules  

### **Purpose**
Provides statistical comparison capabilities for context builds, enabling users to objectively compare performance between different optimization approaches with statistical significance testing.

---

## 🎯 **Functional Requirements**

### **FR-1: Build Comparison** (TDD Cycle 15)
- **FR-1.1**: Compare performance metrics between two context builds
- **FR-1.2**: Calculate statistical significance of performance differences
- **FR-1.3**: Generate confidence intervals for metric comparisons
- **FR-1.4**: Support multiple comparison metrics (success rate, token efficiency, response time)
- **FR-1.5**: Handle different sample sizes and statistical power analysis
- **FR-1.6**: Provide visual representations of comparison results

### **FR-2: Statistical Testing**
- **FR-2.1**: Perform t-tests for continuous metrics
- **FR-2.2**: Conduct chi-square tests for categorical outcomes
- **FR-2.3**: Calculate effect sizes (Cohen's d, odds ratios)
- **FR-2.4**: Handle multiple comparison corrections (Bonferroni, FDR)
- **FR-2.5**: Support non-parametric tests when assumptions violated
- **FR-2.6**: Provide statistical interpretation and recommendations

### **FR-3: Recommendation Engine**
- **FR-3.1**: Generate actionable recommendations based on comparison results
- **FR-3.2**: Identify winning configurations with statistical confidence
- **FR-3.3**: Suggest areas for further optimization
- **FR-3.4**: Provide cost-benefit analysis of different approaches
- **FR-3.5**: Support decision-making with risk assessment

---

## 🏗️ **Technical Architecture**

```typescript
// Domain Layer
export class BuildComparison {
    constructor(
        public readonly id: ComparisonId,
        public readonly buildA: BuildId,
        public readonly buildB: BuildId,
        private results: ComparisonResult[],
        private significance: StatisticalSignificance,
        private recommendations: Recommendation[],
        private readonly createdAt: Date = new Date()
    ) {}

    static create(buildA: BuildId, buildB: BuildId): BuildComparison {
        return new BuildComparison(
            ComparisonId.generate(),
            buildA,
            buildB,
            [],
            StatisticalSignificance.pending(),
            []
        );
    }

    addResult(result: ComparisonResult): void {
        this.results.push(result);
    }

    setSignificance(significance: StatisticalSignificance): void {
        this.significance = significance;
    }

    addRecommendation(recommendation: Recommendation): void {
        this.recommendations.push(recommendation);
    }

    getWinningBuild(): BuildId | null {
        if (!this.significance.isSignificant()) {
            return null;
        }

        const overallScore = this.calculateOverallScore();
        return overallScore.buildA > overallScore.buildB ? this.buildA : this.buildB;
    }

    private calculateOverallScore(): { buildA: number; buildB: number } {
        // Weighted composite score based on multiple metrics
        let scoreA = 0;
        let scoreB = 0;
        
        this.results.forEach(result => {
            const weight = result.metric.weight;
            scoreA += result.buildAValue * weight;
            scoreB += result.buildBValue * weight;
        });

        return { buildA: scoreA, buildB: scoreB };
    }
}

export class StatisticalSignificance {
    constructor(
        public readonly pValue: number,
        public readonly confidenceLevel: number,
        public readonly isSignificant: boolean,
        public readonly testType: StatisticalTest,
        public readonly effectSize: number
    ) {}

    static pending(): StatisticalSignificance {
        return new StatisticalSignificance(1.0, 0.95, false, StatisticalTest.NONE, 0);
    }

    getInterpretation(): StatisticalInterpretation {
        if (!this.isSignificant) {
            return StatisticalInterpretation.NOT_SIGNIFICANT;
        }

        if (this.effectSize < 0.2) {
            return StatisticalInterpretation.SMALL_EFFECT;
        } else if (this.effectSize < 0.5) {
            return StatisticalInterpretation.MEDIUM_EFFECT;
        } else {
            return StatisticalInterpretation.LARGE_EFFECT;
        }
    }
}

// Application Services
@Injectable()
export class BuildComparisonService {
    constructor(
        private readonly repository: IComparisonRepository,
        private readonly buildRepository: IBuildRepository,
        private readonly statisticalService: IStatisticalTestingService,
        private readonly recommendationEngine: IRecommendationEngine
    ) {}

    async compareBuilds(command: CompareBuildCommand): Promise<BuildComparison> {
        const [buildA, buildB] = await Promise.all([
            this.buildRepository.findById(command.buildAId),
            this.buildRepository.findById(command.buildBId)
        ]);

        if (!buildA || !buildB) {
            throw new BuildNotFoundError();
        }

        const comparison = BuildComparison.create(command.buildAId, command.buildBId);

        // Perform statistical comparisons for each metric
        for (const metric of command.metrics) {
            const result = await this.compareMetric(buildA, buildB, metric);
            comparison.addResult(result);
        }

        // Calculate overall statistical significance
        const significance = await this.statisticalService.calculateOverallSignificance(
            comparison.results
        );
        comparison.setSignificance(significance);

        // Generate recommendations
        const recommendations = await this.recommendationEngine.generateRecommendations(
            comparison
        );
        recommendations.forEach(rec => comparison.addRecommendation(rec));

        await this.repository.save(comparison);
        return comparison;
    }

    private async compareMetric(
        buildA: ContextBuild,
        buildB: ContextBuild,
        metric: ComparisonMetric
    ): Promise<ComparisonResult> {
        const [dataA, dataB] = await Promise.all([
            this.getMetricData(buildA, metric),
            this.getMetricData(buildB, metric)
        ]);

        const testResult = await this.statisticalService.performTest(
            dataA,
            dataB,
            metric.testType
        );

        return new ComparisonResult(
            metric,
            dataA.mean,
            dataB.mean,
            testResult.pValue,
            testResult.confidenceInterval,
            testResult.effectSize
        );
    }

    async getComparison(comparisonId: ComparisonId): Promise<BuildComparison | null> {
        return this.repository.findById(comparisonId);
    }

    async getComparisonHistory(buildId: BuildId): Promise<BuildComparison[]> {
        return this.repository.findByBuildId(buildId);
    }
}

@Injectable()
export class StatisticalTestingService {
    async performTTest(
        groupA: number[],
        groupB: number[]
    ): Promise<TTestResult> {
        const meanA = this.calculateMean(groupA);
        const meanB = this.calculateMean(groupB);
        const stdA = this.calculateStandardDeviation(groupA);
        const stdB = this.calculateStandardDeviation(groupB);
        
        const pooledStd = this.calculatePooledStandardDeviation(groupA, groupB);
        const tStatistic = (meanA - meanB) / (pooledStd * Math.sqrt(1/groupA.length + 1/groupB.length));
        
        const degreesOfFreedom = groupA.length + groupB.length - 2;
        const pValue = this.calculatePValue(tStatistic, degreesOfFreedom);
        
        const effectSize = Math.abs(meanA - meanB) / pooledStd; // Cohen's d
        
        return new TTestResult(
            tStatistic,
            pValue,
            degreesOfFreedom,
            effectSize,
            pValue < 0.05
        );
    }

    async performChiSquareTest(
        observedA: number[],
        observedB: number[]
    ): Promise<ChiSquareResult> {
        const total = observedA.reduce((sum, val, i) => sum + val + observedB[i], 0);
        const expected = observedA.map((val, i) => {
            const rowTotal = val + observedB[i];
            const colTotalA = observedA.reduce((sum, v) => sum + v, 0);
            return (rowTotal * colTotalA) / total;
        });

        const chiSquare = observedA.reduce((sum, val, i) => {
            return sum + Math.pow(val - expected[i], 2) / expected[i];
        }, 0);

        const degreesOfFreedom = observedA.length - 1;
        const pValue = this.calculateChiSquarePValue(chiSquare, degreesOfFreedom);

        return new ChiSquareResult(
            chiSquare,
            pValue,
            degreesOfFreedom,
            pValue < 0.05
        );
    }

    private calculateMean(values: number[]): number {
        return values.reduce((sum, val) => sum + val, 0) / values.length;
    }

    private calculateStandardDeviation(values: number[]): number {
        const mean = this.calculateMean(values);
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (values.length - 1);
        return Math.sqrt(variance);
    }

    private calculatePooledStandardDeviation(groupA: number[], groupB: number[]): number {
        const varA = Math.pow(this.calculateStandardDeviation(groupA), 2);
        const varB = Math.pow(this.calculateStandardDeviation(groupB), 2);
        
        return Math.sqrt(((groupA.length - 1) * varA + (groupB.length - 1) * varB) / 
                        (groupA.length + groupB.length - 2));
    }

    private calculatePValue(tStatistic: number, degreesOfFreedom: number): number {
        // Simplified p-value calculation - in practice, use a proper statistical library
        return 2 * (1 - this.studentTCDF(Math.abs(tStatistic), degreesOfFreedom));
    }

    private studentTCDF(t: number, df: number): number {
        // Approximation of Student's t cumulative distribution function
        // In production, use a proper statistical library like jStat
        return 0.5; // Placeholder
    }

    private calculateChiSquarePValue(chiSquare: number, degreesOfFreedom: number): number {
        // Simplified chi-square p-value calculation
        return Math.exp(-chiSquare / 2); // Placeholder approximation
    }
}

@Injectable()
export class RecommendationEngine {
    async generateRecommendations(comparison: BuildComparison): Promise<Recommendation[]> {
        const recommendations: Recommendation[] = [];
        
        const winningBuild = comparison.getWinningBuild();
        
        if (winningBuild) {
            recommendations.push(new Recommendation(
                RecommendationType.ADOPT_WINNER,
                `Adopt build ${winningBuild.value} as it shows statistically significant improvement`,
                RecommendationPriority.HIGH,
                comparison.significance.effectSize
            ));
        } else {
            recommendations.push(new Recommendation(
                RecommendationType.INSUFFICIENT_EVIDENCE,
                'No statistically significant difference found. Consider collecting more data or trying different approaches.',
                RecommendationPriority.MEDIUM,
                0
            ));
        }

        // Add metric-specific recommendations
        comparison.results.forEach(result => {
            if (result.isSignificant() && result.effectSize > 0.3) {
                recommendations.push(new Recommendation(
                    RecommendationType.METRIC_IMPROVEMENT,
                    `Focus on ${result.metric.name} optimization - significant improvement potential identified`,
                    RecommendationPriority.MEDIUM,
                    result.effectSize
                ));
            }
        });

        return recommendations;
    }
}
```

---

## 📊 **Database Schema**

```sql
-- Build Comparisons
CREATE TABLE build_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    build_a_id UUID NOT NULL,
    build_b_id UUID NOT NULL,
    overall_p_value DECIMAL(10,8),
    is_significant BOOLEAN DEFAULT false,
    effect_size DECIMAL(6,4),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Comparison Results
CREATE TABLE comparison_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comparison_id UUID REFERENCES build_comparisons(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    build_a_value DECIMAL(12,6) NOT NULL,
    build_b_value DECIMAL(12,6) NOT NULL,
    p_value DECIMAL(10,8) NOT NULL,
    confidence_interval JSONB NOT NULL,
    effect_size DECIMAL(6,4) NOT NULL,
    test_type statistical_test_type NOT NULL
);

CREATE TYPE statistical_test_type AS ENUM ('t_test', 'chi_square', 'mann_whitney', 'wilcoxon');

-- Recommendations
CREATE TABLE comparison_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comparison_id UUID REFERENCES build_comparisons(id) ON DELETE CASCADE,
    type recommendation_type NOT NULL,
    description TEXT NOT NULL,
    priority recommendation_priority NOT NULL,
    confidence DECIMAL(3,2) NOT NULL
);

CREATE TYPE recommendation_type AS ENUM ('adopt_winner', 'insufficient_evidence', 'metric_improvement', 'further_testing');
CREATE TYPE recommendation_priority AS ENUM ('low', 'medium', 'high', 'critical');
```

---

## 🔌 **API Specifications**

```yaml
paths:
  /comparisons:
    post:
      summary: Create build comparison
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                buildAId:
                  type: string
                  format: uuid
                buildBId:
                  type: string
                  format: uuid
                metrics:
                  type: array
                  items:
                    type: string
              required: [buildAId, buildBId, metrics]
      responses:
        201:
          description: Comparison created

  /comparisons/{id}:
    get:
      summary: Get comparison results
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Comparison results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BuildComparison'

  /comparisons/{id}/recommendations:
    get:
      summary: Get comparison recommendations
      responses:
        200:
          description: Recommendations
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Recommendation'

components:
  schemas:
    BuildComparison:
      type: object
      properties:
        id:
          type: string
          format: uuid
        buildAId:
          type: string
        buildBId:
          type: string
        isSignificant:
          type: boolean
        pValue:
          type: number
        effectSize:
          type: number
        
    Recommendation:
      type: object
      properties:
        type:
          type: string
        description:
          type: string
        priority:
          type: string
        confidence:
          type: number
```

---

## 🧪 **Testing Requirements**

```typescript
// TDD Cycle 15: Build Comparison
describe('BuildComparisonService', () => {
    describe('compareBuilds', () => {
        it('should detect significant difference between builds', async () => {
            // RED: Test fails initially
            const buildA = createMockBuild({ successRate: 0.75 });
            const buildB = createMockBuild({ successRate: 0.85 });
            
            mockBuildRepository.findById.mockImplementation((id) => {
                return id.equals(buildA.id) ? buildA : buildB;
            });

            const command = new CompareBuildCommand(
                buildA.id,
                buildB.id,
                [ComparisonMetric.SUCCESS_RATE]
            );

            const comparison = await service.compareBuilds(command);

            expect(comparison.significance.isSignificant).toBe(true);
            expect(comparison.getWinningBuild()).toBe(buildB.id);
        });

        it('should handle non-significant differences', async () => {
            // RED: Test fails initially
            const buildA = createMockBuild({ successRate: 0.80 });
            const buildB = createMockBuild({ successRate: 0.81 }); // Small difference
            
            const comparison = await service.compareBuilds(createCompareCommand(buildA.id, buildB.id));

            expect(comparison.significance.isSignificant).toBe(false);
            expect(comparison.getWinningBuild()).toBeNull();
        });
    });
});

describe('StatisticalTestingService', () => {
    describe('performTTest', () => {
        it('should calculate t-test correctly', async () => {
            // RED: Test fails initially
            const groupA = [0.7, 0.8, 0.75, 0.82, 0.78]; // Mean ~0.77
            const groupB = [0.85, 0.88, 0.83, 0.90, 0.87]; // Mean ~0.866
            
            const result = await service.performTTest(groupA, groupB);

            expect(result.pValue).toBeLessThan(0.05); // Significant difference
            expect(result.effectSize).toBeGreaterThan(0.5); // Large effect
        });
    });
});
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Compare context builds with statistical significance testing
- [ ] Calculate confidence intervals and effect sizes
- [ ] Generate actionable recommendations based on results
- [ ] Support multiple statistical test types (t-test, chi-square)
- [ ] Handle different sample sizes and power analysis
- [ ] Provide clear interpretation of statistical results

### **Performance Acceptance**
- [ ] Statistical calculations complete within 10 seconds
- [ ] Support comparison of builds with 10,000+ data points
- [ ] Handle concurrent comparisons efficiently
- [ ] Cache results for repeat comparisons

### **Accuracy Acceptance**
- [ ] Statistical calculations accurate to 6 decimal places
- [ ] Proper handling of multiple comparison corrections
- [ ] Correct interpretation of effect sizes and confidence intervals

This Comparison Module provides essential statistical analysis capabilities for objective performance evaluation and decision-making in the Self-Improving RAG Platform. 