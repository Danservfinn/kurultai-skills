# Parse Financial Database Schema

Reference for database models relevant to financial queries and reporting.

---

## Database Location

**Connection**: PostgreSQL on Railway
**ORM**: Prisma
**Schema File**: `/Users/kurultai/Eris/Parse/prisma/schema.prisma`

---

## Transaction Model

**Purpose**: Track all credit and financial transactions

```prisma
model Transaction {
  id           String            @id @default(cuid())
  userId       String
  amount       Int               // Amount in credits or dollars
  type         String            // Transaction type
  description  String?           // Human-readable description
  metadata     Json?             // { stripeEventId, stripeSessionId, ... }
  status       TransactionStatus @default(CONFIRMED)
  analysisId   String?           // For reservation tracking
  cancelReason String?
  createdAt    DateTime          @default(now())
  updatedAt    DateTime          @default(now()) @updatedAt
}
```

### Transaction Types

| Type | Description | Amount Unit |
|------|-------------|-------------|
| `CREDIT_PURCHASE` | Credit pack bought | Dollars |
| `SUBSCRIPTION_RENEWAL` | Subscription renewed | Dollars |
| `GRANT_CREDIT` | Credits granted (free tier, promo) | Credits |
| `CONSUME_CREDIT` | Analysis completed | Credits (negative) |
| `REFUND_CREDIT` | Credits refunded | Credits |
| `ADMIN_ADJUSTMENT` | Manual admin adjustment | Credits/Dollars |

### Transaction Status

| Status | Meaning |
|--------|---------|
| `PENDING` | Reserved for in-progress analysis |
| `CONFIRMED` | Completed/committed |
| `CANCELLED` | Failed/refunded |

### Key Metadata Fields

```json
{
  "stripeEventId": "evt_...",      // Stripe event ID for reconciliation
  "stripeSessionId": "cs_...",     // Checkout session ID
  "stripeCustomerId": "cus_...",   // Stripe customer
  "priceId": "price_...",          // Product purchased
  "packId": "pack_starter",        // Credit pack ID
  "tierId": "tier_pro"             // Subscription tier
}
```

### Useful Queries

**Revenue by period**:
```sql
SELECT DATE_TRUNC('month', createdAt) as month,
       type,
       SUM(amount) as total
FROM transactions
WHERE type IN ('CREDIT_PURCHASE', 'SUBSCRIPTION_RENEWAL')
  AND status = 'CONFIRMED'
GROUP BY month, type
ORDER BY month DESC;
```

**Payment failures**:
```sql
SELECT COUNT(*) as failures,
       DATE_TRUNC('day', createdAt) as day
FROM transactions
WHERE type LIKE '%FAILED%'
GROUP BY day
ORDER BY day DESC;
```

---

## Subscription Model

**Purpose**: Track active subscriptions

```prisma
model Subscription {
  id                    String   @id @default(cuid())
  userId                String   @unique
  stripeSubscriptionId  String   @unique
  stripePriceId         String
  status                String   // active, canceled, past_due, etc.
  tierId                String   // tier_free, tier_pro, tier_max
  analysesPerMonth      Int
  analysesUsedThisMonth Int      @default(0)
  currentPeriodStart    DateTime
  currentPeriodEnd      DateTime
  cancelAtPeriodEnd     Boolean  @default(false)
  createdAt             DateTime @default(now())
  updatedAt             DateTime @updatedAt
}
```

### Subscription Status Values

| Status | Meaning | Count in MRR? |
|--------|---------|---------------|
| `active` | Paying subscriber | Yes |
| `trialing` | In trial period | No (count separately) |
| `past_due` | Payment failed, retrying | Yes (at risk) |
| `canceled` | Canceled but period active | Yes (until period ends) |
| `unpaid` | Payment failed, no retry | No (churned) |

### Tier MRR Contribution

| Tier | Monthly MRR |
|------|------------|
| `tier_pro` | $9.00 |
| `tier_max` | $69.00 |
| `tier_free` | $0.00 |

**Annual tiers**: Divide annual price by 12 for MRR
- Pro Annual: $90.00 → $7.50 MRR
- Max Annual: $690.00 → $57.50 MRR

---

## Credits Model

**Purpose**: Track user credit balances

```prisma
model Credits {
  id              String   @id @default(cuid())
  userId          String   @unique
  balance         Int      @default(10)     // Current available
  lifetimeCredits Int      @default(10)     // Total granted
  lifetimeSpent   Int      @default(0)      // Total consumed
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}
```

### Credit Economics Metrics

**Total Credits Issued**: `SUM(lifetimeCredits)`
**Total Credits Consumed**: `SUM(lifetimeSpent)`
**Credit Burn Rate**: `SUM(lifetimeSpent) / COUNT(DISTINCT users) / days_active`
**Average Balance**: `AVG(balance)`

---

## AdminAction Model (Audit Trail)

**Purpose**: Track admin operations affecting finances

```prisma
model AdminAction {
  id           String   @id @default(cuid())
  adminId      String
  targetUserId String?
  action       String   // GRANT_CREDITS, ADJUST_BALANCE, etc.
  details      Json
  ipAddress    String?
  userAgent    String?
  createdAt    DateTime @default(now())
}
```

### Financial Admin Actions

| Action | Description |
|--------|-------------|
| `GRANT_CREDITS` | Manual credit grant |
| `ADJUST_BALANCE` | Balance correction |
| `CHANGE_SUBSCRIPTION` | Manual tier change |
| `REFUND` | Process refund |
| `COMP_CREDIT` | Compensatory credits |

---

## Useful SQL Queries for CFO

### Active Subscriptions by Tier

```sql
SELECT tierId,
       COUNT(*) as count,
       CASE
         WHEN tierId = 'tier_pro' THEN COUNT(*) * 9
         WHEN tierId = 'tier_max' THEN COUNT(*) * 69
         ELSE 0
       END as mrr_contribution
FROM subscriptions
WHERE status = 'active'
GROUP BY tierId;
```

### Monthly Revenue (Subscription)

```sql
SELECT DATE_TRUNC('month', t.createdAt) as month,
       SUM(CASE
         WHEN s.tierId = 'tier_pro' THEN 9
         WHEN s.tierId = 'tier_max' THEN 69
         ELSE 0
       END) as subscription_mrr
FROM transactions t
JOIN subscriptions s ON s.userId = t.userId
WHERE t.type = 'SUBSCRIPTION_RENEWAL'
  AND t.status = 'CONFIRMED'
GROUP BY month
ORDER BY month DESC;
```

### Credit Pack Revenue (One-Time)

```sql
SELECT DATE_TRUNC('month', createdAt) as month,
       SUM(amount) as pack_revenue
FROM transactions
WHERE type = 'CREDIT_PURCHASE'
  AND status = 'CONFIRMED'
GROUP BY month
ORDER BY month DESC;
```

### Churn Analysis (Last 30 Days)

```sql
SELECT COUNT(*) as churned_count,
       tierId
FROM subscriptions
WHERE status IN ('canceled', 'unpaid')
  AND updatedAt > NOW() - INTERVAL '30 days'
GROUP BY tierId;
```

### Payment Failures (Pending Attention)

```sql
SELECT COUNT(*) as failed_count,
       DATE_TRUNC('day', createdAt) as day
FROM transactions
WHERE type LIKE '%FAILED%'
  OR status = 'CANCELLED'
GROUP BY day
ORDER BY day DESC
LIMIT 7;
```

---

## Schema File Location

Full schema: `/Users/kurultai/Eris/Parse/prisma/schema.prisma`
