# Parse Pricing & Unit Economics

Reference for Parse SaaS pricing tiers, credit packs, and unit economics calculations.

---

## Stripe Configuration

**Account ID**: `acct_1Snq0B8LghiREdMS`
**Dashboard**: https://dashboard.stripe.com/acct_1Snq0B8LghiREdMS

---

## Subscription Tiers

### Pro Tier

| Attribute | Value |
|-----------|-------|
| Monthly Price ID | `price_1SrWHX8LghiREdMSL26rdsSH` |
| Annual Price ID | `price_1SrWHY8LghiREdMSyEyzq1j3` |
| Monthly Price | $9.00 |
| Annual Price | $90.00 (17% savings) |
| Credits Per Month | 100 |
| Included Features | Full analysis, all agents, history |

**Unit Economics - Pro Monthly**:
- Revenue: $9.00
- Variable Cost: ~$3.00 (100 analyses × $0.03/analysis)
- Gross Margin: 67%
- Contribution Margin: $6.00/month

**Unit Economics - Pro Annual**:
- Revenue: $90.00/year
- Variable Cost: ~$36.00/year
- Gross Margin: 60%
- Contribution Margin: $54.00/year

### Max Tier

| Attribute | Value |
|-----------|-------|
| Monthly Price ID | `price_1SrWHY8LghiREdMSN6D82M6g` |
| Annual Price ID | `price_1SrWHY8LghiREdMSEJVUeHU7` |
| Monthly Price | $69.00 |
| Annual Price | $690.00 (17% savings) |
| Credits Per Month | 1,000 |
| Included Features | Everything in Pro + API access + priority support |

**Unit Economics - Max Monthly**:
- Revenue: $69.00
- Variable Cost: ~$30.00 (1,000 analyses × $0.03/analysis)
- Gross Margin: 57%
- Contribution Margin: $39.00/month

**Unit Economics - Max Annual**:
- Revenue: $690.00/year
- Variable Cost: ~$360.00/year
- Gross Margin: 48%
- Contribution Margin: $330.00/year

---

## Credit Packs (One-Time)

### Starter Pack

| Attribute | Value |
|-----------|-------|
| Price ID | `price_1SrWHZ8LghiREdMS0bq7hsI7` |
| Price | $4.99 |
| Credits | 10 |
| Cost Per Credit | $0.50 |
| Variable Cost | ~$0.30 (10 × $0.03) |
| Gross Margin | 94% |

### Growth Pack

| Attribute | Value |
|-----------|-------|
| Price ID | `price_1SrWHa8LghiREdMSjBnAWps3` |
| Price | $12.99 |
| Credits | 30 |
| Cost Per Credit | $0.43 |
| Variable Cost | ~$0.90 (30 × $0.03) |
| Gross Margin | 93% |

### Power Pack

| Attribute | Value |
|-----------|-------|
| Price ID | `price_1SrWHa8LghiREdMSGCDAl5t3` |
| Price | $34.99 |
| Credits | 100 |
| Cost Per Credit | $0.35 |
| Variable Cost | ~$3.00 (100 × $0.03) |
| Gross Margin | 91% |

---

## Cost Per Analysis

**Confirmed Cost**: ~$0.03 per analysis

This includes:
- LLM API costs (multi-provider pool: DeepSeek, Z.ai, OpenRouter)
- No additional per-analysis costs (search APIs bundled)
- Orchestrator overhead negligible

**Cost Variance**: Article complexity affects agent count
- Simple articles: Fewer agents = lower cost
- Complex articles: All 11+ agents = higher cost
- Average: ~$0.03 (break-even point)

---

## Price Tiers Summary Table

| Product | Price | Cost | Margin % | Margin $ |
|---------|-------|------|----------|---------|
| Pro Monthly | $9.00 | $3.00 | 67% | $6.00 |
| Pro Annual | $90.00 | $36.00 | 60% | $54.00 |
| Max Monthly | $69.00 | $30.00 | 57% | $39.00 |
| Max Annual | $690.00 | $360.00 | 48% | $330.00 |
| Starter Pack | $4.99 | $0.30 | 94% | $4.69 |
| Growth Pack | $12.99 | $0.90 | 93% | $12.09 |
| Power Pack | $34.99 | $3.00 | 91% | $31.99 |

---

## MRR/ARR Calculations

**MRR Formula**:
```
MRR = (Pro_Monthly_Count × $9) + (Max_Monthly_Count × $69) + (Pro_Annual_Count × $9/12) + (Max_Annual_Count × $69/12)
```

**ARR Formula**:
```
ARR = MRR × 12
```

**Note**: Credit packs are NOT included in MRR/ARR (one-time revenue)

---

## Mercury Bank Account

| Field | Value |
|-------|-------|
| Routing Number | 121145433 |
| Account Number | 474816468300230 |
| Account Holder | Kurultai Limited Liability Company |
| Dashboard | https://mercury.com |

---

## Stripe Payout Configuration

- Payout Schedule: Configurable (daily/weekly/manual)
- Minimum Payout: $50 recommended
- Bank Status: Linked (micro-deposits pending)
- Payout Destination: Mercury account above

---

## Webhook Events for Financial Tracking

Monitor these events in `transactions` table:
- `checkout.session.completed` - New purchase (pack or subscription)
- `customer.subscription.created` - New subscription
- `invoice.paid` - Subscription renewal
- `invoice.payment_failed` - Churn risk alert

**Reconciliation**: Each transaction has `metadata.stripeEventId` for Stripe lookup.
