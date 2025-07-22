import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Area, AreaChart, Treemap, Cell, ScatterChart, Scatter } from 'recharts';
import { Trophy, Target, Zap, TrendingUp, Award, Star, Settings, Play, Pause, RotateCcw, Brain, ChevronRight, ArrowUp, ArrowDown, Medal, Crown, Flame, Users, Clock, Activity, Cpu, Database, Code, Shield, Layers, FileText, TestTube, GitBranch, Sparkles, Rocket, Gamepad2, Swords, TrendingDown, Plus, Edit, Trash2, Copy, Download, Upload, Filter, Search, MoreVertical, CheckCircle, XCircle, AlertTriangle, Info, DollarSign, Coins, Network, Server, Bot, Webhook, Key, Eye, EyeOff, Sigma, BarChart3, PieChart, Gauge, Microscope, Beaker, Dna, Globe, Link, MessageSquare, Github, Slack, GitMerge, BookOpen } from 'lucide-react';

// Type definitions
interface Notification {
  id: number;
  message: string;
  type: string;
  timestamp: Date;
}

interface ContextBuild {
  id: string;
  name: string;
  version: string;
  level: string;
  rarity: string;
  successRate: number;
  tokenEfficiency: number;
  timeToGreen: number;
  tokenBudget: number;
  tokensUsed: number;
  confidenceInterval: [number, number];
  uncertaintyScore: number;
  causalFactors: string[];
  specializations: string[];
  weaknesses: string[];
  lastOptimized: string;
  trending: string;
  winStreak: number;
  totalTests: number;
  averageScore: number;
  mcpSources: string[];
  generalizationBound: number;
  epistemicUncertainty: number;
  aleatoricUncertainty: number;
  elements: Array<{
    name: string;
    tokens: number;
    performance: number;
    causalImpact: number;
  }>;
}

const SelfImprovingRAGPlatform = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [selectedBuild, setSelectedBuild] = useState('crud-specialist');
  const [currentLevel, setCurrentLevel] = useState(12);
  const [xp, setXp] = useState(2847);
  const [nextLevelXp] = useState(3000);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isAbTesting, setIsAbTesting] = useState(false);
  const [selectedBuildsForComparison, setSelectedBuildsForComparison] = useState<string[]>([]);
  const [tokenBalance, setTokenBalance] = useState(15000);
  const [isBetting, setIsBetting] = useState(false);
  const [betAmount, setBetAmount] = useState(1000);
  const [selectedOptimizationTarget, setSelectedOptimizationTarget] = useState('success_rate');
  const [mcpServerStatus, setMcpServerStatus] = useState({});
  const [uncertaintyView, setUncertaintyView] = useState(false);
  const [causalAnalysisEnabled, setCausalAnalysisEnabled] = useState(true);

  // Performance History Data
  const [performanceHistory] = useState([
    { day: 'Mon', successRate: 78, tokenEfficiency: 32.1, xpGained: 120, testsRun: 24 },
    { day: 'Tue', successRate: 82, tokenEfficiency: 35.4, xpGained: 145, testsRun: 31 },
    { day: 'Wed', successRate: 89, tokenEfficiency: 41.2, xpGained: 180, testsRun: 28 },
    { day: 'Thu', successRate: 94, tokenEfficiency: 47.2, xpGained: 220, testsRun: 35 },
    { day: 'Fri', successRate: 91, tokenEfficiency: 44.8, xpGained: 195, testsRun: 29 },
    { day: 'Sat', successRate: 96, tokenEfficiency: 52.1, xpGained: 280, testsRun: 42 },
    { day: 'Sun', successRate: 88, tokenEfficiency: 39.7, xpGained: 165, testsRun: 26 }
  ]);

  // Leaderboard Data
  const [leaderboard] = useState([
    { rank: 1, name: 'Alex Chen', level: 15, successRate: 96.2, badge: 'Context Master', streak: 12, totalXP: 4850, weeklyXP: 450 },
    { rank: 2, name: 'You', level: 12, successRate: 94.1, badge: 'Optimizer', streak: 8, totalXP: 2847, weeklyXP: 380 },
    { rank: 3, name: 'Sarah Kim', level: 14, successRate: 92.8, badge: 'Efficiency Expert', streak: 6, totalXP: 4200, weeklyXP: 320 },
    { rank: 4, name: 'Mike Rodriguez', level: 11, successRate: 89.5, badge: 'Build Specialist', streak: 4, totalXP: 2650, weeklyXP: 285 },
    { rank: 5, name: 'Emily Davis', level: 13, successRate: 87.3, badge: 'Token Saver', streak: 3, totalXP: 3200, weeklyXP: 210 }
  ]);

  // Achievements Data
  const [achievements] = useState([
    { id: 1, name: 'Context Optimizer', description: 'Achieved 90%+ success rate', icon: Target, unlocked: true, rarity: 'gold', xp: 200, date: '2024-01-15' },
    { id: 2, name: 'Token Efficiency Master', description: 'Reached 50+ token efficiency', icon: Zap, unlocked: true, rarity: 'gold', xp: 300, date: '2024-01-18' },
    { id: 3, name: 'Speed Demon', description: 'Sub-2 minute time to green', icon: TrendingUp, unlocked: true, rarity: 'silver', xp: 150, date: '2024-01-20' },
    { id: 4, name: 'Perfect Week', description: 'No failed builds for 7 days', icon: Award, unlocked: false, rarity: 'legendary', xp: 500 },
    { id: 5, name: 'Context Alchemist', description: 'Created 5 specialized builds', icon: Star, unlocked: true, rarity: 'epic', xp: 400, date: '2024-01-22' },
    { id: 6, name: 'Win Streak Master', description: '10+ consecutive successful optimizations', icon: Flame, unlocked: true, rarity: 'epic', xp: 350, date: '2024-01-21' },
    { id: 7, name: 'Team Player', description: 'Shared 3 builds with team', icon: Users, unlocked: false, rarity: 'silver', xp: 200 },
    { id: 8, name: 'Data Scientist', description: 'Completed 100 A/B tests', icon: TestTube, unlocked: false, rarity: 'gold', xp: 300 }
  ]);

  // Enhanced mock data for the full platform
  const [contextBuilds] = useState<ContextBuild[]>([
    {
      id: 'crud-specialist',
      name: 'CRUD Specialist',
      version: 'v3.2',
      level: 'Epic',
      rarity: 'epic',
      successRate: 94.2,
      tokenEfficiency: 47.2,
      timeToGreen: 1.8,
      tokenBudget: 2500,
      tokensUsed: 2100,
      confidenceInterval: [92.1, 96.3],
      uncertaintyScore: 0.12,
      causalFactors: ['pattern_quality', 'validation_rules', 'error_handling'],
      specializations: ['Database Operations', 'REST APIs', 'Validation'],
      weaknesses: ['Complex Business Logic', 'Performance Optimization'],
      lastOptimized: '2 hours ago',
      trending: 'up',
      winStreak: 8,
      totalTests: 156,
      averageScore: 4.7,
      mcpSources: ['database-patterns', 'api-design', 'validation-rules'],
      generalizationBound: 0.089,
      epistemicUncertainty: 0.067,
      aleatoricUncertainty: 0.043,
      elements: [
        { name: 'CRUD Patterns', tokens: 800, performance: 92, causalImpact: 0.34 },
        { name: 'Validation Logic', tokens: 600, performance: 89, causalImpact: 0.28 },
        { name: 'Error Handling', tokens: 500, performance: 87, causalImpact: 0.21 },
        { name: 'Test Patterns', tokens: 200, performance: 85, causalImpact: 0.17 }
      ]
    },
    {
      id: 'auth-tank',
      name: 'AuthGuard Pro',
      version: 'v2.1',
      level: 'Legendary',
      rarity: 'legendary',
      successRate: 87.4,
      tokenEfficiency: 34.8,
      timeToGreen: 3.2,
      tokenBudget: 4200,
      tokensUsed: 3850,
      confidenceInterval: [84.7, 90.1],
      uncertaintyScore: 0.18,
      causalFactors: ['oauth_complexity', 'jwt_handling', 'security_patterns'],
      specializations: ['OAuth', 'JWT', 'Security'],
      weaknesses: ['Simple Prototypes', 'Performance'],
      lastOptimized: '1 day ago',
      trending: 'stable',
      winStreak: 12,
      totalTests: 203,
      averageScore: 4.9,
      mcpSources: ['auth-patterns', 'security-protocols', 'jwt-best-practices'],
      generalizationBound: 0.156,
      epistemicUncertainty: 0.089,
      aleatoricUncertainty: 0.067,
      elements: [
        { name: 'OAuth Flows', tokens: 1200, performance: 91, causalImpact: 0.41 },
        { name: 'JWT Handling', tokens: 800, performance: 88, causalImpact: 0.29 },
        { name: 'Session Management', tokens: 700, performance: 86, causalImpact: 0.18 },
        { name: 'Security Patterns', tokens: 600, performance: 84, causalImpact: 0.12 }
      ]
    },
    {
      id: 'integration-cannon',
      name: 'IntegrationMaster',
      version: 'v1.9',
      level: 'Rare',
      rarity: 'rare',
      successRate: 82.1,
      tokenEfficiency: 26.5,
      timeToGreen: 2.1,
      tokenBudget: 3100,
      tokensUsed: 2900,
      confidenceInterval: [79.3, 84.9],
      uncertaintyScore: 0.21,
      causalFactors: ['api_complexity', 'error_recovery', 'rate_limiting'],
      specializations: ['API Integration', 'Error Handling'],
      weaknesses: ['Greenfield Development'],
      lastOptimized: '5 days ago',
      trending: 'down',
      winStreak: 3,
      totalTests: 98,
      averageScore: 4.2,
      mcpSources: ['api-integration', 'retry-patterns', 'rate-limiting'],
      generalizationBound: 0.187,
      epistemicUncertainty: 0.123,
      aleatoricUncertainty: 0.087,
      elements: [
        { name: 'API Patterns', tokens: 900, performance: 85, causalImpact: 0.38 },
        { name: 'Rate Limiting', tokens: 600, performance: 82, causalImpact: 0.25 },
        { name: 'Retry Logic', tokens: 500, performance: 80, causalImpact: 0.22 },
        { name: 'Response Mapping', tokens: 400, performance: 78, causalImpact: 0.15 }
      ]
    },
    {
      id: 'ui-wizard',
      name: 'UI Component Wizard',
      version: 'v2.0',
      level: 'Epic',
      rarity: 'epic',
      successRate: 91.3,
      tokenEfficiency: 42.1,
      timeToGreen: 1.5,
      tokenBudget: 2800,
      tokensUsed: 2400,
      confidenceInterval: [89.1, 93.5],
      uncertaintyScore: 0.14,
      causalFactors: ['component_patterns', 'styling_consistency', 'accessibility'],
      specializations: ['React Components', 'Styling', 'Accessibility'],
      weaknesses: ['Backend Logic', 'Database Operations'],
      lastOptimized: '3 hours ago',
      trending: 'up',
      winStreak: 15,
      totalTests: 134,
      averageScore: 4.6,
      mcpSources: ['ui-patterns', 'component-library', 'accessibility-guidelines'],
      generalizationBound: 0.098,
      epistemicUncertainty: 0.071,
      aleatoricUncertainty: 0.069,
      elements: [
        { name: 'Component Patterns', tokens: 800, performance: 93, causalImpact: 0.35 },
        { name: 'Styling Systems', tokens: 600, performance: 90, causalImpact: 0.27 },
        { name: 'Accessibility', tokens: 500, performance: 88, causalImpact: 0.23 },
        { name: 'State Management', tokens: 500, performance: 92, causalImpact: 0.15 }
      ]
    }
  ]);

  // MCP Server Status
  const [mcpServers] = useState([
    {
      id: 'auth-patterns',
      name: 'Authentication Patterns',
      status: 'healthy',
      domain: 'authentication',
      lastSync: '2 minutes ago',
      dataQuality: 96.2,
      sources: ['slack-auth-channel', 'github-auth-repos', 'confluence-auth-docs'],
      requestCount: 1247,
      avgResponseTime: 120,
      errorRate: 0.8
    },
    {
      id: 'api-design',
      name: 'API Design Patterns',
      status: 'healthy',
      domain: 'api_patterns',
      lastSync: '5 minutes ago',
      dataQuality: 94.7,
      sources: ['github-api-repos', 'swagger-docs', 'postman-collections'],
      requestCount: 2341,
      avgResponseTime: 95,
      errorRate: 1.2
    },
    {
      id: 'database-patterns',
      name: 'Database Operations',
      status: 'degraded',
      domain: 'database',
      lastSync: '15 minutes ago',
      dataQuality: 89.3,
      sources: ['github-db-repos', 'dba-slack-channel', 'db-migration-logs'],
      requestCount: 876,
      avgResponseTime: 180,
      errorRate: 4.2
    },
    {
      id: 'ui-patterns',
      name: 'UI Component Library',
      status: 'healthy',
      domain: 'frontend',
      lastSync: '1 minute ago',
      dataQuality: 97.8,
      sources: ['storybook', 'figma-designs', 'component-tests'],
      requestCount: 1832,
      avgResponseTime: 85,
      errorRate: 0.3
    }
  ]);

  // API Usage Statistics
  const [apiUsage] = useState({
    totalRequests: 15247,
    successRate: 94.2,
    avgResponseTime: 1.8,
    tokensSaved: 125000,
    costSavings: 312.50,
    topUseCases: [
      { name: 'CRUD Generation', requests: 4523, successRate: 94.2 },
      { name: 'Auth Implementation', requests: 3241, successRate: 87.4 },
      { name: 'API Design', requests: 2876, successRate: 91.3 },
      { name: 'UI Components', requests: 2134, successRate: 93.1 },
      { name: 'Data Migration', requests: 1987, successRate: 82.1 }
    ]
  });

  // Token Betting History
  const [betHistory] = useState([
    {
      id: 1,
      buildId: 'crud-specialist',
      amount: 1500,
      target: 'success_rate',
      expectedImprovement: 2.5,
      actualImprovement: 3.1,
      payout: 2200,
      timestamp: '2 hours ago',
      status: 'won'
    },
    {
      id: 2,
      buildId: 'auth-tank',
      amount: 2000,
      target: 'token_efficiency',
      expectedImprovement: 5.0,
      actualImprovement: 3.2,
      payout: 800,
      timestamp: '1 day ago',
      status: 'partial'
    },
    {
      id: 3,
      buildId: 'ui-wizard',
      amount: 1000,
      target: 'time_to_green',
      expectedImprovement: 15.0,
      actualImprovement: 8.2,
      payout: 0,
      timestamp: '3 days ago',
      status: 'lost'
    }
  ]);

  // Company Data Sources
  const [dataSources] = useState([
    {
      name: 'Slack Engineering',
      type: 'slack',
      status: 'connected',
      lastSync: '5 minutes ago',
      messagesProcessed: 15234,
      qualityScore: 94.2,
      insights: ['Authentication discussions', 'Bug resolution patterns', 'Architecture decisions']
    },
    {
      name: 'GitHub Repositories',
      type: 'github',
      status: 'connected',
      lastSync: '2 minutes ago',
      messagesProcessed: 8567,
      qualityScore: 96.8,
      insights: ['Code patterns', 'PR review feedback', 'Commit message analysis']
    },
    {
      name: 'Jira Projects',
      type: 'jira',
      status: 'connected',
      lastSync: '10 minutes ago',
      messagesProcessed: 4321,
      qualityScore: 89.7,
      insights: ['Requirement patterns', 'User story structures', 'Bug classifications']
    },
    {
      name: 'Confluence Docs',
      type: 'confluence',
      status: 'syncing',
      lastSync: '1 hour ago',
      messagesProcessed: 2134,
      qualityScore: 92.1,
      insights: ['Architecture docs', 'API specifications', 'Best practices']
    }
  ]);

  // Self-Improvement Events
  const [improvementEvents] = useState([
    {
      id: 1,
      type: 'causal_discovery',
      description: 'Identified that validation_rules has 34% causal impact on CRUD success',
      confidence: 0.89,
      implementation: 'Increased validation pattern tokens by 200',
      result: '+3.1% success rate',
      timestamp: '2 hours ago'
    },
    {
      id: 2,
      type: 'statistical_anomaly',
      description: 'Auth patterns showing declining performance on weekend deployments',
      confidence: 0.76,
      implementation: 'Added weekend-specific error handling patterns',
      result: '+1.8% weekend success rate',
      timestamp: '1 day ago'
    },
    {
      id: 3,
      type: 'pattern_emergence',
      description: 'New GraphQL integration pattern detected in 15+ repositories',
      confidence: 0.94,
      implementation: 'Created new GraphQL context element',
      result: 'New use case unlocked',
      timestamp: '3 days ago'
    }
  ]);

  const selectedBuildData = contextBuilds.find(build => build.id === selectedBuild);

  const radarData = [
    { subject: 'Success Rate', A: selectedBuildData?.successRate || 0, B: 100, fullMark: 100 },
    { subject: 'Token Efficiency', A: selectedBuildData?.tokenEfficiency || 0, B: 60, fullMark: 60 },
    { subject: 'Speed', A: Math.max(0, 10 - (selectedBuildData?.timeToGreen || 0)) * 10, B: 100, fullMark: 100 },
    { subject: 'Confidence', A: (1 - (selectedBuildData?.uncertaintyScore || 0)) * 100, B: 100, fullMark: 100 },
    { subject: 'Generalization', A: (1 - (selectedBuildData?.generalizationBound || 0)) * 100, B: 100, fullMark: 100 },
    { subject: 'Reliability', A: (selectedBuildData?.successRate || 0) - 5, B: 100, fullMark: 100 }
  ];

  const startOptimization = () => {
    setIsOptimizing(true);
    addNotification('Optimization started for ' + selectedBuildData?.name, 'info');
    
    setTimeout(() => {
      setIsOptimizing(false);
      setXp(prev => prev + 150);
      addNotification('Optimization complete! +3% success rate, +150 XP', 'success');
    }, 3000);
  };

  const startABTest = () => {
    if (selectedBuildsForComparison.length !== 2) {
      addNotification('Select exactly 2 builds for A/B testing', 'warning');
      return;
    }
    
    setIsAbTesting(true);
    addNotification('A/B test started', 'info');
    
    setTimeout(() => {
      setIsAbTesting(false);
      setXp(prev => prev + 75);
      addNotification('A/B test complete! Results available in optimization lab.', 'success');
    }, 4000);
  };

  const placeBet = () => {
    if (betAmount > tokenBalance) {
      addNotification('Insufficient tokens for this bet', 'error');
      return;
    }

    setIsBetting(true);
    setTokenBalance(prev => prev - betAmount);
    addNotification(`Placed ${betAmount} token bet on ${selectedOptimizationTarget}`, 'info');

    setTimeout(() => {
      setIsBetting(false);
      const success = Math.random() > 0.3; // 70% chance of success
      const payout = success ? betAmount * 1.8 : betAmount * 0.2;
      setTokenBalance(prev => prev + payout);
      setXp(prev => prev + (success ? 200 : 50));
      
      addNotification(
        success 
          ? `Bet won! +${Math.round(payout - betAmount)} tokens, +200 XP`
          : `Bet partially successful. +${Math.round(payout)} tokens, +50 XP`,
        success ? 'success' : 'warning'
      );
    }, 4000);
  };

  const addNotification = (message: string, type: string) => {
    const notification: Notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date()
    };
    setNotifications(prev => [notification, ...prev.slice(0, 4)]);
    
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  const getLevelColor = (level: string) => {
    switch(level) {
      case 'Legendary': return 'text-purple-400 bg-purple-900/30 border-purple-500';
      case 'Epic': return 'text-orange-400 bg-orange-900/30 border-orange-500';
      case 'Rare': return 'text-blue-400 bg-blue-900/30 border-blue-500';
      default: return 'text-gray-400 bg-gray-900/30 border-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'healthy': return 'text-green-400 bg-green-900/30';
      case 'degraded': return 'text-yellow-400 bg-yellow-900/30';
      case 'error': return 'text-red-400 bg-red-900/30';
      default: return 'text-gray-400 bg-gray-900/30';
    }
  };

  const getRarityColor = (rarity: string) => {
    switch(rarity) {
      case 'legendary': return 'text-purple-400';
      case 'epic': return 'text-orange-400';
      case 'gold': return 'text-yellow-400';
      case 'silver': return 'text-gray-300';
      case 'rare': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const getBadgeIcon = (rank: number) => {
    switch(rank) {
      case 1: return <Crown className="w-5 h-5 text-yellow-400" />;
      case 2: return <Medal className="w-5 h-5 text-gray-300" />;
      case 3: return <Medal className="w-5 h-5 text-orange-400" />;
      default: return <Star className="w-4 h-4 text-gray-500" />;
    }
  };

  const getSourceIcon = (type: string) => {
    switch(type) {
      case 'slack': return <MessageSquare className="w-4 h-4" />;
      case 'github': return <Github className="w-4 h-4" />;
      case 'jira': return <FileText className="w-4 h-4" />;
      case 'confluence': return <BookOpen className="w-4 h-4" />;
      default: return <Database className="w-4 h-4" />;
    }
  };

  const toggleBuildForComparison = (buildId: string) => {
    setSelectedBuildsForComparison(prev => {
      if (prev.includes(buildId)) {
        return prev.filter(id => id !== buildId);
      } else if (prev.length < 2) {
        return [...prev, buildId];
      } else {
        return [prev[1], buildId]; // Replace first selection
      }
    });
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Enhanced Header with Token Balance */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Brain className="w-8 h-8 text-blue-400" />
            <div>
              <h1 className="text-xl font-bold">Self-Improving AI Context Engineering Platform</h1>
              <p className="text-sm text-gray-400">Agentic RAG + MCP + Statistical Optimization</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            {/* Token Balance */}
            <div className="flex items-center space-x-2 bg-gray-700 rounded-lg px-3 py-2">
              <Coins className="w-5 h-5 text-yellow-400" />
              <div className="text-right">
                <div className="text-sm font-medium">{tokenBalance.toLocaleString()} Tokens</div>
                <div className="text-xs text-gray-400">Available for betting</div>
              </div>
            </div>

            {/* Notifications */}
            {notifications.length > 0 && (
              <div className="relative">
                <div className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs">
                  {notifications.length}
                </div>
                <div className="w-6 h-6 bg-blue-600 rounded-full"></div>
              </div>
            )}
            
            {/* XP and Level */}
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <div className="text-sm font-medium">Level {currentLevel}</div>
                <div className="text-xs text-gray-400">{xp}/{nextLevelXp} XP</div>
              </div>
              <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                  style={{ width: `${(xp / nextLevelXp) * 100}%` }}
                />
              </div>
              {xp > 2800 && <Flame className="w-5 h-5 text-orange-400 animate-pulse" />}
            </div>

            {/* Uncertainty Toggle */}
            <button
              onClick={() => setUncertaintyView(!uncertaintyView)}
              className={`p-2 rounded ${uncertaintyView ? 'bg-purple-600' : 'bg-gray-600'}`}
              title="Toggle uncertainty visualization"
            >
              <Sigma className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Enhanced Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex space-x-6">
          {[
            { id: 'dashboard', name: 'Dashboard', icon: TrendingUp },
            { id: 'builds', name: 'Context Builds', icon: Settings },
            { id: 'betting', name: 'Token Betting', icon: Coins },
            { id: 'mcp-servers', name: 'MCP Servers', icon: Server },
            { id: 'api-usage', name: 'API Usage', icon: Globe },
            { id: 'data-sources', name: 'Data Sources', icon: Database },
            { id: 'self-improvement', name: 'Self-Improvement', icon: Bot },
            { id: 'optimization', name: 'Optimization Lab', icon: Target },
            { id: 'leaderboard', name: 'Leaderboard', icon: Trophy },
            { id: 'achievements', name: 'Achievements', icon: Award },
            { id: 'analytics', name: 'Analytics', icon: Activity }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.name}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Enhanced Performance Overview */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Performance Metrics</h2>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setUncertaintyView(!uncertaintyView)}
                      className={`px-3 py-1 rounded text-sm ${
                        uncertaintyView ? 'bg-purple-600' : 'bg-gray-600'
                      }`}
                    >
                      {uncertaintyView ? 'Hide' : 'Show'} Uncertainty
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Success Rate</p>
                        <p className="text-2xl font-bold text-green-400">94.2%</p>
                        {uncertaintyView && (
                          <p className="text-xs text-purple-400">CI: 92.1-96.3%</p>
                        )}
                        <p className="text-xs text-green-400">+2.3% this week</p>
                      </div>
                      <ArrowUp className="w-5 h-5 text-green-400" />
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Token Efficiency</p>
                        <p className="text-2xl font-bold text-blue-400">47.2</p>
                        {uncertaintyView && (
                          <p className="text-xs text-purple-400">σ: ±3.4</p>
                        )}
                        <p className="text-xs text-blue-400">+5.1 this week</p>
                      </div>
                      <ArrowUp className="w-5 h-5 text-green-400" />
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Avg Time to Green</p>
                        <p className="text-2xl font-bold text-purple-400">1.8m</p>
                        {uncertaintyView && (
                          <p className="text-xs text-purple-400">Range: 1.2-2.4m</p>
                        )}
                        <p className="text-xs text-green-400">-0.4m this week</p>
                      </div>
                      <ArrowDown className="w-5 h-5 text-green-400" />
                    </div>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Token Balance</p>
                        <p className="text-2xl font-bold text-yellow-400">{tokenBalance.toLocaleString()}</p>
                        <p className="text-xs text-yellow-400">+2.5K this week</p>
                      </div>
                      <Coins className="w-5 h-5 text-yellow-400" />
                    </div>
                  </div>
                </div>
                
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={performanceHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="day" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                      labelStyle={{ color: '#F3F4F6' }}
                    />
                    <Area type="monotone" dataKey="successRate" stackId="1" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="tokenEfficiency" stackId="2" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Self-Improvement Events */}
              <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4">Recent Self-Improvements</h2>
                <div className="space-y-3">
                  {improvementEvents.map(event => (
                    <div key={event.id} className="bg-gray-700 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <Bot className="w-4 h-4 text-blue-400" />
                            <span className="text-sm font-medium capitalize">
                              {event.type.replace('_', ' ')}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${
                              event.confidence > 0.8 ? 'bg-green-900/30 text-green-400' :
                              event.confidence > 0.6 ? 'bg-yellow-900/30 text-yellow-400' :
                              'bg-red-900/30 text-red-400'
                            }`}>
                              {Math.round(event.confidence * 100)}% confidence
                            </span>
                          </div>
                          <p className="text-sm text-gray-300 mb-2">{event.description}</p>
                          <p className="text-xs text-gray-400">Implementation: {event.implementation}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-sm text-green-400">{event.result}</span>
                            <span className="text-xs text-gray-500">{event.timestamp}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Enhanced Right Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions with Token Betting */}
              <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  <button 
                    onClick={startOptimization}
                    disabled={isOptimizing}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                  >
                    {isOptimizing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Optimizing...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        <span>Start Optimization</span>
                      </>
                    )}
                  </button>
                  
                  <button 
                    onClick={() => setActiveTab('betting')}
                    className="w-full bg-yellow-600 hover:bg-yellow-700 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                  >
                    <Coins className="w-4 h-4" />
                    <span>Place Token Bet</span>
                  </button>
                  
                  <button 
                    onClick={() => setActiveTab('mcp-servers')}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                  >
                    <Server className="w-4 h-4" />
                    <span>Manage MCP Servers</span>
                  </button>
                  
                  <button 
                    onClick={() => setActiveTab('api-usage')}
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                  >
                    <Globe className="w-4 h-4" />
                    <span>View API Usage</span>
                  </button>
                </div>
              </div>

              {/* MCP Server Status */}
              <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4">MCP Server Status</h2>
                <div className="space-y-3">
                  {mcpServers.slice(0, 4).map(server => (
                    <div key={server.id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${
                          server.status === 'healthy' ? 'bg-green-400' :
                          server.status === 'degraded' ? 'bg-yellow-400' : 'bg-red-400'
                        }`}></div>
                        <span className="text-sm">{server.name}</span>
                      </div>
                      <span className="text-xs text-gray-400">{server.dataQuality}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Token Bets */}
              <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4">Recent Bets</h2>
                <div className="space-y-3">
                  {betHistory.slice(0, 3).map(bet => (
                    <div key={bet.id} className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        <Coins className={`w-4 h-4 ${
                          bet.status === 'won' ? 'text-green-400' :
                          bet.status === 'partial' ? 'text-yellow-400' : 'text-red-400'
                        }`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">
                          {bet.amount} on {bet.target.replace('_', ' ')}
                        </p>
                        <p className="text-xs text-gray-400">
                          Expected: +{bet.expectedImprovement}% | Actual: +{bet.actualImprovement}%
                        </p>
                        <div className="flex items-center justify-between">
                          <span className={`text-xs ${
                            bet.status === 'won' ? 'text-green-400' :
                            bet.status === 'partial' ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {bet.status === 'won' ? '+' : bet.status === 'partial' ? '+' : ''}{bet.payout}
                          </span>
                          <span className="text-xs text-gray-500">{bet.timestamp}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'betting' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-6">Token Betting System</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Betting Interface */}
                <div className="space-y-6">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-medium mb-4">Place New Bet</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Select Build
                        </label>
                        <select 
                          value={selectedBuild} 
                          onChange={(e) => setSelectedBuild(e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                        >
                          {contextBuilds.map(build => (
                            <option key={build.id} value={build.id}>
                              {build.name} {build.version}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Optimization Target
                        </label>
                        <select 
                          value={selectedOptimizationTarget} 
                          onChange={(e) => setSelectedOptimizationTarget(e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                        >
                          <option value="success_rate">Success Rate</option>
                          <option value="token_efficiency">Token Efficiency</option>
                          <option value="time_to_green">Time to Green</option>
                          <option value="uncertainty_reduction">Uncertainty Reduction</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Bet Amount: {betAmount} tokens
                        </label>
                        <input
                          type="range"
                          min="100"
                          max={Math.min(5000, tokenBalance)}
                          value={betAmount}
                          onChange={(e) => setBetAmount(parseInt(e.target.value))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-400 mt-1">
                          <span>100</span>
                          <span>{Math.min(5000, tokenBalance)}</span>
                        </div>
                      </div>

                      <div className="bg-gray-600 rounded p-3">
                        <h4 className="text-sm font-medium mb-2">Bet Analysis</h4>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Current Performance:</span>
                            <span>{selectedBuildData?.successRate}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Estimated Odds:</span>
                            <span className="text-green-400">1.8x payout</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Success Probability:</span>
                            <span className="text-yellow-400">65%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Expected Return:</span>
                            <span className="text-blue-400">+{Math.round(betAmount * 0.17)}</span>
                          </div>
                        </div>
                      </div>

                      <button 
                        onClick={placeBet}
                        disabled={isBetting || betAmount > tokenBalance}
                        className="w-full bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                      >
                        {isBetting ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Processing Bet...</span>
                          </>
                        ) : (
                          <>
                            <Coins className="w-4 h-4" />
                            <span>Place Bet ({betAmount} tokens)</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Betting History & Statistics */}
                <div className="space-y-6">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-medium mb-4">Betting Statistics</h3>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">68%</div>
                        <div className="text-sm text-gray-400">Win Rate</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">+2,340</div>
                        <div className="text-sm text-gray-400">Net Tokens</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">23</div>
                        <div className="text-sm text-gray-400">Total Bets</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-400">1.6x</div>
                        <div className="text-sm text-gray-400">Avg Multiplier</div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-medium mb-4">Recent Bets</h3>
                    <div className="space-y-3">
                      {betHistory.map(bet => (
                        <div key={bet.id} className="flex items-center justify-between bg-gray-600 rounded p-3">
                          <div>
                            <div className="text-sm font-medium">
                              {bet.amount} on {bet.target.replace('_', ' ')}
                            </div>
                            <div className="text-xs text-gray-400">{bet.timestamp}</div>
                          </div>
                          <div className="text-right">
                            <div className={`text-sm font-medium ${
                              bet.status === 'won' ? 'text-green-400' :
                              bet.status === 'partial' ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {bet.status === 'won' ? '+' : bet.status === 'partial' ? '+' : ''}{bet.payout}
                            </div>
                            <div className="text-xs text-gray-400 capitalize">{bet.status}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'mcp-servers' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">MCP Server Management</h2>
              <button className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Add MCP Server</span>
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {mcpServers.map(server => (
                <div key={server.id} className="bg-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <Server className="w-5 h-5 text-blue-400" />
                      <div>
                        <h3 className="font-semibold">{server.name}</h3>
                        <p className="text-sm text-gray-400">{server.domain}</p>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded text-xs ${getStatusColor(server.status)}`}>
                      {server.status}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-400">Data Quality</p>
                      <p className="text-lg font-semibold text-green-400">{server.dataQuality}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Requests</p>
                      <p className="text-lg font-semibold text-blue-400">{server.requestCount.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Avg Response</p>
                      <p className="text-lg font-semibold text-purple-400">{server.avgResponseTime}ms</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Error Rate</p>
                      <p className="text-lg font-semibold text-red-400">{server.errorRate}%</p>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-400 mb-2">Data Sources</p>
                    <div className="flex flex-wrap gap-2">
                      {server.sources.map((source, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-700 rounded text-xs">
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Last sync: {server.lastSync}</span>
                    <div className="flex space-x-2">
                      <button className="text-blue-400 hover:text-blue-300">
                        <Settings className="w-4 h-4" />
                      </button>
                      <button className="text-green-400 hover:text-green-300">
                        <Play className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'api-usage' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">API Usage Analytics</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Requests</p>
                    <p className="text-2xl font-bold text-blue-400">{apiUsage.totalRequests.toLocaleString()}</p>
                    <p className="text-xs text-green-400">+12% this week</p>
                  </div>
                  <Globe className="w-8 h-8 text-blue-400" />
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Success Rate</p>
                    <p className="text-2xl font-bold text-green-400">{apiUsage.successRate}%</p>
                    <p className="text-xs text-green-400">+1.8% this week</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-400" />
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Avg Response Time</p>
                    <p className="text-2xl font-bold text-purple-400">{apiUsage.avgResponseTime}s</p>
                    <p className="text-xs text-green-400">-0.3s this week</p>
                  </div>
                  <Clock className="w-8 h-8 text-purple-400" />
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Cost Savings</p>
                    <p className="text-2xl font-bold text-yellow-400">${apiUsage.costSavings}</p>
                    <p className="text-xs text-yellow-400">{apiUsage.tokensSaved.toLocaleString()} tokens</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-yellow-400" />
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Top Use Cases</h3>
              <div className="space-y-3">
                {apiUsage.topUseCases.map((useCase, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-700 rounded p-3">
                    <div className="flex items-center space-x-3">
                      <div className="text-lg font-bold text-gray-400">#{index + 1}</div>
                      <div>
                        <div className="font-medium">{useCase.name}</div>
                        <div className="text-sm text-gray-400">{useCase.requests.toLocaleString()} requests</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-green-400 font-semibold">{useCase.successRate}%</div>
                      <div className="text-xs text-gray-400">success rate</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'data-sources' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Company Data Sources</h2>
              <button className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Connect Source</span>
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {dataSources.map((source, index) => (
                <div key={index} className="bg-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {getSourceIcon(source.type)}
                      <div>
                        <h3 className="font-semibold">{source.name}</h3>
                        <p className="text-sm text-gray-400">{source.type}</p>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded text-xs ${getStatusColor(source.status)}`}>
                      {source.status}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-400">Messages Processed</p>
                      <p className="text-lg font-semibold text-blue-400">{source.messagesProcessed.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Quality Score</p>
                      <p className="text-lg font-semibold text-green-400">{source.qualityScore}%</p>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-400 mb-2">Key Insights</p>
                    <div className="space-y-1">
                      {source.insights.map((insight, idx) => (
                        <div key={idx} className="text-sm bg-gray-700 rounded px-2 py-1">
                          {insight}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Last sync: {source.lastSync}</span>
                    <div className="flex space-x-2">
                      <button className="text-blue-400 hover:text-blue-300">
                        <Settings className="w-4 h-4" />
                      </button>
                      <button className="text-green-400 hover:text-green-300">
                        <RotateCcw className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'self-improvement' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Self-Improvement Engine</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <Microscope className="w-6 h-6 text-purple-400" />
                  <h3 className="text-lg font-semibold">Causal Analysis</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Active Analyses</span>
                    <span className="text-purple-400 font-semibold">7</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Confidence Avg</span>
                    <span className="text-green-400 font-semibold">0.84</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Interventions</span>
                    <span className="text-blue-400 font-semibold">23</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <Beaker className="w-6 h-6 text-green-400" />
                  <h3 className="text-lg font-semibold">A/B Testing</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Running Tests</span>
                    <span className="text-green-400 font-semibold">5</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Completed</span>
                    <span className="text-blue-400 font-semibold">47</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Success Rate</span>
                    <span className="text-purple-400 font-semibold">73%</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <Dna className="w-6 h-6 text-orange-400" />
                  <h3 className="text-lg font-semibold">Pattern Evolution</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">New Patterns</span>
                    <span className="text-orange-400 font-semibold">12</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Evolved</span>
                    <span className="text-green-400 font-semibold">34</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Deprecated</span>
                    <span className="text-red-400 font-semibold">8</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Improvements</h3>
              <div className="space-y-4">
                {improvementEvents.map(event => (
                  <div key={event.id} className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Bot className="w-4 h-4 text-blue-400" />
                          <span className="text-sm font-medium capitalize">
                            {event.type.replace('_', ' ')}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs ${
                            event.confidence > 0.8 ? 'bg-green-900/30 text-green-400' :
                            event.confidence > 0.6 ? 'bg-yellow-900/30 text-yellow-400' :
                            'bg-red-900/30 text-red-400'
                          }`}>
                            {Math.round(event.confidence * 100)}% confidence
                          </span>
                        </div>
                        <p className="text-sm text-gray-300 mb-2">{event.description}</p>
                        <p className="text-xs text-gray-400 mb-2">Implementation: {event.implementation}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-green-400">{event.result}</span>
                          <span className="text-xs text-gray-500">{event.timestamp}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Causal Factor Analysis</h3>
              <ResponsiveContainer width="100%" height={300}>
                <ScatterChart data={contextBuilds.map(build => ({
                  name: build.name,
                  causalImpact: build.elements.reduce((sum, el) => sum + el.causalImpact, 0),
                  successRate: build.successRate,
                  uncertainty: build.uncertaintyScore * 100
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="causalImpact" stroke="#9CA3AF" name="Causal Impact" />
                  <YAxis dataKey="successRate" stroke="#9CA3AF" name="Success Rate" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                    cursor={{ strokeDasharray: '3 3' }}
                  />
                  <Scatter dataKey="successRate" fill="#3B82F6" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'builds' && selectedBuildData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Enhanced Build Overview with Uncertainty */}
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold">{selectedBuildData.name}</h2>
                  <p className="text-gray-400">{selectedBuildData.version} • {selectedBuildData.level}</p>
                </div>
                <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getLevelColor(selectedBuildData.level)}`}>
                  {selectedBuildData.level}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Success Rate</p>
                  <p className="text-2xl font-bold text-green-400">{selectedBuildData.successRate}%</p>
                  {uncertaintyView && (
                    <p className="text-xs text-purple-400">
                      CI: {selectedBuildData.confidenceInterval[0]}-{selectedBuildData.confidenceInterval[1]}%
                    </p>
                  )}
                  <p className="text-xs text-gray-400">Rank #2 globally</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Token Efficiency</p>
                  <p className="text-2xl font-bold text-blue-400">{selectedBuildData.tokenEfficiency}</p>
                  {uncertaintyView && (
                    <p className="text-xs text-purple-400">
                      Gen Bound: {selectedBuildData.generalizationBound.toFixed(3)}
                    </p>
                  )}
                  <p className="text-xs text-gray-400">Above average</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Uncertainty Score</p>
                  <p className="text-2xl font-bold text-purple-400">{selectedBuildData.uncertaintyScore.toFixed(2)}</p>
                  <p className="text-xs text-gray-400">Lower is better</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Win Streak</p>
                  <p className="text-2xl font-bold text-orange-400">{selectedBuildData.winStreak}</p>
                  <p className="text-xs text-gray-400">Personal best</p>
                </div>
              </div>

              {/* Enhanced Context Elements with Causal Impact */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-300 mb-3">Context Elements</h3>
                <div className="space-y-2">
                  {selectedBuildData.elements.map((element, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-700 rounded p-3">
                      <div>
                        <p className="text-sm font-medium">{element.name}</p>
                        <p className="text-xs text-gray-400">
                          {element.tokens} tokens • {element.performance}% performance
                        </p>
                        {causalAnalysisEnabled && (
                          <p className="text-xs text-purple-400">
                            Causal impact: {Math.round(element.causalImpact * 100)}%
                          </p>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="text-blue-400 hover:text-blue-300">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="text-red-400 hover:text-red-300">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* MCP Sources */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-300 mb-3">MCP Data Sources</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedBuildData.mcpSources.map((source, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-900/30 text-blue-400 rounded text-xs">
                      {source}
                    </span>
                  ))}
                </div>
              </div>

              {/* Specializations & Weaknesses */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-300 mb-2">Specializations</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedBuildData.specializations.map((spec, index) => (
                      <span key={index} className="px-2 py-1 bg-green-900/30 text-green-400 rounded text-xs">
                        {spec}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-300 mb-2">Weaknesses</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedBuildData.weaknesses.map((weakness, index) => (
                      <span key={index} className="px-2 py-1 bg-red-900/30 text-red-400 rounded text-xs">
                        {weakness}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Enhanced Performance Radar with Uncertainty */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Performance Profile</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                  <PolarRadiusAxis 
                    angle={90} 
                    domain={[0, 100]} 
                    tick={{ fill: '#9CA3AF', fontSize: 10 }}
                  />
                  <Radar
                    name="Current"
                    dataKey="A"
                    stroke="#3B82F6"
                    fill="#3B82F6"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                  {uncertaintyView && (
                    <Radar
                      name="Upper Bound"
                      dataKey="B"
                      stroke="#8B5CF6"
                      fill="none"
                      strokeWidth={1}
                      strokeDasharray="5 5"
                    />
                  )}
                </RadarChart>
              </ResponsiveContainer>
              
              <div className="mt-4 grid grid-cols-2 gap-4">
                <button className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm">
                  Optimize Build
                </button>
                <button className="bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg text-sm">
                  Clone Build
                </button>
              </div>
            </div>

            {/* Build Selection remains the same */}
            <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">All Context Builds</h3>
                <div className="flex items-center space-x-2">
                  <button className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg text-sm flex items-center space-x-2">
                    <Plus className="w-4 h-4" />
                    <span>New Build</span>
                  </button>
                  <button className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg text-sm flex items-center space-x-2">
                    <Filter className="w-4 h-4" />
                    <span>Filter</span>
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {contextBuilds.map(build => (
                  <button
                    key={build.id}
                    onClick={() => setSelectedBuild(build.id)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      selectedBuild === build.id
                        ? 'border-blue-500 bg-blue-900/20'
                        : 'border-gray-600 hover:border-gray-500'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{build.name}</h4>
                      {build.winStreak > 10 && <Flame className="w-4 h-4 text-orange-400" />}
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{build.version}</p>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">Success</span>
                        <span className="text-sm text-green-400">{build.successRate}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">Efficiency</span>
                        <span className="text-sm text-blue-400">{build.tokenEfficiency}</span>
                      </div>
                      {uncertaintyView && (
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">Uncertainty</span>
                          <span className="text-sm text-purple-400">{build.uncertaintyScore.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                    <div className={`mt-2 px-2 py-1 rounded text-xs text-center ${getLevelColor(build.level)}`}>
                      {build.level}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'optimization' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Optimization Controls */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Optimization Lab</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Select Build for Optimization
                  </label>
                  <select 
                    value={selectedBuild} 
                    onChange={(e) => setSelectedBuild(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                  >
                    {contextBuilds.map(build => (
                      <option key={build.id} value={build.id}>
                        {build.name} {build.version}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Optimization Strategy
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="radio" name="strategy" value="ablation" className="mr-2" defaultChecked />
                      <span className="text-sm">Ablation Testing</span>
                    </label>
                    <label className="flex items-center">
                      <input type="radio" name="strategy" value="genetic" className="mr-2" />
                      <span className="text-sm">Genetic Algorithm</span>
                    </label>
                    <label className="flex items-center">
                      <input type="radio" name="strategy" value="gradient" className="mr-2" />
                      <span className="text-sm">Gradient Descent</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Target Metric
                  </label>
                  <select className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white">
                    <option>Success Rate</option>
                    <option>Token Efficiency</option>
                    <option>Time to Green</option>
                    <option>Overall Score</option>
                  </select>
                </div>

                <button 
                  onClick={startOptimization}
                  disabled={isOptimizing}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                >
                  {isOptimizing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Optimizing...</span>
                    </>
                  ) : (
                    <>
                      <Rocket className="w-4 h-4" />
                      <span>Start Optimization</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* A/B Testing */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">A/B Testing</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Select Builds to Compare ({selectedBuildsForComparison.length}/2)
                  </label>
                  <div className="space-y-2">
                    {contextBuilds.map(build => (
                      <label key={build.id} className="flex items-center">
                        <input 
                          type="checkbox" 
                          checked={selectedBuildsForComparison.includes(build.id)}
                          onChange={() => toggleBuildForComparison(build.id)}
                          className="mr-2" 
                        />
                        <span className="text-sm">{build.name} {build.version}</span>
                        <span className="ml-auto text-xs text-gray-400">{build.successRate}%</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Test Parameters
                  </label>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Sample Size</span>
                      <select className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-sm">
                        <option>50 tests</option>
                        <option>100 tests</option>
                        <option>200 tests</option>
                      </select>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Confidence Level</span>
                      <select className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-sm">
                        <option>95%</option>
                        <option>99%</option>
                      </select>
                    </div>
                  </div>
                </div>

                <button 
                  onClick={startABTest}
                  disabled={isAbTesting || selectedBuildsForComparison.length !== 2}
                  className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                >
                  {isAbTesting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Testing...</span>
                    </>
                  ) : (
                    <>
                      <TestTube className="w-4 h-4" />
                      <span>Start A/B Test</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Test Results */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Recent Test Results</h2>
              
              <div className="space-y-4">
                <div className="bg-gray-700 rounded p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">CRUD Specialist Optimization</span>
                    <span className="text-xs text-green-400">+3% improvement</span>
                  </div>
                  <p className="text-xs text-gray-400">2 hours ago • Ablation testing</p>
                  <div className="mt-2 w-full bg-gray-600 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '94%' }}></div>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">Success rate: 91% → 94%</p>
                </div>

                <div className="bg-gray-700 rounded p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">AuthGuard vs SecurityTank</span>
                    <span className="text-xs text-blue-400">AuthGuard wins</span>
                  </div>
                  <p className="text-xs text-gray-400">1 day ago • A/B test</p>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-gray-400">AuthGuard</p>
                      <div className="bg-gray-600 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '87%' }}></div>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">SecurityTank</p>
                      <div className="bg-gray-600 rounded-full h-2">
                        <div className="bg-gray-500 h-2 rounded-full" style={{ width: '83%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700 rounded p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">UI Wizard Token Optimization</span>
                    <span className="text-xs text-orange-400">+12% efficiency</span>
                  </div>
                  <p className="text-xs text-gray-400">3 days ago • Gradient descent</p>
                  <div className="mt-2 w-full bg-gray-600 rounded-full h-2">
                    <div className="bg-orange-500 h-2 rounded-full" style={{ width: '91%' }}></div>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">Token efficiency: 37.5 → 42.1</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'leaderboard' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Context Engineering Leaderboard</h2>
                <div className="flex items-center space-x-2">
                  <select className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm">
                    <option>This Week</option>
                    <option>This Month</option>
                    <option>All Time</option>
                  </select>
                  <select className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm">
                    <option>Success Rate</option>
                    <option>Token Efficiency</option>
                    <option>Total XP</option>
                  </select>
                </div>
              </div>
              
              <div className="space-y-3">
                {leaderboard.map((player, index) => (
                  <div 
                    key={player.rank} 
                    className={`p-4 rounded-lg flex items-center justify-between ${
                      player.name === 'You' ? 'bg-blue-900/30 border border-blue-500' : 'bg-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {getBadgeIcon(player.rank)}
                        <span className="text-lg font-bold">#{player.rank}</span>
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium">{player.name}</h3>
                          {player.name === 'You' && <span className="text-xs bg-blue-600 px-2 py-1 rounded">YOU</span>}
                          {player.streak > 10 && <Flame className="w-4 h-4 text-orange-400" />}
                        </div>
                        <p className="text-sm text-gray-400">Level {player.level} • {player.badge}</p>
                        <p className="text-xs text-gray-500">{player.totalXP} total XP • +{player.weeklyXP} this week</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-green-400">{player.successRate}%</p>
                      <p className="text-sm text-gray-400">{player.streak} day streak</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Team Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Team Performance</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Average Success Rate</span>
                    <span className="text-green-400 font-semibold">91.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Optimizations</span>
                    <span className="text-blue-400 font-semibold">1,247</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Active Builds</span>
                    <span className="text-purple-400 font-semibold">23</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Weekly Progress</h3>
                <ResponsiveContainer width="100%" height={120}>
                  <AreaChart data={performanceHistory.slice(-7)}>
                    <Area type="monotone" dataKey="xpGained" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                    <XAxis dataKey="day" hide />
                    <YAxis hide />
                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Achievements</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Unlocked</span>
                    <span className="text-yellow-400 font-semibold">{achievements.filter(a => a.unlocked).length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total</span>
                    <span className="text-gray-400 font-semibold">{achievements.length}</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2 mt-2">
                    <div 
                      className="bg-yellow-500 h-2 rounded-full" 
                      style={{ width: `${(achievements.filter(a => a.unlocked).length / achievements.length) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'achievements' && (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-bold mb-2">Achievements</h2>
              <p className="text-gray-400">
                Unlock achievements by improving your context engineering skills. Each achievement grants XP and showcases your expertise.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {achievements.map(achievement => (
                <div 
                  key={achievement.id} 
                  className={`bg-gray-800 rounded-lg p-6 border transition-all hover:border-gray-500 ${
                    achievement.unlocked 
                      ? 'border-gray-600' 
                      : 'border-gray-700 opacity-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <achievement.icon className={`w-8 h-8 ${
                      achievement.unlocked
                        ? getRarityColor(achievement.rarity)
                        : 'text-gray-600'
                    }`} />
                    <div className="text-right">
                      <span className={`text-xs px-2 py-1 rounded ${
                        achievement.rarity === 'legendary' 
                          ? 'bg-purple-900/30 text-purple-400'
                          : achievement.rarity === 'epic'
                          ? 'bg-orange-900/30 text-orange-400'
                          : achievement.rarity === 'gold'
                          ? 'bg-yellow-900/30 text-yellow-400'
                          : 'bg-gray-700 text-gray-300'
                      }`}>
                        {achievement.rarity}
                      </span>
                    </div>
                  </div>
                  
                  <h3 className="font-semibold mb-2">{achievement.name}</h3>
                  <p className="text-sm text-gray-400 mb-4">{achievement.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-blue-400">+{achievement.xp} XP</span>
                    {achievement.unlocked ? (
                      <div className="flex items-center space-x-1 text-green-400 text-sm">
                        <CheckCircle className="w-4 h-4" />
                        <span>Unlocked</span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-500">Locked</span>
                    )}
                  </div>
                  
                  {achievement.unlocked && achievement.date && (
                    <p className="text-xs text-gray-500 mt-2">Unlocked on {achievement.date}</p>
                  )}
                </div>
              ))}
            </div>

            {/* Achievement Progress */}
            <div className="mt-8 bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Achievement Progress</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-400">
                    {achievements.filter(a => a.unlocked).length}
                  </div>
                  <div className="text-sm text-gray-400">Unlocked</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-400">
                    {achievements.filter(a => a.unlocked && a.rarity === 'legendary').length}
                  </div>
                  <div className="text-sm text-gray-400">Legendary</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">
                    {achievements.filter(a => a.unlocked).reduce((sum, a) => sum + a.xp, 0)}
                  </div>
                  <div className="text-sm text-gray-400">Total XP</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">
                    {Math.round((achievements.filter(a => a.unlocked).length / achievements.length) * 100)}%
                  </div>
                  <div className="text-sm text-gray-400">Complete</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Performance Trends */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Performance Analytics</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-300 mb-3">Success Rate Trends</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={performanceHistory}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="day" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                        labelStyle={{ color: '#F3F4F6' }}
                      />
                      <Line type="monotone" dataKey="successRate" stroke="#10B981" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-300 mb-3">Token Efficiency</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={performanceHistory}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="day" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                        labelStyle={{ color: '#F3F4F6' }}
                      />
                      <Line type="monotone" dataKey="tokenEfficiency" stroke="#3B82F6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Build Performance Comparison */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Build Performance Comparison</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={contextBuilds}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                    labelStyle={{ color: '#F3F4F6' }}
                  />
                  <Bar dataKey="successRate" fill="#10B981" />
                  <Bar dataKey="tokenEfficiency" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Detailed Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Optimization Impact</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Total Optimizations</span>
                    <span className="text-2xl font-bold text-blue-400">47</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Average Improvement</span>
                    <span className="text-2xl font-bold text-green-400">+4.2%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Best Single Improvement</span>
                    <span className="text-2xl font-bold text-purple-400">+12%</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Usage Statistics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Tests Run</span>
                    <span className="text-2xl font-bold text-blue-400">2,341</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Success Rate</span>
                    <span className="text-2xl font-bold text-green-400">94.1%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Average Time</span>
                    <span className="text-2xl font-bold text-purple-400">1.8m</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Token Efficiency</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Current Efficiency</span>
                    <span className="text-2xl font-bold text-blue-400">47.2</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Best Efficiency</span>
                    <span className="text-2xl font-bold text-green-400">52.1</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Improvement</span>
                    <span className="text-2xl font-bold text-purple-400">+23%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default SelfImprovingRAGPlatform;