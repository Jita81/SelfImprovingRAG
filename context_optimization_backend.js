// server.js - Context Engineering Optimization Platform Backend
const express = require('express');
const cors = require('cors');
const { BlobServiceClient } = require('@azure/storage-blob');
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
const { DefaultAzureCredential } = require('@azure/identity');
const OpenAI = require('openai');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static('public'));

// Azure services initialization
const credential = new DefaultAzureCredential();
const blobServiceClient = new BlobServiceClient(
  `https://${process.env.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net`,
  credential
);

const searchClient = new SearchClient(
  `https://${process.env.AZURE_SEARCH_SERVICE}.search.windows.net`,
  'context-index',
  new AzureKeyCredential(process.env.AZURE_SEARCH_KEY)
);

// OpenAI for testing AI performance
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Context Engineering Classes
class ContextBuild {
  constructor(name, version, elements, tokenBudget) {
    this.id = `${name.toLowerCase().replace(/\s+/g, '-')}-${version}`;
    this.name = name;
    this.version = version;
    this.elements = elements;
    this.tokenBudget = tokenBudget;
    this.tokensUsed = 0;
    this.successRate = 0;
    this.tokenEfficiency = 0;
    this.timeToGreen = 0;
    this.specializations = [];
    this.weaknesses = [];
    this.performanceHistory = [];
  }

  calculateTokenUsage() {
    this.tokensUsed = this.elements.reduce((total, element) => {
      return total + (element.tokenCount || 0);
    }, 0);
    return this.tokensUsed;
  }

  calculateEfficiency() {
    if (this.tokensUsed === 0) return 0;
    this.tokenEfficiency = (this.successRate / (this.tokensUsed / 1000));
    return this.tokenEfficiency;
  }
}

class ContextOptimizer {
  constructor() {
    this.builds = new Map();
    this.testResults = [];
    this.optimizationHistory = [];
  }

  async testContextBuild(build, requirements) {
    const results = {
      buildId: build.id,
      timestamp: new Date(),
      results: []
    };

    for (const requirement of requirements) {
      const testResult = await this.runSingleTest(build, requirement);
      results.results.push(testResult);
    }

    // Calculate aggregate metrics
    const successCount = results.results.filter(r => r.success).length;
    build.successRate = (successCount / results.results.length) * 100;
    
    const avgTime = results.results.reduce((sum, r) => sum + r.timeToComplete, 0) / results.results.length;
    build.timeToGreen = avgTime / 1000; // Convert to seconds

    build.calculateTokenUsage();
    build.calculateEfficiency();

    this.testResults.push(results);
    return results;
  }

  async runSingleTest(build, requirement) {
    const startTime = Date.now();
    
    try {
      // Construct context from build elements
      const context = this.constructContext(build);
      
      // Create prompt with context and requirement
      const prompt = this.createPrompt(context, requirement);
      
      // Test with AI
      const response = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: context },
          { role: "user", content: requirement.description }
        ],
        max_tokens: 2000,
        temperature: 0.1
      });

      const endTime = Date.now();
      const generatedCode = response.choices[0].message.content;

      // Evaluate the response
      const evaluation = await this.evaluateResponse(generatedCode, requirement);

      return {
        requirement: requirement.id,
        success: evaluation.success,
        timeToComplete: endTime - startTime,
        evaluation: evaluation,
        generatedCode: generatedCode
      };

    } catch (error) {
      const endTime = Date.now();
      return {
        requirement: requirement.id,
        success: false,
        timeToComplete: endTime - startTime,
        error: error.message
      };
    }
  }

  constructContext(build) {
    return build.elements.map(element => element.content).join('\n\n');
  }

  createPrompt(context, requirement) {
    return `${context}\n\nRequirement: ${requirement.description}\n\nImplement this requirement following the patterns and examples provided in the context.`;
  }

  async evaluateResponse(generatedCode, requirement) {
    // Simple evaluation - in production, this would be more sophisticated
    const hasRequiredElements = requirement.mustInclude?.every(element => 
      generatedCode.toLowerCase().includes(element.toLowerCase())
    ) ?? true;

    const hasAvoidedElements = !requirement.mustAvoid?.some(element =>
      generatedCode.toLowerCase().includes(element.toLowerCase())
    ) ?? true;

    const codeLength = generatedCode.length;
    const hasReasonableLength = codeLength > 100 && codeLength < 5000;

    return {
      success: hasRequiredElements && hasAvoidedElements && hasReasonableLength,
      hasRequiredElements,
      hasAvoidedElements,
      hasReasonableLength,
      codeLength,
      score: (hasRequiredElements ? 0.4 : 0) + 
             (hasAvoidedElements ? 0.3 : 0) + 
             (hasReasonableLength ? 0.3 : 0)
    };
  }

  async optimizeBuild(buildId) {
    const build = this.builds.get(buildId);
    if (!build) throw new Error('Build not found');

    const optimizationRun = {
      buildId,
      timestamp: new Date(),
      originalPerformance: { ...build },
      optimizations: []
    };

    // Ablation testing - remove elements to find minimum viable build
    const ablationResults = await this.ablationTest(build);
    optimizationRun.optimizations.push({
      type: 'ablation',
      results: ablationResults
    });

    // Context element A/B testing
    const elementTests = await this.testElementCombinations(build);
    optimizationRun.optimizations.push({
      type: 'element_combinations',
      results: elementTests
    });

    // Find optimal token allocation
    const tokenOptimization = await this.optimizeTokenAllocation(build);
    optimizationRun.optimizations.push({
      type: 'token_optimization',
      results: tokenOptimization
    });

    this.optimizationHistory.push(optimizationRun);
    return optimizationRun;
  }

  async ablationTest(build) {
    const baselinePerformance = build.successRate;
    const ablationResults = [];

    for (let i = 0; i < build.elements.length; i++) {
      // Create build without element i
      const reducedElements = build.elements.filter((_, index) => index !== i);
      const testBuild = new ContextBuild(
        `${build.name}-ablation-${i}`,
        'test',
        reducedElements,
        build.tokenBudget
      );

      // Test reduced build
      const testRequirements = await this.getTestRequirements();
      const results = await this.testContextBuild(testBuild, testRequirements);

      ablationResults.push({
        removedElement: build.elements[i].name,
        performanceImpact: baselinePerformance - testBuild.successRate,
        tokenSavings: build.elements[i].tokenCount,
        roi: (baselinePerformance - testBuild.successRate) / build.elements[i].tokenCount
      });
    }

    return ablationResults.sort((a, b) => a.performanceImpact - b.performanceImpact);
  }

  async testElementCombinations(build) {
    // Test synergies between different context elements
    const combinations = this.generateElementCombinations(build.elements);
    const results = [];

    for (const combination of combinations) {
      const testBuild = new ContextBuild(
        `${build.name}-combo-test`,
        'test',
        combination,
        build.tokenBudget
      );

      const testRequirements = await this.getTestRequirements();
      await this.testContextBuild(testBuild, testRequirements);

      results.push({
        elements: combination.map(e => e.name),
        successRate: testBuild.successRate,
        tokenEfficiency: testBuild.tokenEfficiency,
        synegyScore: this.calculateSynergyScore(testBuild, build)
      });
    }

    return results.sort((a, b) => b.synegyScore - a.synegyScore);
  }

  generateElementCombinations(elements) {
    // Generate meaningful combinations of context elements
    const combinations = [];
    
    // All pairs
    for (let i = 0; i < elements.length; i++) {
      for (let j = i + 1; j < elements.length; j++) {
        combinations.push([elements[i], elements[j]]);
      }
    }

    // All triplets
    for (let i = 0; i < elements.length; i++) {
      for (let j = i + 1; j < elements.length; j++) {
        for (let k = j + 1; k < elements.length; k++) {
          combinations.push([elements[i], elements[j], elements[k]]);
        }
      }
    }

    return combinations;
  }

  calculateSynergyScore(testBuild, originalBuild) {
    const expectedPerformance = testBuild.elements.reduce((sum, element) => {
      return sum + (element.individualPerformance || 0);
    }, 0) / testBuild.elements.length;

    return testBuild.successRate - expectedPerformance;
  }

  async optimizeTokenAllocation(build) {
    // Use gradient descent-like approach to optimize token allocation
    const optimizationResults = [];
    let currentBuild = { ...build };

    for (let iteration = 0; iteration < 10; iteration++) {
      const gradients = await this.calculatePerformanceGradients(currentBuild);
      const adjustedBuild = this.adjustTokenAllocation(currentBuild, gradients);
      
      const testRequirements = await this.getTestRequirements();
      await this.testContextBuild(adjustedBuild, testRequirements);

      optimizationResults.push({
        iteration,
        successRate: adjustedBuild.successRate,
        tokenEfficiency: adjustedBuild.tokenEfficiency,
        allocation: adjustedBuild.elements.map(e => ({
          name: e.name,
          tokens: e.tokenCount
        }))
      });

      if (adjustedBuild.successRate <= currentBuild.successRate) {
        break; // No improvement, stop optimizing
      }

      currentBuild = adjustedBuild;
    }

    return optimizationResults;
  }

  async calculatePerformanceGradients(build) {
    // Calculate how much performance changes per token for each element
    const gradients = [];

    for (let i = 0; i < build.elements.length; i++) {
      const element = build.elements[i];
      const increasedTokens = { ...element, tokenCount: element.tokenCount + 100 };
      const decreasedTokens = { ...element, tokenCount: Math.max(0, element.tokenCount - 100) };

      // Test with more tokens
      const increasedBuild = new ContextBuild(
        `${build.name}-gradient-test`,
        'test',
        build.elements.map((e, index) => index === i ? increasedTokens : e),
        build.tokenBudget + 100
      );

      const testRequirements = await this.getTestRequirements();
      await this.testContextBuild(increasedBuild, testRequirements);

      gradients.push({
        elementIndex: i,
        gradient: (increasedBuild.successRate - build.successRate) / 100,
        currentTokens: element.tokenCount
      });
    }

    return gradients;
  }

  adjustTokenAllocation(build, gradients) {
    const learningRate = 0.1;
    const adjustedElements = build.elements.map((element, index) => {
      const gradient = gradients[index];
      const tokenAdjustment = gradient.gradient * learningRate * 100;
      
      return {
        ...element,
        tokenCount: Math.max(50, Math.min(2000, element.tokenCount + tokenAdjustment))
      };
    });

    return new ContextBuild(
      `${build.name}-optimized`,
      build.version,
      adjustedElements,
      build.tokenBudget
    );
  }

  async getTestRequirements() {
    // Load test requirements from Azure Storage
    try {
      const containerClient = blobServiceClient.getContainerClient('company-data');
      const blobClient = containerClient.getBlobClient('test-requirements.json');
      const downloadResponse = await blobClient.download();
      const content = await this.streamToString(downloadResponse.readableStreamBody);
      return JSON.parse(content);
    } catch (error) {
      // Fallback to default requirements
      return [
        {
          id: 'auth-oauth',
          description: 'Implement OAuth 2.0 authentication with Google',
          mustInclude: ['oauth', 'google', 'redirect'],
          mustAvoid: ['plaintext', 'insecure']
        },
        {
          id: 'crud-api',
          description: 'Create a REST API for managing user accounts',
          mustInclude: ['get', 'post', 'put', 'delete'],
          mustAvoid: ['sql injection', 'unsafe']
        },
        {
          id: 'data-validation',
          description: 'Implement input validation for user registration',
          mustInclude: ['validation', 'sanitize', 'check'],
          mustAvoid: ['eval', 'dangerous']
        }
      ];
    }
  }

  async streamToString(readableStream) {
    return new Promise((resolve, reject) => {
      const chunks = [];
      readableStream.on('data', (data) => {
        chunks.push(data.toString());
      });
      readableStream.on('end', () => {
        resolve(chunks.join(''));
      });
      readableStream.on('error', reject);
    });
  }
}

// Initialize context optimizer
const contextOptimizer = new ContextOptimizer();

// API Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Get all context builds
app.get('/api/builds', (req, res) => {
  const builds = Array.from(contextOptimizer.builds.values()).map(build => ({
    id: build.id,
    name: build.name,
    version: build.version,
    successRate: build.successRate,
    tokenEfficiency: build.tokenEfficiency,
    timeToGreen: build.timeToGreen,
    tokensUsed: build.tokensUsed,
    tokenBudget: build.tokenBudget,
    specializations: build.specializations,
    weaknesses: build.weaknesses,
    lastOptimized: build.lastOptimized
  }));
  
  res.json(builds);
});

// Get specific build details
app.get('/api/builds/:id', (req, res) => {
  const build = contextOptimizer.builds.get(req.params.id);
  if (!build) {
    return res.status(404).json({ error: 'Build not found' });
  }
  res.json(build);
});

// Create new context build
app.post('/api/builds', async (req, res) => {
  try {
    const { name, version, elements, tokenBudget } = req.body;
    
    const build = new ContextBuild(name, version, elements, tokenBudget);
    contextOptimizer.builds.set(build.id, build);
    
    // Run initial performance test
    const testRequirements = await contextOptimizer.getTestRequirements();
    await contextOptimizer.testContextBuild(build, testRequirements);
    
    res.json(build);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start optimization for a build
app.post('/api/builds/:id/optimize', async (req, res) => {
  try {
    const optimizationResults = await contextOptimizer.optimizeBuild(req.params.id);
    res.json(optimizationResults);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// A/B test two builds
app.post('/api/builds/compare', async (req, res) => {
  try {
    const { buildA, buildB } = req.body;
    
    const testRequirements = await contextOptimizer.getTestRequirements();
    
    const resultsA = await contextOptimizer.testContextBuild(
      contextOptimizer.builds.get(buildA), 
      testRequirements
    );
    const resultsB = await contextOptimizer.testContextBuild(
      contextOptimizer.builds.get(buildB), 
      testRequirements
    );
    
    const comparison = {
      buildA: { id: buildA, results: resultsA },
      buildB: { id: buildB, results: resultsB },
      winner: resultsA.results.filter(r => r.success).length > 
              resultsB.results.filter(r => r.success).length ? buildA : buildB,
      statisticalSignificance: 0.85 // Simplified for demo
    };
    
    res.json(comparison);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get performance metrics
app.get('/api/metrics', (req, res) => {
  const metrics = {
    totalBuilds: contextOptimizer.builds.size,
    totalTests: contextOptimizer.testResults.length,
    totalOptimizations: contextOptimizer.optimizationHistory.length,
    averageSuccessRate: Array.from(contextOptimizer.builds.values())
      .reduce((sum, build) => sum + build.successRate, 0) / contextOptimizer.builds.size,
    performanceHistory: contextOptimizer.testResults.slice(-7) // Last 7 test runs
  };
  
  res.json(metrics);
});

// Webhook endpoints for data ingestion
app.post('/webhooks/slack', async (req, res) => {
  try {
    // Process Slack webhook data
    const slackData = req.body;
    
    // Store in Azure Storage
    const containerClient = blobServiceClient.getContainerClient('slack-data');
    const blobName = `slack-${Date.now()}.json`;
    const blobClient = containerClient.getBlockBlobClient(blobName);
    
    await blobClient.upload(JSON.stringify(slackData), JSON.stringify(slackData).length);
    
    res.json({ status: 'received' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/webhooks/github', async (req, res) => {
  try {
    // Process GitHub webhook data
    const githubData = req.body;
    
    // Store in Azure Storage
    const containerClient = blobServiceClient.getContainerClient('github-data');
    const blobName = `github-${Date.now()}.json`;
    const blobClient = containerClient.getBlockBlobClient(blobName);
    
    await blobClient.upload(JSON.stringify(githubData), JSON.stringify(githubData).length);
    
    res.json({ status: 'received' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/webhooks/jira', async (req, res) => {
  try {
    // Process Jira webhook data
    const jiraData = req.body;
    
    // Store in Azure Storage
    const containerClient = blobServiceClient.getContainerClient('jira-data');
    const blobName = `jira-${Date.now()}.json`;
    const blobClient = containerClient.getBlockBlobClient(blobName);
    
    await blobClient.upload(JSON.stringify(jiraData), JSON.stringify(jiraData).length);
    
    res.json({ status: 'received' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Initialize sample data
async function initializeSampleData() {
  // Create sample builds
  const crudSpecialist = new ContextBuild(
    'CRUD Specialist',
    'v3.2',
    [
      { name: 'CRUD Patterns', content: 'REST API patterns...', tokenCount: 800 },
      { name: 'Validation', content: 'Input validation...', tokenCount: 600 },
      { name: 'Error Handling', content: 'Database errors...', tokenCount: 500 },
      { name: 'Testing', content: 'CRUD test patterns...', tokenCount: 400 }
    ],
    2500
  );
  crudSpecialist.successRate = 94;
  crudSpecialist.tokenEfficiency = 47.2;
  crudSpecialist.timeToGreen = 1.8;
  crudSpecialist.specializations = ['Database Operations', 'REST APIs', 'Validation'];
  crudSpecialist.weaknesses = ['Complex Business Logic', 'Performance Optimization'];

  const authTank = new ContextBuild(
    'AuthGuard Pro',
    'v2.1',
    [
      { name: 'OAuth Patterns', content: 'OAuth 2.0 flow...', tokenCount: 1200 },
      { name: 'JWT Management', content: 'JWT token handling...', tokenCount: 800 },
      { name: 'Session Handling', content: 'Session management...', tokenCount: 700 },
      { name: 'Security Patterns', content: 'Security best practices...', tokenCount: 600 }
    ],
    4200
  );
  authTank.successRate = 87;
  authTank.tokenEfficiency = 34.8;
  authTank.timeToGreen = 3.2;
  authTank.specializations = ['OAuth', 'JWT', 'Security'];
  authTank.weaknesses = ['Simple Prototypes', 'Performance'];

  contextOptimizer.builds.set(crudSpecialist.id, crudSpecialist);
  contextOptimizer.builds.set(authTank.id, authTank);
}

// Start server
app.listen(port, () => {
  console.log(`🚀 Context Engineering Platform running on port ${port}`);
  console.log(`📊 Dashboard: http://localhost:${port}`);
  console.log(`🔍 Health Check: http://localhost:${port}/health`);
  console.log(`📡 API: http://localhost:${port}/api`);
  
  // Initialize sample data
  initializeSampleData();
});

module.exports = app;