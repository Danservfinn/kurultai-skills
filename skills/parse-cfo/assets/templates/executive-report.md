# Parse {{report_type}} Report - {{date_range}}

**Generated**: {{generated_at}}
**Prepared by**: Parse CFO (automated)

---

## Executive Summary

{{executive_summary_bullets}}

---

## Cash Position

| Account | Balance | Change ({{period}}) |
|---------|---------|-------------------|
| Stripe (Available) | ${{stripe_available}} | {{stripe_change}} |
| Stripe (Pending) | ${{stripe_pending}} | {{stripe_pending_change}} |
| Mercury | ${{mercury_balance}} | {{mercury_change}} |
| **Total Cash** | **${{total_cash}}** | **{{total_change}}** |

---

## Revenue

### Revenue Summary

| Metric | {{current_period}} | {{prior_period}} | Change |
|--------|------------------|-----------------|--------|
| Subscription Revenue | ${{subscription_revenue}} | ${{prior_subscription}} | {{sub_change}}% |
| Credit Pack Revenue | ${{credit_pack_revenue}} | ${{prior_credit_pack}} | {{pack_change}}% |
| **Total Revenue** | **${{total_revenue}}** | **${{prior_total}}** | **{{total_change}}%** |

### Recurring Revenue Metrics

| Metric | Value | Period Change |
|--------|-------|---------------|
| MRR | ${{mrr}} | {{mrr_change}} |
| ARR | ${{arr}} | {{arr_change}} |
| ARPU | ${{arpu}} | {{arpu_change}} |

---

## Subscriptions

### Active Subscriptions by Tier

| Tier | Count | MRR Contribution | Net Change |
|------|-------|------------------|------------|
| Pro | {{pro_count}} | ${{pro_mrr}} | {{pro_net}} |
| Max | {{max_count}} | ${{max_mrr}} | {{max_net}} |
| **Total** | **{{total_count}}** | **${{total_mrr}}** | **{{total_net}}** |

### Growth Metrics

| Metric | {{current_period}} | {{prior_period}} |
|--------|------------------|-----------------|
| New Subscribers | {{new_subscribers}} | {{prior_new}} |
| Churned | {{churned}} | {{prior_churned}} |
| Net New | {{net_new}} | {{prior_net}} |
| Churn Rate | {{churn_rate}}% | {{prior_churn_rate}}% |

---

## Unit Economics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Pro Gross Margin | {{pro_margin}}% | 67% | {{margin_status}} |
| Max Gross Margin | {{max_margin}}% | 57% | {{margin_status}} |
| Weighted Avg Margin | {{weighted_margin}}% | 60% | {{margin_status}} |

---

## Product Metrics

### Credit Usage

| Metric | Value |
|--------|-------|
| Total Analyses ({{period}}) | {{total_analyses}} |
| Avg Analyses per User | {{avg_analyses}} |
| Credit Utilization Rate | {{utilization}}% |

---

## Alerts & Action Items

### Alerts

{{#each alerts}}
- [ ] {{this}}
{{/each}}

### Action Items

{{#each actions}}
- [ ] {{this}}
{{/each}}

---

## Appendix

### Data Exports

Attached:
- `transactions.csv` - Full transaction log
- `metrics.json` - Raw metrics data
- `cohorts.json` - Cohort retention data

---

*Report template located at: `/Users/kurultai/.claude/skills/parse-cfo/assets/templates/executive-report.md`*
