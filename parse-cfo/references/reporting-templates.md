# Parse Financial Reporting Templates

Standard formats for CFO-level financial reporting on Parse SaaS operations.

---

## Report Types

| Report | Frequency | Audience | Purpose |
|--------|-----------|----------|---------|
| Daily Flash | Daily | Internal | Cash position, revenue pulse, alerts |
| Weekly Summary | Weekly | Internal | Trend analysis, churn watch |
| Monthly Executive | Monthly | Leadership | Full financial picture, forecasting |
| Ad-Hoc Analysis | As needed | Varies | Deep dives, investigations |

---

## Daily Flash Report

**Purpose**: Quick daily check on financial health

**Template**:

```markdown
# Parse Daily Flash - YYYY-MM-DD

## Cash Position

| Account | Balance | Change (24h) |
|---------|---------|--------------|
| Stripe (Available) | $X,XXX | +$XX |
| Stripe (Pending) | $XXX | +$XX |
| Mercury | $X,XXX | +$XX |
| **Total Cash** | **$X,XXX** | **+$XX** |

## Revenue Today

| Metric | Today | Yesterday | Change |
|--------|-------|-----------|--------|
| New Subscriptions | X | X | +X |
| Credit Pack Sales | $XX | $XX | +$XX |
| MRR | $X,XXX | $X,XXX | +$XX |

## Active Subscriptions

| Tier | Active | Net Change (24h) |
|------|--------|------------------|
| Pro | XXX | +X |
| Max | XX | 0 |
| **Total** | **XXX** | **+X** |

## Alerts

- [ ] Payment failures: X (requires attention)
- [ ] High churn risk: X users
- [ ] Stripe webhook issues: None
- [ ] Mercury pending deposits: X

## Notes

[Space for ad-hoc notes on anomalies, promotions, etc.]
```

---

## Weekly Summary Report

**Purpose**: Track trends and identify issues

**Template**:

```markdown
# Parse Weekly Summary - Week of YYYY-MM-DD

## Revenue Summary

| Metric | This Week | Last Week | WoW Change |
|--------|-----------|-----------|------------|
| Subscription Revenue | $XXX | $XXX | +X% |
| Credit Pack Revenue | $XXX | $XXX | +X% |
| Total Revenue | $XXX | $XXX | +X% |
| MRR | $X,XXX | $X,XXX | +X% |
| ARR | $XX,XXX | $XX,XXX | +X% |

## Subscription Metrics

| Metric | This Week | Last Week | WoW Change |
|--------|-----------|-----------|------------|
| New Subscribers | XX | XX | +X |
| Churned | X | X | -X |
| Net New | XX | XX | +X |
| Churn Rate | X.X% | X.X% | +/-X.X% |

### Tier Breakdown

| Tier | Start | New | Churned | End | MRR Change |
|------|-------|-----|---------|-----|------------|
| Pro | XXX | XX | X | XXX | +$XX |
| Max | XX | X | 0 | XX | +$XX |

## Cash Flow

| Category | Amount |
|----------|--------|
| Starting Balance | $X,XXX |
| Revenue In | +$XXX |
| Payouts Out | -$XXX |
| Ending Balance | $X,XXX |

## Top Concerns

1. [Concern #1 - e.g., Elevated churn in Pro tier]
2. [Concern #2]
3. [Concern #3]

## Wins

1. [Win #1 - e.g., Max tier growth accelerated]
2. [Win #2]

## Forecast Next Week

- Expected MRR: $X,XXX (+/- $XX)
- Key events: [Promotions, features, etc.]
```

---

## Monthly Executive Report

**Purpose**: Comprehensive financial review for leadership

**Template**:

```markdown
# Parse Monthly Executive Report - MMMM YYYY

## Executive Summary

[3-5 bullet summary of month performance]

- MRR grew X% to $X,XXX, driven primarily by [Pro/Max] tier
- Churn rate of X.X% is [above/below] target of X.X%
- Cash position strengthened to $XX,XXX
- Key risks: [List]

---

## Revenue

### Total Revenue

| Category | This Month | Last Month | MoM | YoY |
|----------|------------|------------|-----|-----|
| Subscription | $X,XXX | $X,XXX | +X% | N/A |
| Credit Packs | $XXX | $XXX | +X% | N/A |
| **Total** | **$X,XXX** | **$X,XXX** | **+X%** | **N/A** |

### Recurring Revenue Metrics

| Metric | Value | Change |
|--------|-------|--------|
| MRR | $X,XXX | +X% MoM |
| ARR | $XX,XXX | +X% MoM |
| ARPU (Avg Revenue Per User) | $XX | +X% MoM |

### Revenue by Tier

| Tier | Subscribers | MRR | Avg Revenue/User |
|------|-------------|-----|------------------|
| Pro | XXX | $X,XXX | $9.00 |
| Max | XX | $X,XXX | $69.00 |
| **Total** | **XXX** | **$X,XXX** | **$XX.XX** |

---

## Subscription Metrics

### Growth

| Metric | This Month | Last Month | MoM |
|--------|------------|------------|-----|
| New Subscribers | XX | XX | +X |
| Gross Churn | X | X | -X |
| Net New | XX | XX | +X |
| Churn Rate | X.X% | X.X% | +/-X.X% |

### Churn by Tier

| Tier | Start | Churned | Churn Rate |
|------|-------|---------|------------|
| Pro | XXX | X | X.X% |
| Max | XX | 0 | 0.0% |

### Cohort Retention

| Signup Month | Start | Month 1 | Month 2 | Month 3 |
|--------------|-------|---------|---------|---------|
| MMM YYYY | 100 | 95% | 90% | 87% |
| ... | ... | ... | ... | ... |

---

## Unit Economics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| CAC (Customer Acquisition Cost) | $XX | $XX | ✅/⚠️ |
| LTV (Lifetime Value) | $XXX | $XXX | ✅/⚠️ |
| LTV:CAC Ratio | X:1 | 3:1 | ✅/⚠️ |
| Payback Period | X months | <12 | ✅/⚠️ |

**Margin Analysis**:
- Pro tier gross margin: XX%
- Max tier gross margin: XX%
- Credit pack gross margin: XX%
- Weighted average gross margin: XX%

---

## Cash Position

### Balances

| Account | Balance | Notes |
|---------|---------|-------|
| Stripe (Available) | $X,XXX | Can be withdrawn |
| Stripe (Pending) | $XXX | Awaiting payout |
| Mercury | $X,XXX | Operating cash |
| **Total** | **$X,XXX** | |

### Cash Flow

| Category | Amount | Notes |
|----------|--------|-------|
| Starting Cash | $X,XXX | |
| Revenue In | +$X,XXX | |
| Payouts Out | -$X,XXX | Stripe → Mercury |
| OpEx | -$XXX | [If tracked] |
| **Ending Cash** | **$X,XXX** | |

### Runway

At current burn rate: $XXX/month
Runway: XX months (excluding new revenue)

---

## Product Metrics

### Credit Usage

| Metric | Value |
|--------|-------|
| Total analyses run | X,XXX |
| Analyses per user (avg) | XX |
| Credit pack consumption | XX% |
| Subscription credit consumption | XX% |

### Tier Distribution

| Tier | Count | % of Base |
|------|-------|------------|
| Free | XXX | XX% |
| Pro | XXX | XX% |
| Max | XX | XX% |

---

## Forecast

### Next 3 Months

| Month | Projected MRR | Confidence |
|-------|---------------|------------|
| MMM | $X,XXX | High |
| MMM | $X,XXX | Medium |
| MMM | $X,XXX | Low |

### Assumptions
- Growth rate: X% MoM
- Churn rate: X.X%
- Avg ticket size: $XX

---

## Risks & Opportunities

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | High/Med/Low | [Action] |
| [Risk 2] | High/Med/Low | [Action] |

### Opportunities

| Opportunity | Impact | Effort |
|-------------|--------|--------|
| [Opp 1] | High/Med/Low | High/Med/Low |
| [Opp 2] | High/Med/Low | High/Med/Low |

---

## Action Items

- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Action item 3]

---

## Appendix: Data Export

[Attach CSV/JSON exports for detailed analysis]
```

---

## Structured Data Exports

### JSON Metrics Format

```json
{
  "reportDate": "YYYY-MM-DD",
  "reportType": "daily|weekly|monthly",
  "generatedAt": "YYYY-MM-DDTHH:mm:ssZ",
  "metrics": {
    "cash": {
      "stripeAvailable": 1000.00,
      "stripePending": 500.00,
      "mercury": 5000.00,
      "total": 6500.00
    },
    "revenue": {
      "mrr": 5000.00,
      "arr": 60000.00,
      "subscriptionRevenue": 4500.00,
      "creditPackRevenue": 500.00
    },
    "subscriptions": {
      "pro": {
        "active": 50,
        "new": 5,
        "churned": 2
      },
      "max": {
        "active": 10,
        "new": 2,
        "churned": 0
      }
    },
    "churn": {
      "rate": 0.033,
      "count": 2
    }
  }
}
```

### CSV Transaction Log Format

```csv
date,transaction_id,user_id,type,amount,status,tier,description
2026-01-20,txn_abc123,user_456,CREDIT_PURCHASE,4.99,CONFIRMED,Starter Pack
2026-01-20,txn_def789,user_123,SUBSCRIPTION_RENEWAL,9.00,CONFIRMED,Pro Monthly
```
