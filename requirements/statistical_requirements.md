# Statistical Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: Statistical  
**Size Estimate**: ~25k tokens  
**Priority**: 3 (Advanced)  
**TDD Cycles**: 18, 19  
**Branch**: `module/statistical`  
**Cursor Window**: #10  
**Dependencies**: Orchestrator, Core RAG, Analytics, Comparison Modules  

### **Purpose**
Provides advanced statistical analysis capabilities including uncertainty quantification, Bayesian inference, causal analysis, and PAC-Bayesian bounds for rigorous performance evaluation and optimization guidance.

---

## 🎯 **Functional Requirements**

### **FR-1: Uncertainty Quantification** (TDD Cycle 18)
- **FR-1.1**: Calculate epistemic and aleatoric uncertainty for model predictions
- **FR-1.2**: Propagate uncertainty through optimization pipelines
- **FR-1.3**: Generate confidence intervals for performance metrics
- **FR-1.4**: Support Monte Carlo uncertainty estimation
- **FR-1.5**: Implement bootstrap sampling for uncertainty bounds
- **FR-1.6**: Provide uncertainty-aware decision making

### **FR-2: Causal Inference** (TDD Cycle 19)
- **FR-2.1**: Discover causal relationships in optimization data
- **FR-2.2**: Estimate intervention effects on performance
- **FR-2.3**: Handle confounding variables and selection bias
- **FR-2.4**: Support instrumental variable estimation
- **FR-2.5**: Implement directed acyclic graph (DAG) construction
- **FR-2.6**: Provide causal effect attribution for improvements

### **FR-3: Bayesian Analysis**
- **FR-3.1**: Implement Bayesian optimization for hyperparameter tuning
- **FR-3.2**: Calculate posterior distributions for model parameters
- **FR-3.3**: Support Bayesian A/B testing with early stopping
- **FR-3.4**: Implement hierarchical Bayesian models
- **FR-3.5**: Provide credible intervals and Bayes factors
- **FR-3.6**: Support prior specification and sensitivity analysis

### **FR-4: PAC-Bayesian Framework**
- **FR-4.1**: Calculate PAC-Bayesian bounds for optimization performance
- **FR-4.2**: Support generalization bound estimation
- **FR-4.3**: Implement theoretical guarantees for improvement claims
- **FR-4.4**: Provide risk assessment with formal bounds
- **FR-4.5**: Support learning theory validation

---

## 🏗️ **Technical Architecture**

```typescript
// Domain Layer
export class UncertaintyEstimate {
    constructor(
        public readonly mean: number,
        public readonly variance: number,
        public readonly epistemicUncertainty: number,
        public readonly aleatoricUncertainty: number,
        public readonly confidenceInterval: ConfidenceInterval,
        public readonly method: UncertaintyMethod
    ) {}

    getTotalUncertainty(): number {
        return Math.sqrt(this.epistemicUncertainty ** 2 + this.aleatoricUncertainty ** 2);
    }

    isHighlyUncertain(threshold: number = 0.1): boolean {
        return this.getTotalUncertainty() > threshold;
    }

    getCredibleInterval(level: number = 0.95): CredibleInterval {
        const multiplier = this.getNormalQuantile((1 + level) / 2);
        const margin = multiplier * Math.sqrt(this.variance);
        
        return new CredibleInterval(
            this.mean - margin,
            this.mean + margin,
            level
        );
    }

    private getNormalQuantile(p: number): number {
        // Approximation of normal quantile function
        return Math.sqrt(2) * this.inverseErrorFunction(2 * p - 1);
    }

    private inverseErrorFunction(x: number): number {
        // Approximation - in production use proper statistical library
        const a = 0.147;
        const firstPart = Math.sqrt((2 / (Math.PI * a)) + (Math.log(1 - x ** 2) / 2));
        const secondPart = Math.log(1 - x ** 2) / a;
        return Math.sign(x) * Math.sqrt(firstPart - secondPart);
    }
}

export class CausalEffect {
    constructor(
        public readonly treatment: TreatmentVariable,
        public readonly outcome: OutcomeVariable,
        public readonly estimatedEffect: number,
        public readonly standardError: number,
        public readonly pValue: number,
        public readonly confounders: ConfoundingVariable[],
        public readonly method: CausalMethod
    ) {}

    isSignificant(alpha: number = 0.05): boolean {
        return this.pValue < alpha;
    }

    getConfidenceInterval(level: number = 0.95): ConfidenceInterval {
        const tValue = this.getTValue(level);
        const margin = tValue * this.standardError;
        
        return new ConfidenceInterval(
            this.estimatedEffect - margin,
            this.estimatedEffect + margin,
            level
        );
    }

    calculateCohenD(): number {
        // Effect size calculation
        return Math.abs(this.estimatedEffect) / this.standardError;
    }

    private getTValue(level: number): number {
        // Simplified t-value calculation
        return 1.96; // Approximation for large samples
    }
}

export class BayesianOptimization {
    constructor(
        private acquisitionFunction: AcquisitionFunction,
        private gaussianProcess: GaussianProcess,
        private priorBelief: PriorDistribution,
        private observations: OptimizationObservation[]
    ) {}

    async suggestNext(): Promise<OptimizationSuggestion> {
        // Update GP with latest observations
        await this.gaussianProcess.update(this.observations);
        
        // Find next best point to evaluate
        const candidate = await this.acquisitionFunction.optimize(this.gaussianProcess);
        
        return new OptimizationSuggestion(
            candidate.parameters,
            candidate.expectedImprovement,
            candidate.uncertainty
        );
    }

    updatePosterior(observation: OptimizationObservation): void {
        this.observations.push(observation);
        this.gaussianProcess.addObservation(observation);
    }

    getPosteriorMean(parameters: OptimizationParameters): number {
        return this.gaussianProcess.predict(parameters).mean;
    }

    getPosteriorVariance(parameters: OptimizationParameters): number {
        return this.gaussianProcess.predict(parameters).variance;
    }
}

export class PACBayesianBound {
    constructor(
        public readonly empiricalRisk: number,
        public readonly complexity: number,
        public readonly confidence: number,
        public readonly sampleSize: number,
        public readonly priorWeight: number
    ) {}

    calculateGeneralizationBound(): number {
        const klDivergence = this.calculateKLDivergence();
        const term1 = klDivergence + Math.log(2 * Math.sqrt(this.sampleSize) / this.confidence);
        const term2 = this.sampleSize;
        
        return this.empiricalRisk + Math.sqrt(term1 / (2 * term2));
    }

    isGeneralizationGuaranteed(threshold: number): boolean {
        return this.calculateGeneralizationBound() <= threshold;
    }

    private calculateKLDivergence(): number {
        // Simplified KL divergence calculation
        // In practice, this would be computed based on the specific prior and posterior
        return this.complexity * Math.log(this.sampleSize);
    }
}

// Application Services
@Injectable()
export class UncertaintyQuantificationService {
    constructor(
        private readonly modelEvaluator: IModelEvaluator,
        private readonly bootstrapSampler: IBootstrapSampler,
        private readonly mcmcSampler: IMCMCSampler
    ) {}

    async quantifyModelUncertainty(
        model: OptimizationModel,
        data: ModelData
    ): Promise<UncertaintyEstimate> {
        // Monte Carlo dropout for epistemic uncertainty
        const epistemicUncertainty = await this.estimateEpistemicUncertainty(model, data);
        
        // Bootstrap sampling for aleatoric uncertainty
        const aleatoricUncertainty = await this.estimateAleatoricUncertainty(model, data);
        
        // Model predictions
        const predictions = await this.modelEvaluator.evaluate(model, data);
        const mean = this.calculateMean(predictions);
        const variance = this.calculateVariance(predictions);
        
        const confidenceInterval = this.calculateConfidenceInterval(predictions, 0.95);
        
        return new UncertaintyEstimate(
            mean,
            variance,
            epistemicUncertainty,
            aleatoricUncertainty,
            confidenceInterval,
            UncertaintyMethod.MONTE_CARLO_BOOTSTRAP
        );
    }

    private async estimateEpistemicUncertainty(
        model: OptimizationModel,
        data: ModelData
    ): Promise<number> {
        const samples = [];
        for (let i = 0; i < 100; i++) {
            const prediction = await this.modelEvaluator.evaluateWithDropout(model, data);
            samples.push(prediction);
        }
        return this.calculateVariance(samples);
    }

    private async estimateAleatoricUncertainty(
        model: OptimizationModel,
        data: ModelData
    ): Promise<number> {
        const bootstrapSamples = await this.bootstrapSampler.sample(data, 1000);
        const predictions = await Promise.all(
            bootstrapSamples.map(sample => this.modelEvaluator.evaluate(model, sample))
        );
        return this.calculateVariance(predictions);
    }

    private calculateMean(values: number[]): number {
        return values.reduce((sum, val) => sum + val, 0) / values.length;
    }

    private calculateVariance(values: number[]): number {
        const mean = this.calculateMean(values);
        return values.reduce((sum, val) => sum + (val - mean) ** 2, 0) / (values.length - 1);
    }

    private calculateConfidenceInterval(values: number[], level: number): ConfidenceInterval {
        const sorted = values.sort((a, b) => a - b);
        const alpha = 1 - level;
        const lowerIndex = Math.floor(alpha * sorted.length / 2);
        const upperIndex = Math.ceil((1 - alpha / 2) * sorted.length) - 1;
        
        return new ConfidenceInterval(
            sorted[lowerIndex],
            sorted[upperIndex],
            level
        );
    }
}

@Injectable()
export class CausalInferenceService {
    constructor(
        private readonly causalDiscovery: ICausalDiscoveryAlgorithm,
        private readonly ivEstimator: IInstrumentalVariableEstimator,
        private readonly propensityScorer: IPropensityScoreCalculator
    ) {}

    async estimateInterventionEffect(
        data: CausalDataset,
        treatment: TreatmentVariable,
        outcome: OutcomeVariable,
        confounders: ConfoundingVariable[]
    ): Promise<CausalEffect> {
        // Discover causal structure
        const causalGraph = await this.causalDiscovery.discover(data);
        
        // Validate identification
        if (!this.isIdentifiable(causalGraph, treatment, outcome, confounders)) {
            throw new CausalIdentificationError('Effect is not identifiable given the causal structure');
        }

        // Choose estimation method
        const method = this.selectEstimationMethod(causalGraph, treatment, confounders);
        let effectEstimate: EffectEstimate;

        switch (method) {
            case CausalMethod.PROPENSITY_SCORE_MATCHING:
                effectEstimate = await this.estimateWithPropensityScore(
                    data, treatment, outcome, confounders
                );
                break;
            
            case CausalMethod.INSTRUMENTAL_VARIABLES:
                effectEstimate = await this.estimateWithIV(data, treatment, outcome);
                break;
            
            case CausalMethod.REGRESSION_ADJUSTMENT:
                effectEstimate = await this.estimateWithRegression(
                    data, treatment, outcome, confounders
                );
                break;
            
            default:
                throw new UnsupportedCausalMethodError(method);
        }

        return new CausalEffect(
            treatment,
            outcome,
            effectEstimate.effect,
            effectEstimate.standardError,
            effectEstimate.pValue,
            confounders,
            method
        );
    }

    private async estimateWithPropensityScore(
        data: CausalDataset,
        treatment: TreatmentVariable,
        outcome: OutcomeVariable,
        confounders: ConfoundingVariable[]
    ): Promise<EffectEstimate> {
        // Calculate propensity scores
        const propensityScores = await this.propensityScorer.calculate(data, treatment, confounders);
        
        // Match treated and control units
        const matches = this.findMatches(data, propensityScores);
        
        // Estimate average treatment effect
        const ate = this.calculateATE(matches, outcome);
        const standardError = this.calculateATEStandardError(matches, outcome);
        const pValue = this.calculatePValue(ate, standardError);
        
        return new EffectEstimate(ate, standardError, pValue);
    }

    private isIdentifiable(
        graph: CausalGraph,
        treatment: TreatmentVariable,
        outcome: OutcomeVariable,
        confounders: ConfoundingVariable[]
    ): boolean {
        // Check backdoor criterion
        return graph.satisfiesBackdoorCriterion(treatment, outcome, confounders);
    }

    private selectEstimationMethod(
        graph: CausalGraph,
        treatment: TreatmentVariable,
        confounders: ConfoundingVariable[]
    ): CausalMethod {
        if (graph.hasValidInstrument(treatment)) {
            return CausalMethod.INSTRUMENTAL_VARIABLES;
        } else if (confounders.length > 0) {
            return CausalMethod.PROPENSITY_SCORE_MATCHING;
        } else {
            return CausalMethod.REGRESSION_ADJUSTMENT;
        }
    }
}

@Injectable()
export class BayesianAnalysisService {
    constructor(
        private readonly optimizer: IBayesianOptimizer,
        private readonly sampler: IGibbsSampler,
        private readonly modelSelector: IBayesianModelSelector
    ) {}

    async optimizeHyperparameters(
        objectiveFunction: ObjectiveFunction,
        parameterSpace: ParameterSpace,
        budget: number
    ): Promise<BayesianOptimizationResult> {
        const optimization = new BayesianOptimization(
            new ExpectedImprovementAcquisition(),
            new GaussianProcessRegressor(),
            new UniformPrior(parameterSpace),
            []
        );

        const results = [];
        
        for (let iteration = 0; iteration < budget; iteration++) {
            // Get next suggestion
            const suggestion = await optimization.suggestNext();
            
            // Evaluate objective function
            const performance = await objectiveFunction.evaluate(suggestion.parameters);
            
            // Update optimization state
            const observation = new OptimizationObservation(
                suggestion.parameters,
                performance,
                new Date()
            );
            optimization.updatePosterior(observation);
            
            results.push({
                iteration,
                parameters: suggestion.parameters,
                performance,
                uncertainty: suggestion.uncertainty
            });
        }

        return new BayesianOptimizationResult(
            results,
            this.findBestResult(results),
            optimization.getPosteriorMean.bind(optimization)
        );
    }

    async performBayesianABTest(
        controlData: number[],
        treatmentData: number[],
        priors: BayesianPriors
    ): Promise<BayesianABTestResult> {
        // Sample from posterior distributions
        const controlPosterior = await this.sampler.samplePosterior(
            controlData,
            priors.controlPrior,
            10000
        );
        
        const treatmentPosterior = await this.sampler.samplePosterior(
            treatmentData,
            priors.treatmentPrior,
            10000
        );

        // Calculate probability of superiority
        const probabilityTreatmentBetter = this.calculateSuperiority(
            treatmentPosterior,
            controlPosterior
        );

        // Calculate credible intervals
        const controlCI = this.calculateCredibleInterval(controlPosterior, 0.95);
        const treatmentCI = this.calculateCredibleInterval(treatmentPosterior, 0.95);

        // Calculate Bayes factor
        const bayesFactor = this.calculateBayesFactor(
            controlData,
            treatmentData,
            priors
        );

        return new BayesianABTestResult(
            probabilityTreatmentBetter,
            controlCI,
            treatmentCI,
            bayesFactor,
            probabilityTreatmentBetter > 0.95 // Decision threshold
        );
    }

    private findBestResult(results: OptimizationIteration[]): OptimizationIteration {
        return results.reduce((best, current) => 
            current.performance > best.performance ? current : best
        );
    }

    private calculateSuperiority(
        treatmentSamples: number[],
        controlSamples: number[]
    ): number {
        let count = 0;
        for (let i = 0; i < treatmentSamples.length; i++) {
            if (treatmentSamples[i] > controlSamples[i]) {
                count++;
            }
        }
        return count / treatmentSamples.length;
    }
}
```

---

## 📊 **Database Schema**

```sql
-- Uncertainty Estimates
CREATE TABLE uncertainty_estimates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id VARCHAR(255) NOT NULL,
    mean_value DECIMAL(12,6) NOT NULL,
    variance DECIMAL(12,6) NOT NULL,
    epistemic_uncertainty DECIMAL(12,6) NOT NULL,
    aleatoric_uncertainty DECIMAL(12,6) NOT NULL,
    confidence_lower DECIMAL(12,6) NOT NULL,
    confidence_upper DECIMAL(12,6) NOT NULL,
    confidence_level DECIMAL(3,2) NOT NULL,
    method uncertainty_method NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE uncertainty_method AS ENUM ('monte_carlo', 'bootstrap', 'bayesian', 'ensemble');

-- Causal Effects
CREATE TABLE causal_effects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    treatment_variable VARCHAR(255) NOT NULL,
    outcome_variable VARCHAR(255) NOT NULL,
    estimated_effect DECIMAL(12,6) NOT NULL,
    standard_error DECIMAL(12,6) NOT NULL,
    p_value DECIMAL(10,8) NOT NULL,
    confidence_lower DECIMAL(12,6) NOT NULL,
    confidence_upper DECIMAL(12,6) NOT NULL,
    confounders JSONB DEFAULT '[]',
    method causal_method NOT NULL,
    is_significant BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE causal_method AS ENUM ('propensity_score', 'instrumental_variables', 'regression_adjustment', 'matching');

-- Bayesian Optimization Results
CREATE TABLE bayesian_optimization_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objective_function VARCHAR(255) NOT NULL,
    iteration INTEGER NOT NULL,
    parameters JSONB NOT NULL,
    performance DECIMAL(12,6) NOT NULL,
    uncertainty DECIMAL(12,6) NOT NULL,
    acquisition_value DECIMAL(12,6),
    is_best BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- PAC-Bayesian Bounds
CREATE TABLE pac_bayesian_bounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id VARCHAR(255) NOT NULL,
    empirical_risk DECIMAL(12,6) NOT NULL,
    complexity DECIMAL(12,6) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    sample_size INTEGER NOT NULL,
    generalization_bound DECIMAL(12,6) NOT NULL,
    is_guaranteed BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🧪 **Testing Requirements**

```typescript
// TDD Cycle 18: Uncertainty Quantification
describe('UncertaintyQuantificationService', () => {
    describe('quantifyModelUncertainty', () => {
        it('should calculate epistemic and aleatoric uncertainty', async () => {
            // RED: Test fails initially
            const model = createMockOptimizationModel();
            const data = createMockModelData();
            
            mockModelEvaluator.evaluate.mockResolvedValue([0.85, 0.82, 0.88, 0.79, 0.86]);
            mockModelEvaluator.evaluateWithDropout.mockResolvedValue(0.83);
            mockBootstrapSampler.sample.mockResolvedValue([
                createMockSample(),
                createMockSample()
            ]);

            const uncertainty = await service.quantifyModelUncertainty(model, data);

            expect(uncertainty.epistemicUncertainty).toBeGreaterThan(0);
            expect(uncertainty.aleatoricUncertainty).toBeGreaterThan(0);
            expect(uncertainty.getTotalUncertainty()).toBeGreaterThan(0);
            expect(uncertainty.confidenceInterval.lower).toBeLessThan(uncertainty.mean);
            expect(uncertainty.confidenceInterval.upper).toBeGreaterThan(uncertainty.mean);
        });

        it('should identify high uncertainty scenarios', async () => {
            // RED: Test fails initially
            const uncertainty = createMockUncertaintyEstimate({
                epistemicUncertainty: 0.15,
                aleatoricUncertainty: 0.08
            });

            const isHighlyUncertain = uncertainty.isHighlyUncertain(0.1);

            expect(isHighlyUncertain).toBe(true);
        });
    });
});

// TDD Cycle 19: Causal Inference
describe('CausalInferenceService', () => {
    describe('estimateInterventionEffect', () => {
        it('should estimate causal effect with confounders', async () => {
            // RED: Test fails initially
            const data = createMockCausalDataset();
            const treatment = new TreatmentVariable('optimization_type');
            const outcome = new OutcomeVariable('success_rate');
            const confounders = [new ConfoundingVariable('user_experience')];

            const causalGraph = createMockCausalGraph();
            mockCausalDiscovery.discover.mockResolvedValue(causalGraph);
            mockPropensityScorer.calculate.mockResolvedValue([0.3, 0.7, 0.5, 0.8]);

            const effect = await service.estimateInterventionEffect(
                data,
                treatment,
                outcome,
                confounders
            );

            expect(effect.estimatedEffect).toBeDefined();
            expect(effect.standardError).toBeGreaterThan(0);
            expect(effect.pValue).toBeLessThanOrEqual(1);
            expect(effect.confounders).toEqual(confounders);
        });

        it('should throw error when effect is not identifiable', async () => {
            // RED: Test fails initially
            const data = createMockCausalDataset();
            const treatment = new TreatmentVariable('optimization_type');
            const outcome = new OutcomeVariable('success_rate');
            const confounders = [];

            const nonIdentifiableGraph = createMockNonIdentifiableCausalGraph();
            mockCausalDiscovery.discover.mockResolvedValue(nonIdentifiableGraph);

            await expect(service.estimateInterventionEffect(
                data,
                treatment,
                outcome,
                confounders
            )).rejects.toThrow(CausalIdentificationError);
        });
    });
});

describe('BayesianAnalysisService', () => {
    describe('optimizeHyperparameters', () => {
        it('should find optimal hyperparameters with uncertainty', async () => {
            // RED: Test fails initially
            const objectiveFunction = createMockObjectiveFunction();
            const parameterSpace = createMockParameterSpace();
            const budget = 20;

            const result = await service.optimizeHyperparameters(
                objectiveFunction,
                parameterSpace,
                budget
            );

            expect(result.iterations).toHaveLength(budget);
            expect(result.bestResult.performance).toBeGreaterThan(0);
            expect(result.posteriorMean).toBeDefined();
        });
    });

    describe('performBayesianABTest', () => {
        it('should calculate probability of superiority', async () => {
            // RED: Test fails initially
            const controlData = [0.75, 0.78, 0.72, 0.80, 0.76];
            const treatmentData = [0.82, 0.85, 0.79, 0.88, 0.84];
            const priors = createMockBayesianPriors();

            mockSampler.samplePosterior.mockImplementation((data) => {
                return data.map(d => d + Math.random() * 0.02 - 0.01); // Mock sampling
            });

            const result = await service.performBayesianABTest(
                controlData,
                treatmentData,
                priors
            );

            expect(result.probabilityTreatmentBetter).toBeGreaterThan(0.5);
            expect(result.treatmentCredibleInterval.upper).toBeGreaterThan(
                result.treatmentCredibleInterval.lower
            );
            expect(result.bayesFactor).toBeGreaterThan(0);
        });
    });
});
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Quantify epistemic and aleatoric uncertainty for model predictions
- [ ] Estimate causal effects with proper confounder adjustment
- [ ] Perform Bayesian optimization with uncertainty-aware acquisition
- [ ] Calculate PAC-Bayesian bounds for generalization guarantees
- [ ] Support Bayesian A/B testing with credible intervals
- [ ] Provide theoretical guarantees for optimization claims

### **Performance Acceptance**
- [ ] Uncertainty quantification completes within 30 seconds
- [ ] Causal inference handles datasets with 100,000+ observations
- [ ] Bayesian optimization converges within 50 iterations
- [ ] Statistical calculations maintain numerical stability

### **Accuracy Acceptance**
- [ ] Uncertainty estimates accurate to within 5% of true values
- [ ] Causal effect estimates unbiased under correct model specification
- [ ] PAC-Bayesian bounds hold with specified confidence levels
- [ ] Bayesian posteriors converge to true distributions

This Statistical Module provides the advanced theoretical foundation for rigorous uncertainty quantification, causal analysis, and optimization guidance essential for scientifically sound performance evaluation in the Self-Improving RAG Platform. 