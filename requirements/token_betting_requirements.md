# Token Betting Module: Requirements & Technical Plan

## 📋 **Module Overview**

**Module Name**: Token Betting  
**Size Estimate**: ~22k tokens  
**Priority**: 1 (Foundation)  
**TDD Cycles**: 3  
**Branch**: `module/token-betting`  
**Cursor Window**: #4  
**Dependencies**: Orchestrator Module, User Management Module  

### **Purpose**
The Token Betting Module implements the gamified betting system where users can wager tokens on optimization outcomes. It manages token economies, calculates odds, handles bet resolution, and provides the core engagement mechanics that drive user participation in the platform.

---

## 🎯 **Functional Requirements**

### **FR-1: Token Wallet Management** (TDD Cycle 3)
- **FR-1.1**: Create token wallets for new users with initial balance
- **FR-1.2**: Track token balance and transaction history per user
- **FR-1.3**: Support token deposits and withdrawals (virtual economy)
- **FR-1.4**: Handle token transfers between users (future feature)
- **FR-1.5**: Implement daily/weekly token allowances for engagement
- **FR-1.6**: Support premium token purchases for monetization
- **FR-1.7**: Maintain audit trail for all token transactions

### **FR-2: Betting System** (TDD Cycle 3)
- **FR-2.1**: Allow users to place bets on optimization outcomes
- **FR-2.2**: Support different bet types (success/failure, improvement percentage)
- **FR-2.3**: Calculate dynamic odds based on historical data and market activity
- **FR-2.4**: Enforce minimum and maximum bet amounts
- **FR-2.5**: Handle bet cancellation before optimization starts
- **FR-2.6**: Support multiple bets per user on different optimizations
- **FR-2.7**: Implement bet pooling for popular optimizations

### **FR-3: Odds Calculation Engine**
- **FR-3.1**: Calculate real-time odds based on optimization success rates
- **FR-3.2**: Factor in user skill level and historical performance
- **FR-3.3**: Adjust odds based on current betting volume and distribution
- **FR-3.4**: Support different odds formats (decimal, fractional, American)
- **FR-3.5**: Implement house edge for platform sustainability
- **FR-3.6**: Provide odds history and trend analysis

### **FR-4: Bet Resolution & Payouts**
- **FR-4.1**: Automatically resolve bets when optimization completes
- **FR-4.2**: Calculate payouts based on final odds and bet amounts
- **FR-4.3**: Handle partial payouts for threshold-based bets
- **FR-4.4**: Process winnings to user wallets instantly
- **FR-4.5**: Support dispute resolution for edge cases
- **FR-4.6**: Generate payout notifications and summaries

### **FR-5: Market Making & Liquidity**
- **FR-5.1**: Provide liquidity through automated market making
- **FR-5.2**: Manage platform risk exposure across all active bets
- **FR-5.3**: Implement circuit breakers for unusual betting patterns
- **FR-5.4**: Support bet matching between users (peer-to-peer)
- **FR-5.5**: Handle market suspension for problematic optimizations
- **FR-5.6**: Maintain fair and balanced markets

### **FR-6: Betting Analytics & Insights**
- **FR-6.1**: Track user betting patterns and preferences
- **FR-6.2**: Provide performance analytics for betting strategies
- **FR-6.3**: Generate profitability reports per user
- **FR-6.4**: Identify and flag potential problem gambling
- **FR-6.5**: Support betting strategy recommendations
- **FR-6.6**: Maintain historical betting market data

---

## 🔧 **Non-Functional Requirements**

### **NFR-1: Performance**
- **NFR-1.1**: Bet placement processing < 100ms for 95% of requests
- **NFR-1.2**: Odds calculation updates in real-time (< 500ms)
- **NFR-1.3**: Support 1,000+ concurrent betting operations
- **NFR-1.4**: Payout processing < 200ms after bet resolution
- **NFR-1.5**: Wallet balance updates with strong consistency

### **NFR-2: Security & Compliance**
- **NFR-2.1**: Tamper-proof bet records with cryptographic signatures
- **NFR-2.2**: Fair odds calculation without manipulation
- **NFR-2.3**: Secure token transfer mechanisms
- **NFR-2.4**: Compliance with gambling regulations where applicable
- **NFR-2.5**: Prevention of insider trading and advantage play

### **NFR-3: Reliability**
- **NFR-3.1**: 99.9% uptime for betting services
- **NFR-3.2**: Atomic transactions for bet placement and resolution
- **NFR-3.3**: Guaranteed bet resolution within 24 hours
- **NFR-3.4**: Backup and recovery for all betting data
- **NFR-3.5**: Graceful handling of optimization failures

### **NFR-4: Scalability**
- **NFR-4.1**: Support millions of active bets simultaneously
- **NFR-4.2**: Handle spike traffic during popular optimizations
- **NFR-4.3**: Efficient storage and retrieval of betting history
- **NFR-4.4**: Horizontal scaling for bet processing
- **NFR-4.5**: Real-time odds updates across all instances

### **NFR-5: Fairness & Transparency**
- **NFR-5.1**: Publicly auditable betting records
- **NFR-5.2**: Transparent odds calculation methodology
- **NFR-5.3**: Equal access to betting opportunities
- **NFR-5.4**: No preferential treatment for any users
- **NFR-5.5**: Clear terms and conditions for all bets

---

## 🏗️ **Technical Architecture**

### **Architecture Pattern**: Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   Betting   │ │   Wallet    │ │    Odds     │       │
│  │ Controller  │ │ Controller  │ │ Controller  │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│              Application Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   Betting   │ │   Wallet    │ │    Odds     │       │
│  │  Service    │ │  Service    │ │Calculation  │       │
│  │             │ │             │ │  Service    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                Domain Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Token Bet   │ │   Token     │ │  Betting    │       │
│  │ Aggregate   │ │   Wallet    │ │   Market    │       │
│  │             │ │             │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│            Infrastructure Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ PostgreSQL  │ │    Redis    │ │  Payment    │       │
│  │ Repository  │ │    Cache    │ │  Gateway    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### **Core Components**

#### **1. Domain Layer**

```typescript
// Token Bet Aggregate Root
export class TokenBet {
    constructor(
        public readonly id: BetId,
        public readonly userId: UserId,
        public readonly buildId: BuildId,
        public readonly betType: BetType,
        public readonly tokenAmount: TokenAmount,
        private prediction: OptimizationPrediction,
        private odds: BettingOdds,
        private status: BetStatus,
        private placedAt: Date,
        private resolvedAt?: Date,
        private payout?: TokenAmount
    ) {}

    static create(
        userId: UserId,
        buildId: BuildId,
        betType: BetType,
        tokenAmount: TokenAmount,
        prediction: OptimizationPrediction,
        odds: BettingOdds
    ): TokenBet {
        return new TokenBet(
            BetId.generate(),
            userId,
            buildId,
            betType,
            tokenAmount,
            prediction,
            odds,
            BetStatus.PENDING,
            new Date()
        );
    }

    cancel(): void {
        if (this.status !== BetStatus.PENDING) {
            throw new BetCannotBeCancelledError(this.id, this.status);
        }
        this.status = BetStatus.CANCELLED;
    }

    resolve(actualResult: OptimizationResult): BetResult {
        if (this.status !== BetStatus.PENDING) {
            throw new BetAlreadyResolvedError(this.id);
        }

        const isWinning = this.prediction.matches(actualResult);
        const payout = isWinning 
            ? this.calculatePayout() 
            : TokenAmount.zero();

        this.status = isWinning ? BetStatus.WON : BetStatus.LOST;
        this.payout = payout;
        this.resolvedAt = new Date();

        return new BetResult(
            this.id,
            isWinning,
            payout,
            this.odds,
            actualResult
        );
    }

    private calculatePayout(): TokenAmount {
        const baseAmount = this.tokenAmount.value;
        const oddsMultiplier = this.odds.getDecimalOdds();
        const payoutValue = Math.floor(baseAmount * oddsMultiplier);
        
        return new TokenAmount(payoutValue);
    }

    isActive(): boolean {
        return this.status === BetStatus.PENDING;
    }

    hasExpired(): boolean {
        const expiryTime = new Date(this.placedAt.getTime() + 24 * 60 * 60 * 1000); // 24 hours
        return new Date() > expiryTime && this.status === BetStatus.PENDING;
    }
}

// Token Wallet Aggregate Root
export class TokenWallet {
    constructor(
        public readonly userId: UserId,
        private balance: TokenBalance,
        private transactions: TokenTransaction[] = [],
        private dailyAllowance: DailyAllowance = DailyAllowance.default(),
        private createdAt: Date = new Date()
    ) {}

    static createForUser(userId: UserId, initialBalance: TokenAmount = TokenAmount.fromValue(1000)): TokenWallet {
        return new TokenWallet(
            userId,
            new TokenBalance(initialBalance),
            [new TokenTransaction(
                TransactionId.generate(),
                TransactionType.INITIAL_GRANT,
                initialBalance,
                'Initial wallet creation',
                new Date()
            )],
            DailyAllowance.default(),
            new Date()
        );
    }

    deduct(amount: TokenAmount, reason: string): DeductionResult {
        if (!this.balance.canDeduct(amount)) {
            return DeductionResult.insufficientFunds(this.balance.available);
        }

        const transaction = new TokenTransaction(
            TransactionId.generate(),
            TransactionType.DEBIT,
            amount,
            reason,
            new Date()
        );

        this.balance = this.balance.deduct(amount);
        this.transactions.push(transaction);

        return DeductionResult.success(transaction);
    }

    credit(amount: TokenAmount, reason: string): void {
        const transaction = new TokenTransaction(
            TransactionId.generate(),
            TransactionType.CREDIT,
            amount,
            reason,
            new Date()
        );

        this.balance = this.balance.credit(amount);
        this.transactions.push(transaction);
    }

    claimDailyAllowance(): ClaimResult {
        if (!this.dailyAllowance.canClaim()) {
            return ClaimResult.alreadyClaimed(this.dailyAllowance.getNextClaimTime());
        }

        const allowanceAmount = this.dailyAllowance.getAmount();
        this.credit(allowanceAmount, 'Daily allowance');
        this.dailyAllowance = this.dailyAllowance.markClaimed();

        return ClaimResult.success(allowanceAmount);
    }

    getAvailableBalance(): TokenAmount {
        return this.balance.available;
    }

    getTransactionHistory(limit: number = 50): TokenTransaction[] {
        return this.transactions
            .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
            .slice(0, limit);
    }

    calculateProfitLoss(timeframe: Timeframe): ProfitLossAnalysis {
        const startDate = timeframe.getStartDate();
        const relevantTransactions = this.transactions.filter(
            tx => tx.timestamp >= startDate
        );

        const credits = relevantTransactions
            .filter(tx => tx.type === TransactionType.CREDIT)
            .reduce((sum, tx) => sum + tx.amount.value, 0);

        const debits = relevantTransactions
            .filter(tx => tx.type === TransactionType.DEBIT)
            .reduce((sum, tx) => sum + tx.amount.value, 0);

        const netChange = credits - debits;
        const transactionCount = relevantTransactions.length;

        return new ProfitLossAnalysis(
            new TokenAmount(credits),
            new TokenAmount(debits),
            new TokenAmount(Math.abs(netChange)),
            netChange >= 0,
            transactionCount,
            timeframe
        );
    }
}

// Betting Market
export class BettingMarket {
    constructor(
        public readonly buildId: BuildId,
        private odds: MarketOdds,
        private volume: BettingVolume,
        private bets: TokenBet[] = [],
        private status: MarketStatus = MarketStatus.OPEN,
        private createdAt: Date = new Date()
    ) {}

    placeBet(bet: TokenBet): MarketUpdate {
        if (this.status !== MarketStatus.OPEN) {
            throw new MarketClosedError(this.buildId);
        }

        this.bets.push(bet);
        this.volume = this.volume.addBet(bet.tokenAmount);
        
        // Update odds based on new betting activity
        const oldOdds = this.odds;
        this.odds = this.recalculateOdds();

        return new MarketUpdate(
            this.buildId,
            oldOdds,
            this.odds,
            this.volume,
            bet
        );
    }

    closeMarket(): void {
        this.status = MarketStatus.CLOSED;
    }

    resolveMarket(result: OptimizationResult): MarketResolution {
        if (this.status !== MarketStatus.CLOSED) {
            throw new MarketNotClosedError(this.buildId);
        }

        const resolutions = this.bets.map(bet => bet.resolve(result));
        const totalPayout = resolutions
            .filter(res => res.isWinning)
            .reduce((sum, res) => sum + res.payout.value, 0);

        this.status = MarketStatus.RESOLVED;

        return new MarketResolution(
            this.buildId,
            result,
            resolutions,
            new TokenAmount(totalPayout),
            this.calculateHouseEdge()
        );
    }

    private recalculateOdds(): MarketOdds {
        // Simple odds calculation based on betting volume distribution
        const successBets = this.bets.filter(bet => 
            bet.prediction.type === PredictionType.SUCCESS
        );
        const failureBets = this.bets.filter(bet => 
            bet.prediction.type === PredictionType.FAILURE
        );

        const successVolume = successBets.reduce((sum, bet) => sum + bet.tokenAmount.value, 0);
        const failureVolume = failureBets.reduce((sum, bet) => sum + bet.tokenAmount.value, 0);
        const totalVolume = successVolume + failureVolume;

        if (totalVolume === 0) {
            return MarketOdds.default(); // 50/50 odds
        }

        // Calculate implied probabilities and add house edge
        const successProbability = (failureVolume / totalVolume) * 0.95; // 5% house edge
        const failureProbability = (successVolume / totalVolume) * 0.95;

        return new MarketOdds(
            successProbability > 0 ? 1 / successProbability : 1.05,
            failureProbability > 0 ? 1 / failureProbability : 1.05
        );
    }

    private calculateHouseEdge(): number {
        const totalStaked = this.bets.reduce((sum, bet) => sum + bet.tokenAmount.value, 0);
        const totalPayout = this.bets
            .filter(bet => bet.status === BetStatus.WON)
            .reduce((sum, bet) => sum + (bet.payout?.value || 0), 0);

        return totalStaked > 0 ? (totalStaked - totalPayout) / totalStaked : 0;
    }
}

// Value Objects
export class BettingOdds {
    constructor(private readonly decimalOdds: number) {
        if (decimalOdds < 1.01) {
            throw new InvalidOddsError(decimalOdds);
        }
    }

    getDecimalOdds(): number {
        return this.decimalOdds;
    }

    getFractionalOdds(): string {
        const decimal = this.decimalOdds - 1;
        const gcd = this.greatestCommonDivisor(Math.round(decimal * 100), 100);
        const numerator = Math.round(decimal * 100) / gcd;
        const denominator = 100 / gcd;
        return `${numerator}/${denominator}`;
    }

    getAmericanOdds(): number {
        if (this.decimalOdds >= 2.0) {
            return Math.round((this.decimalOdds - 1) * 100);
        } else {
            return Math.round(-100 / (this.decimalOdds - 1));
        }
    }

    getImpliedProbability(): number {
        return 1 / this.decimalOdds;
    }

    private greatestCommonDivisor(a: number, b: number): number {
        return b === 0 ? a : this.greatestCommonDivisor(b, a % b);
    }
}

export class OptimizationPrediction {
    constructor(
        public readonly type: PredictionType,
        public readonly threshold?: number,
        public readonly confidence?: number
    ) {}

    matches(result: OptimizationResult): boolean {
        switch (this.type) {
            case PredictionType.SUCCESS:
                return result.improvement > 0;
            case PredictionType.FAILURE:
                return result.improvement <= 0;
            case PredictionType.IMPROVEMENT_THRESHOLD:
                return this.threshold !== undefined && result.improvement >= this.threshold;
            case PredictionType.EXACT_RANGE:
                return this.threshold !== undefined && 
                       Math.abs(result.improvement - this.threshold) <= 0.01;
            default:
                return false;
        }
    }
}
```

#### **2. Application Layer**

```typescript
// Token Betting Service
@Injectable()
export class TokenBettingService {
    constructor(
        private readonly betRepository: IBetRepository,
        private readonly walletService: IWalletService,
        private readonly oddsService: IOddsCalculationService,
        private readonly eventBus: IEventBus
    ) {}

    async placeBet(command: PlaceBetCommand): Promise<TokenBet> {
        // Validate user has sufficient balance
        const wallet = await this.walletService.getWallet(command.userId);
        const deductionResult = wallet.deduct(command.tokenAmount, 'Bet placement');
        
        if (!deductionResult.isSuccess()) {
            throw new InsufficientFundsError(wallet.getAvailableBalance(), command.tokenAmount);
        }

        // Get current odds
        const odds = await this.oddsService.calculateOdds(
            command.buildId,
            command.prediction
        );

        // Create bet
        const bet = TokenBet.create(
            command.userId,
            command.buildId,
            command.betType,
            command.tokenAmount,
            command.prediction,
            odds
        );

        // Save bet and update wallet
        await this.betRepository.save(bet);
        await this.walletService.saveWallet(wallet);

        // Update market odds
        await this.oddsService.updateMarketAfterBet(command.buildId, bet);

        // Publish event
        await this.eventBus.publish(new BetPlacedEvent(
            bet.id,
            command.userId,
            command.buildId,
            command.tokenAmount,
            odds
        ));

        return bet;
    }

    async resolveBet(command: ResolveBetCommand): Promise<BetResult> {
        const bet = await this.betRepository.findById(command.betId);
        if (!bet) {
            throw new BetNotFoundError(command.betId);
        }

        const result = bet.resolve(command.optimizationResult);
        
        // Process payout if bet won
        if (result.isWinning) {
            const wallet = await this.walletService.getWallet(bet.userId);
            wallet.credit(result.payout, `Bet win: ${bet.id.value}`);
            await this.walletService.saveWallet(wallet);
        }

        await this.betRepository.save(bet);

        // Publish event
        await this.eventBus.publish(new BetResolvedEvent(
            bet.id,
            bet.userId,
            result.isWinning,
            result.payout
        ));

        return result;
    }

    async cancelBet(command: CancelBetCommand): Promise<void> {
        const bet = await this.betRepository.findById(command.betId);
        if (!bet) {
            throw new BetNotFoundError(command.betId);
        }

        if (bet.userId.value !== command.userId.value) {
            throw new UnauthorizedBetCancellationError(command.betId, command.userId);
        }

        bet.cancel();

        // Refund tokens to wallet
        const wallet = await this.walletService.getWallet(command.userId);
        wallet.credit(bet.tokenAmount, `Bet cancellation: ${bet.id.value}`);
        
        await this.betRepository.save(bet);
        await this.walletService.saveWallet(wallet);

        await this.eventBus.publish(new BetCancelledEvent(
            bet.id,
            command.userId,
            bet.tokenAmount
        ));
    }

    async getUserBets(userId: UserId, limit: number = 50): Promise<TokenBet[]> {
        return this.betRepository.findByUserId(userId, limit);
    }

    async getBetsByBuild(buildId: BuildId): Promise<TokenBet[]> {
        return this.betRepository.findByBuildId(buildId);
    }

    async getBettingStats(userId: UserId): Promise<BettingStatsDto> {
        const bets = await this.betRepository.findByUserId(userId, 1000);
        const wallet = await this.walletService.getWallet(userId);

        const totalBets = bets.length;
        const wonBets = bets.filter(bet => bet.status === BetStatus.WON).length;
        const lostBets = bets.filter(bet => bet.status === BetStatus.LOST).length;
        const winRate = totalBets > 0 ? wonBets / totalBets : 0;

        const totalStaked = bets.reduce((sum, bet) => sum + bet.tokenAmount.value, 0);
        const totalReturns = bets
            .filter(bet => bet.status === BetStatus.WON)
            .reduce((sum, bet) => sum + (bet.payout?.value || 0), 0);
        const netProfit = totalReturns - totalStaked;

        return new BettingStatsDto(
            totalBets,
            wonBets,
            lostBets,
            winRate,
            new TokenAmount(totalStaked),
            new TokenAmount(totalReturns),
            new TokenAmount(Math.abs(netProfit)),
            netProfit >= 0,
            wallet.getAvailableBalance()
        );
    }
}

// Wallet Service
@Injectable()
export class WalletService {
    constructor(
        private readonly walletRepository: IWalletRepository,
        private readonly eventBus: IEventBus
    ) {}

    async createWallet(userId: UserId, initialBalance?: TokenAmount): Promise<TokenWallet> {
        const existingWallet = await this.walletRepository.findByUserId(userId);
        if (existingWallet) {
            throw new WalletAlreadyExistsError(userId);
        }

        const wallet = TokenWallet.createForUser(userId, initialBalance);
        await this.walletRepository.save(wallet);

        await this.eventBus.publish(new WalletCreatedEvent(
            userId,
            wallet.getAvailableBalance()
        ));

        return wallet;
    }

    async getWallet(userId: UserId): Promise<TokenWallet> {
        const wallet = await this.walletRepository.findByUserId(userId);
        if (!wallet) {
            // Auto-create wallet if it doesn't exist
            return this.createWallet(userId);
        }
        return wallet;
    }

    async claimDailyAllowance(userId: UserId): Promise<ClaimResult> {
        const wallet = await this.getWallet(userId);
        const result = wallet.claimDailyAllowance();
        
        if (result.isSuccess()) {
            await this.walletRepository.save(wallet);
            await this.eventBus.publish(new DailyAllowanceClaimedEvent(
                userId,
                result.amount
            ));
        }

        return result;
    }

    async transferTokens(command: TransferTokensCommand): Promise<void> {
        const fromWallet = await this.getWallet(command.fromUserId);
        const toWallet = await this.getWallet(command.toUserId);

        const deductionResult = fromWallet.deduct(
            command.amount,
            `Transfer to ${command.toUserId.value}`
        );

        if (!deductionResult.isSuccess()) {
            throw new InsufficientFundsError(
                fromWallet.getAvailableBalance(),
                command.amount
            );
        }

        toWallet.credit(
            command.amount,
            `Transfer from ${command.fromUserId.value}`
        );

        await this.walletRepository.save(fromWallet);
        await this.walletRepository.save(toWallet);

        await this.eventBus.publish(new TokensTransferredEvent(
            command.fromUserId,
            command.toUserId,
            command.amount
        ));
    }
}

// Odds Calculation Service
@Injectable()
export class OddsCalculationService {
    constructor(
        private readonly betRepository: IBetRepository,
        private readonly optimizationHistoryService: IOptimizationHistoryService,
        private readonly marketDataCache: IMarketDataCache
    ) {}

    async calculateOdds(buildId: BuildId, prediction: OptimizationPrediction): Promise<BettingOdds> {
        // Get historical success rate for this type of optimization
        const historicalRate = await this.optimizationHistoryService
            .getSuccessRate(buildId, prediction.type);

        // Get current market sentiment
        const currentBets = await this.betRepository.findByBuildId(buildId);
        const marketSentiment = this.calculateMarketSentiment(currentBets, prediction);

        // Combine historical data with market sentiment
        const adjustedProbability = this.blendProbabilities(
            historicalRate,
            marketSentiment,
            0.7 // 70% weight on historical, 30% on market
        );

        // Apply house edge and return odds
        const fairOdds = 1 / adjustedProbability;
        const oddsWithEdge = fairOdds * 1.05; // 5% house edge

        return new BettingOdds(Math.max(oddsWithEdge, 1.01)); // Minimum odds of 1.01
    }

    async updateMarketAfterBet(buildId: BuildId, newBet: TokenBet): Promise<void> {
        // Invalidate cached odds for this market
        await this.marketDataCache.invalidate(buildId);
        
        // Recalculate and cache new odds
        const newOdds = await this.calculateOdds(buildId, newBet.prediction);
        await this.marketDataCache.set(buildId, newOdds, 300); // Cache for 5 minutes
    }

    private calculateMarketSentiment(bets: TokenBet[], prediction: OptimizationPrediction): number {
        const relevantBets = bets.filter(bet => 
            bet.prediction.type === prediction.type && bet.isActive()
        );

        if (relevantBets.length === 0) {
            return 0.5; // Neutral sentiment
        }

        const totalVolume = relevantBets.reduce((sum, bet) => sum + bet.tokenAmount.value, 0);
        const weightedSentiment = relevantBets.reduce((sum, bet) => {
            const weight = bet.tokenAmount.value / totalVolume;
            return sum + (weight * 1); // Assuming positive sentiment for all bets
        }, 0);

        return Math.min(Math.max(weightedSentiment, 0.1), 0.9); // Clamp between 10% and 90%
    }

    private blendProbabilities(historical: number, market: number, historicalWeight: number): number {
        return (historical * historicalWeight) + (market * (1 - historicalWeight));
    }
}
```

---

## 📊 **Database Schema**

### **PostgreSQL Tables**

```sql
-- Token Wallets
CREATE TABLE token_wallets (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 1000,
    total_earned INTEGER NOT NULL DEFAULT 0,
    total_spent INTEGER NOT NULL DEFAULT 0,
    daily_allowance_amount INTEGER NOT NULL DEFAULT 50,
    last_allowance_claim DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_token_wallets_balance ON token_wallets(balance DESC);

-- Token Transactions
CREATE TABLE token_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_type transaction_type NOT NULL,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT NOT NULL,
    reference_id UUID, -- bet_id, transfer_id, etc.
    reference_type VARCHAR(50), -- 'bet', 'transfer', 'allowance', etc.
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE transaction_type AS ENUM ('credit', 'debit', 'initial_grant', 'daily_allowance', 'bet_payout', 'bet_stake', 'transfer_in', 'transfer_out');

CREATE INDEX idx_token_transactions_user_id ON token_transactions(user_id);
CREATE INDEX idx_token_transactions_type ON token_transactions(transaction_type);
CREATE INDEX idx_token_transactions_created_at ON token_transactions(created_at DESC);
CREATE INDEX idx_token_transactions_reference ON token_transactions(reference_type, reference_id);

-- Token Bets
CREATE TABLE token_bets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    build_id UUID NOT NULL, -- References context_builds from core-rag module
    bet_type bet_type NOT NULL,
    token_amount INTEGER NOT NULL,
    prediction JSONB NOT NULL,
    odds_decimal DECIMAL(6,2) NOT NULL,
    odds_fractional VARCHAR(20),
    odds_american INTEGER,
    status bet_status NOT NULL DEFAULT 'pending',
    payout INTEGER,
    placed_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours')
);

CREATE TYPE bet_type AS ENUM ('success_failure', 'improvement_threshold', 'exact_range', 'performance_comparison');
CREATE TYPE bet_status AS ENUM ('pending', 'won', 'lost', 'cancelled', 'expired');

CREATE INDEX idx_token_bets_user_id ON token_bets(user_id);
CREATE INDEX idx_token_bets_build_id ON token_bets(build_id);
CREATE INDEX idx_token_bets_status ON token_bets(status);
CREATE INDEX idx_token_bets_placed_at ON token_bets(placed_at DESC);
CREATE INDEX idx_token_bets_expires_at ON token_bets(expires_at) WHERE status = 'pending';

-- Betting Markets
CREATE TABLE betting_markets (
    build_id UUID PRIMARY KEY,
    market_status market_status NOT NULL DEFAULT 'open',
    total_volume INTEGER NOT NULL DEFAULT 0,
    total_bets INTEGER NOT NULL DEFAULT 0,
    success_odds_decimal DECIMAL(6,2) NOT NULL DEFAULT 2.00,
    failure_odds_decimal DECIMAL(6,2) NOT NULL DEFAULT 2.00,
    house_edge DECIMAL(4,3) NOT NULL DEFAULT 0.050,
    created_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TYPE market_status AS ENUM ('open', 'closed', 'resolved', 'suspended');

CREATE INDEX idx_betting_markets_status ON betting_markets(market_status);
CREATE INDEX idx_betting_markets_volume ON betting_markets(total_volume DESC);

-- Market Odds History
CREATE TABLE market_odds_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    build_id UUID REFERENCES betting_markets(build_id) ON DELETE CASCADE,
    success_odds DECIMAL(6,2) NOT NULL,
    failure_odds DECIMAL(6,2) NOT NULL,
    volume_at_time INTEGER NOT NULL,
    bets_count_at_time INTEGER NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_market_odds_history_build_id ON market_odds_history(build_id);
CREATE INDEX idx_market_odds_history_recorded_at ON market_odds_history(recorded_at DESC);

-- Betting Analytics
CREATE TABLE betting_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_bets INTEGER NOT NULL DEFAULT 0,
    total_staked INTEGER NOT NULL DEFAULT 0,
    total_won INTEGER NOT NULL DEFAULT 0,
    win_rate DECIMAL(4,3) NOT NULL DEFAULT 0,
    profit_loss INTEGER NOT NULL DEFAULT 0,
    largest_win INTEGER NOT NULL DEFAULT 0,
    largest_loss INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE INDEX idx_betting_analytics_user_id ON betting_analytics(user_id);
CREATE INDEX idx_betting_analytics_date ON betting_analytics(date DESC);
CREATE INDEX idx_betting_analytics_profit_loss ON betting_analytics(profit_loss DESC);

-- Risk Management
CREATE TABLE risk_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    alert_type risk_alert_type NOT NULL,
    severity alert_severity NOT NULL,
    description TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE TYPE risk_alert_type AS ENUM ('high_frequency_betting', 'large_stakes', 'consistent_losses', 'unusual_patterns');
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');

CREATE INDEX idx_risk_alerts_user_id ON risk_alerts(user_id);
CREATE INDEX idx_risk_alerts_type ON risk_alerts(alert_type);
CREATE INDEX idx_risk_alerts_severity ON risk_alerts(severity);
CREATE INDEX idx_risk_alerts_unresolved ON risk_alerts(is_resolved) WHERE is_resolved = false;
```

---

## 🔌 **API Specifications**

### **REST API Endpoints**

```yaml
# OpenAPI 3.0 Specification
openapi: 3.0.0
info:
  title: Token Betting Module API
  version: 1.0.0

paths:
  /wallet:
    get:
      summary: Get user's token wallet
      security:
        - bearerAuth: []
      responses:
        200:
          description: Wallet information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenWallet'

  /wallet/claim-allowance:
    post:
      summary: Claim daily token allowance
      security:
        - bearerAuth: []
      responses:
        200:
          description: Allowance claimed successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  amount:
                    type: integer
                  nextClaimTime:
                    type: string
                    format: date-time
        400:
          description: Allowance already claimed today

  /wallet/transactions:
    get:
      summary: Get transaction history
      security:
        - bearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 50
        - name: type
          in: query
          schema:
            type: string
            enum: [credit, debit, bet_payout, bet_stake]
      responses:
        200:
          description: Transaction history
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TokenTransaction'

  /bets:
    post:
      summary: Place a new bet
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                buildId:
                  type: string
                  format: uuid
                betType:
                  type: string
                  enum: [success_failure, improvement_threshold, exact_range]
                tokenAmount:
                  type: integer
                  minimum: 1
                  maximum: 10000
                prediction:
                  type: object
                  properties:
                    type:
                      type: string
                      enum: [success, failure, improvement_threshold]
                    threshold:
                      type: number
                      minimum: 0
                      maximum: 1
                  required: [type]
              required: [buildId, betType, tokenAmount, prediction]
      responses:
        201:
          description: Bet placed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenBet'
        400:
          description: Invalid bet parameters
        402:
          description: Insufficient funds

    get:
      summary: Get user's betting history
      security:
        - bearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 50
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, won, lost, cancelled]
      responses:
        200:
          description: Betting history
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TokenBet'

  /bets/{id}:
    get:
      summary: Get bet details
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
          description: Bet details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenBet'
        404:
          description: Bet not found

    delete:
      summary: Cancel a pending bet
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
        204:
          description: Bet cancelled successfully
        400:
          description: Bet cannot be cancelled
        404:
          description: Bet not found

  /bets/stats:
    get:
      summary: Get betting statistics
      security:
        - bearerAuth: []
      parameters:
        - name: timeframe
          in: query
          schema:
            type: string
            enum: [daily, weekly, monthly, all_time]
            default: all_time
      responses:
        200:
          description: Betting statistics
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BettingStats'

  /markets/{buildId}:
    get:
      summary: Get betting market information
      parameters:
        - name: buildId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Market information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BettingMarket'

  /markets/{buildId}/odds:
    get:
      summary: Get current odds for market
      parameters:
        - name: buildId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: predictionType
          in: query
          schema:
            type: string
            enum: [success, failure, improvement_threshold]
      responses:
        200:
          description: Current odds
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BettingOdds'

  /leaderboard/betting:
    get:
      summary: Get betting leaderboard
      parameters:
        - name: timeframe
          in: query
          schema:
            type: string
            enum: [daily, weekly, monthly, all_time]
            default: monthly
        - name: metric
          in: query
          schema:
            type: string
            enum: [profit, win_rate, total_volume]
            default: profit
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
      responses:
        200:
          description: Betting leaderboard
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/BettingLeaderboardEntry'

components:
  schemas:
    TokenWallet:
      type: object
      properties:
        userId:
          type: string
          format: uuid
        balance:
          type: integer
        totalEarned:
          type: integer
        totalSpent:
          type: integer
        dailyAllowanceAmount:
          type: integer
        lastAllowanceClaim:
          type: string
          format: date
        canClaimAllowance:
          type: boolean
        nextClaimTime:
          type: string
          format: date-time

    TokenBet:
      type: object
      properties:
        id:
          type: string
          format: uuid
        userId:
          type: string
          format: uuid
        buildId:
          type: string
          format: uuid
        betType:
          type: string
        tokenAmount:
          type: integer
        prediction:
          type: object
        odds:
          $ref: '#/components/schemas/BettingOdds'
        status:
          type: string
        payout:
          type: integer
        placedAt:
          type: string
          format: date-time
        resolvedAt:
          type: string
          format: date-time

    BettingOdds:
      type: object
      properties:
        decimal:
          type: number
        fractional:
          type: string
        american:
          type: integer
        impliedProbability:
          type: number

    BettingStats:
      type: object
      properties:
        totalBets:
          type: integer
        wonBets:
          type: integer
        lostBets:
          type: integer
        winRate:
          type: number
        totalStaked:
          type: integer
        totalReturns:
          type: integer
        netProfit:
          type: integer
        isProfit:
          type: boolean
        currentBalance:
          type: integer
```

---

## 🧪 **Testing Requirements**

### **Unit Tests** (TDD Cycle 3)

```typescript
// TDD Cycle 3: Token Betting System
describe('TokenBettingService', () => {
    let service: TokenBettingService;
    let mockBetRepository: jest.Mocked<IBetRepository>;
    let mockWalletService: jest.Mocked<IWalletService>;

    beforeEach(() => {
        mockBetRepository = createMockBetRepository();
        mockWalletService = createMockWalletService();
        service = new TokenBettingService(mockBetRepository, mockWalletService);
    });

    describe('placeBet', () => {
        it('should place bet when user has sufficient balance', async () => {
            // RED: Test fails initially
            const userId = UserId.generate();
            const buildId = BuildId.generate();
            const tokenAmount = new TokenAmount(100);
            
            const mockWallet = createMockWallet(userId, new TokenAmount(500));
            mockWalletService.getWallet.mockResolvedValue(mockWallet);

            const command = new PlaceBetCommand(
                userId,
                buildId,
                BetType.SUCCESS_FAILURE,
                tokenAmount,
                new OptimizationPrediction(PredictionType.SUCCESS)
            );

            const bet = await service.placeBet(command);

            expect(bet.userId).toBe(userId);
            expect(bet.buildId).toBe(buildId);
            expect(bet.tokenAmount).toBe(tokenAmount);
            expect(bet.status).toBe(BetStatus.PENDING);
            expect(mockBetRepository.save).toHaveBeenCalledWith(bet);
            expect(mockWalletService.saveWallet).toHaveBeenCalled();
        });

        it('should throw error when user has insufficient balance', async () => {
            // RED: Test fails initially
            const userId = UserId.generate();
            const tokenAmount = new TokenAmount(1000);
            
            const mockWallet = createMockWallet(userId, new TokenAmount(50)); // Insufficient
            mockWalletService.getWallet.mockResolvedValue(mockWallet);

            const command = new PlaceBetCommand(
                userId,
                BuildId.generate(),
                BetType.SUCCESS_FAILURE,
                tokenAmount,
                new OptimizationPrediction(PredictionType.SUCCESS)
            );

            await expect(service.placeBet(command))
                .rejects.toThrow(InsufficientFundsError);
        });
    });

    describe('resolveBet', () => {
        it('should payout winning bet correctly', async () => {
            // RED: Test fails initially
            const bet = createMockBet({
                status: BetStatus.PENDING,
                tokenAmount: new TokenAmount(100),
                odds: new BettingOdds(2.0)
            });
            
            mockBetRepository.findById.mockResolvedValue(bet);
            
            const optimizationResult = new OptimizationResult(0.15); // Success
            const command = new ResolveBetCommand(bet.id, optimizationResult);

            const result = await service.resolveBet(command);

            expect(result.isWinning).toBe(true);
            expect(result.payout.value).toBe(200); // 100 * 2.0 odds
            expect(bet.status).toBe(BetStatus.WON);
        });

        it('should handle losing bet correctly', async () => {
            // RED: Test fails initially
            const bet = createMockBet({
                status: BetStatus.PENDING,
                prediction: new OptimizationPrediction(PredictionType.SUCCESS)
            });
            
            mockBetRepository.findById.mockResolvedValue(bet);
            
            const optimizationResult = new OptimizationResult(-0.05); // Failure
            const command = new ResolveBetCommand(bet.id, optimizationResult);

            const result = await service.resolveBet(command);

            expect(result.isWinning).toBe(false);
            expect(result.payout.value).toBe(0);
            expect(bet.status).toBe(BetStatus.LOST);
        });
    });
});

describe('TokenWallet', () => {
    describe('deduct', () => {
        it('should deduct tokens when sufficient balance', () => {
            // RED: Test fails initially
            const wallet = TokenWallet.createForUser(
                UserId.generate(),
                new TokenAmount(1000)
            );

            const deductionResult = wallet.deduct(
                new TokenAmount(250),
                'Test bet'
            );

            expect(deductionResult.isSuccess()).toBe(true);
            expect(wallet.getAvailableBalance().value).toBe(750);
        });

        it('should fail deduction when insufficient balance', () => {
            // RED: Test fails initially
            const wallet = TokenWallet.createForUser(
                UserId.generate(),
                new TokenAmount(100)
            );

            const deductionResult = wallet.deduct(
                new TokenAmount(500),
                'Large bet'
            );

            expect(deductionResult.isSuccess()).toBe(false);
            expect(wallet.getAvailableBalance().value).toBe(100); // Unchanged
        });
    });

    describe('claimDailyAllowance', () => {
        it('should claim allowance successfully', () => {
            // RED: Test fails initially
            const wallet = TokenWallet.createForUser(UserId.generate());

            const claimResult = wallet.claimDailyAllowance();

            expect(claimResult.isSuccess()).toBe(true);
            expect(claimResult.amount.value).toBeGreaterThan(0);
            expect(wallet.getAvailableBalance().value).toBeGreaterThan(1000);
        });
    });
});

describe('BettingOdds', () => {
    describe('odds calculations', () => {
        it('should convert between odds formats correctly', () => {
            // RED: Test fails initially
            const odds = new BettingOdds(2.5);

            expect(odds.getDecimalOdds()).toBe(2.5);
            expect(odds.getFractionalOdds()).toBe('3/2');
            expect(odds.getAmericanOdds()).toBe(150);
            expect(odds.getImpliedProbability()).toBeCloseTo(0.4, 2);
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
DATABASE_URL=postgresql://user:password@postgres:5432/selfrag_betting
DATABASE_SSL=true
DATABASE_POOL_SIZE=20

# Token Economy
INITIAL_WALLET_BALANCE=1000
DAILY_ALLOWANCE_AMOUNT=50
MAXIMUM_BET_AMOUNT=10000
MINIMUM_BET_AMOUNT=1

# Betting Configuration
DEFAULT_HOUSE_EDGE=0.05
MINIMUM_ODDS=1.01
MAXIMUM_ODDS=100.0
BET_EXPIRY_HOURS=24

# Risk Management
HIGH_FREQUENCY_THRESHOLD=20
LARGE_STAKE_THRESHOLD=5000
LOSS_STREAK_ALERT=10

# Caching
REDIS_URL=redis://redis:6379
ODDS_CACHE_TTL=300
MARKET_DATA_CACHE_TTL=60

# External Services
PAYMENT_GATEWAY_URL=https://payments.api.com
COMPLIANCE_SERVICE_URL=https://compliance.api.com

# Monitoring
LOG_LEVEL=info
METRICS_PORT=9090
ALERT_WEBHOOK_URL=https://alerts.slack.com/webhook
```

---

## ✅ **Acceptance Criteria**

### **Functional Acceptance**
- [ ] Create token wallets with initial balance for new users
- [ ] Place bets with real-time odds calculation
- [ ] Process bet resolution with accurate payouts
- [ ] Handle daily token allowance claims
- [ ] Support bet cancellation for pending bets
- [ ] Maintain transaction history and audit trail

### **Performance Acceptance**
- [ ] Bet placement processing < 100ms for 95% of requests
- [ ] Real-time odds updates within 500ms
- [ ] Support 1,000+ concurrent betting operations
- [ ] Payout processing < 200ms after resolution

### **Security Acceptance**
- [ ] Tamper-proof bet records with cryptographic signatures
- [ ] Fair odds calculation without manipulation
- [ ] Secure token transfer mechanisms
- [ ] Compliance with applicable gambling regulations

This Token Betting Module provides the core gamification engine that drives user engagement through the virtual token economy and betting mechanics. 