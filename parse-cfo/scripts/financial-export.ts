#!/usr/bin/env tsx
/**
 * Financial Data Export
 * Generates financial data exports in multiple formats (JSON, CSV, Markdown)
 *
 * Usage:
 *   DATABASE_URL=... npx tsx financial-export.ts [format] [output-path]
 *
 * Formats:
 *   json - Structured JSON for analysis/dashboards
 *   csv - Transaction log for accounting
 *   markdown - Human-readable executive summary
 *   all - Generate all formats
 *
 * Environment Variables:
 *   DATABASE_URL - PostgreSQL connection string (required)
 *   STRIPE_SECRET_KEY - For balance data (optional)
 */

import { PrismaClient } from '@prisma/client'
import { writeFile } from 'fs/promises'
import { join } from 'path'

const prisma = new PrismaClient()

type ExportFormat = 'json' | 'csv' | 'markdown' | 'all'

interface FinancialData {
  generatedAt: string
  period: string
  revenue: RevenueSnapshot
  subscriptions: SubscriptionSnapshot
  cash: CashSnapshot
  transactions: TransactionSummary[]
}

interface RevenueSnapshot {
  mrr: number
  arr: number
  subscriptionRevenue: number
  creditPackRevenue: number
  totalRevenue: number
  netNewMrr: number
}

interface SubscriptionSnapshot {
  total: number
  byTier: Record<string, number>
  newThisMonth: number
  churnedThisMonth: number
  churnRate: number
}

interface CashSnapshot {
  stripeAvailable?: number
  stripePending?: number
  mercuryBalance?: number
  totalCash: number
}

interface TransactionSummary {
  date: string
  count: number
  totalAmount: number
  byType: Record<string, { count: number; amount: number }>
}

/**
 * Gather financial data from database
 */
async function gatherFinancialData(): Promise<FinancialData> {
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  const period = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`

  // Revenue from transactions this month
  const [subscriptionRevenue, creditPackRevenue] = await Promise.all([
    prisma.transaction.aggregate({
      where: {
        type: 'SUBSCRIPTION_RENEWAL',
        status: 'CONFIRMED',
        createdAt: { gte: startOfMonth },
      },
      _sum: { amount: true },
    }),
    prisma.transaction.aggregate({
      where: {
        type: 'CREDIT_PURCHASE',
        status: 'CONFIRMED',
        createdAt: { gte: startOfMonth },
      },
      _sum: { amount: true },
    }),
  ])

  // Active subscriptions
  const activeSubs = await prisma.subscription.findMany({
    where: { status: { in: ['active', 'trialing'] } },
  })

  // Calculate MRR (simplified)
  const mrr = activeSubs.reduce((sum, sub) => {
    if (sub.tierId === 'tier_pro') return sum + 9
    if (sub.tierId === 'tier_max') return sum + 69
    return sum
  }, 0)

  // By tier counts
  const byTier: Record<string, number> = {}
  for (const sub of activeSubs) {
    byTier[sub.tierId] = (byTier[sub.tierId] || 0) + 1
  }

  // Churn and new this month
  const [churned, newSubs] = await Promise.all([
    prisma.subscription.count({
      where: {
        status: { in: ['canceled', 'unpaid'] },
        updatedAt: { gte: startOfMonth },
      },
    }),
    prisma.subscription.count({
      where: { createdAt: { gte: startOfMonth } },
    }),
  ])

  const churnRate = (activeSubs.length + churned) > 0
    ? (churned / (activeSubs.length + churned))
    : 0

  // Transaction summary by day (last 30 days)
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  const recentTransactions = await prisma.transaction.findMany({
    where: {
      createdAt: { gte: thirtyDaysAgo },
      status: 'CONFIRMED',
    },
    orderBy: { createdAt: 'desc' },
  })

  // Group by date
  const transactionsByDate: Record<string, TransactionSummary> = {}
  for (const tx of recentTransactions) {
    const date = tx.createdAt.toISOString().split('T')[0]
    if (!transactionsByDate[date]) {
      transactionsByDate[date] = {
        date,
        count: 0,
        totalAmount: 0,
        byType: {},
      }
    }
    transactionsByDate[date].count++
    transactionsByDate[date].totalAmount += tx.amount

    if (!transactionsByDate[date].byType[tx.type]) {
      transactionsByDate[date].byType[tx.type] = { count: 0, amount: 0 }
    }
    transactionsByDate[date].byType[tx.type].count++
    transactionsByDate[date].byType[tx.type].amount += tx.amount
  }

  return {
    generatedAt: now.toISOString(),
    period,
    revenue: {
      mrr,
      arr: mrr * 12,
      subscriptionRevenue: subscriptionRevenue._sum.amount || 0,
      creditPackRevenue: creditPackRevenue._sum.amount || 0,
      totalRevenue: (subscriptionRevenue._sum.amount || 0) + (creditPackRevenue._sum.amount || 0),
      netNewMrr: 0, // Would need historical data
    },
    subscriptions: {
      total: activeSubs.length,
      byTier,
      newThisMonth: newSubs,
      churnedThisMonth: churned,
      churnRate: Math.round(churnRate * 1000) / 10,
    },
    cash: {
      totalCash: 0, // Will be populated if Stripe API available
    },
    transactions: Object.values(transactionsByDate).slice(0, 30),
  }
}

/**
 * Generate JSON export
 */
function generateJsonExport(data: FinancialData): string {
  return JSON.stringify(data, null, 2)
}

/**
 * Generate CSV export (transaction log)
 */
function generateCsvExport(data: FinancialData): string {
  const headers = 'Date,Transaction Count,Total Amount,Subscription Revenue,Credit Pack Revenue\n'
  const rows = data.transactions.map((tx) => {
    const subRev = tx.byType['SUBSCRIPTION_RENEWAL']?.amount || 0
    const packRev = tx.byType['CREDIT_PURCHASE']?.amount || 0
    return `${tx.date},${tx.count},${tx.totalAmount},${subRev},${packRev}`
  })
  return headers + rows.join('\n')
}

/**
 * Generate Markdown export (executive summary)
 */
function generateMarkdownExport(data: FinancialData): string {
  return `# Parse Financial Report - ${data.period}

*Generated: ${new Date(data.generatedAt).toLocaleString()}*

---

## Revenue Summary

| Metric | Value |
|--------|-------|
| MRR | $${data.revenue.mrr.toFixed(2)} |
| ARR | $${data.revenue.arr.toFixed(2)} |
| Subscription Revenue (MTD) | $${data.revenue.subscriptionRevenue.toFixed(2)} |
| Credit Pack Revenue (MTD) | $${data.revenue.creditPackRevenue.toFixed(2)} |
| Total Revenue (MTD) | $${data.revenue.totalRevenue.toFixed(2)} |

---

## Subscriptions

| Tier | Count |
|------|-------|
${Object.entries(data.subscriptions.byTier).map(([tier, count]) => `| ${tier} | ${count} |`).join('\n')}

| Metric | Value |
|--------|-------|
| Total Active | ${data.subscriptions.total} |
| New This Month | ${data.subscriptions.newThisMonth} |
| Churned This Month | ${data.subscriptions.churnedThisMonth} |
| Churn Rate | ${data.subscriptions.churnRate}% |

---

## Cash Position

| Account | Balance |
|---------|---------|
| Total Cash | $${data.cash.totalCash.toFixed(2)} |

---

## Recent Transactions (Last 30 Days)

${data.transactions.slice(0, 10).map((tx) => `
**${tx.date}**: ${tx.count} transactions, $${tx.totalAmount.toFixed(2)}
${Object.entries(tx.byType).map(([type, info]) => `  - ${type}: ${info.count} × $${info.amount.toFixed(2)}`).join('\n')}
`).join('\n')}
`
}

/**
 * Main export function
 */
async function exportFinancialData(
  format: ExportFormat = 'all',
  outputPath: string = './financial-export'
): Promise<void> {
  const data = await gatherFinancialData()

  if (format === 'json' || format === 'all') {
    const json = generateJsonExport(data)
    await writeFile(join(outputPath, 'financial-report.json'), json)
    console.log(`✅ JSON export written to ${outputPath}/financial-report.json`)
  }

  if (format === 'csv' || format === 'all') {
    const csv = generateCsvExport(data)
    await writeFile(join(outputPath, 'transactions.csv'), csv)
    console.log(`✅ CSV export written to ${outputPath}/transactions.csv`)
  }

  if (format === 'markdown' || format === 'all') {
    const md = generateMarkdownExport(data)
    await writeFile(join(outputPath, 'financial-report.md'), md)
    console.log(`✅ Markdown export written to ${outputPath}/financial-report.md`)
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const databaseUrl = process.env.DATABASE_URL
  const format = (process.argv[2] || 'all') as ExportFormat
  const outputPath = process.argv[3] || './financial-export'

  if (!databaseUrl) {
    console.error('Error: DATABASE_URL environment variable required')
    process.exit(1)
  }

  exportFinancialData(format, outputPath)
    .then(() => console.log('\n✅ Export complete'))
    .catch((error) => {
      console.error('Error:', error.message)
      process.exit(1)
    })
    .finally(() => prisma.$disconnect())
}

export { gatherFinancialData, generateJsonExport, generateCsvExport, generateMarkdownExport }
