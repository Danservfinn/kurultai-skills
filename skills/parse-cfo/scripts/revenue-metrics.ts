#!/usr/bin/env tsx
/**
 * Revenue Metrics Calculator
 * Calculates MRR, ARR, churn, and other SaaS metrics from the database
 *
 * Usage:
 *   DATABASE_URL=... npx tsx revenue-metrics.ts
 *
 * Environment Variables:
 *   DATABASE_URL - PostgreSQL connection string (required)
 *
 * Output: JSON with revenue metrics
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

interface RevenueMetrics {
  mrr: number
  arr: number
  subscriptionRevenue: number
  creditPackRevenue: number
  totalRevenue: number
  activeSubscriptions: number
  subscriptionsByTier: Record<string, { count: number; mrr: number }>
  churnedThisMonth: number
  customerChurnRate: number
  mrrChurned: number
  mrrChurnRate: number
  newSubscriptionsThisMonth: number
  mrrFromNew: number
  netNewMrr: number
  previousMrr: number
  calculatedAt: string
}

interface TierConfig {
  tierId: string
  monthlyPrice: number
  annualPrice: number
}

const TIER_PRICES: TierConfig[] = [
  { tierId: 'tier_pro', monthlyPrice: 9, annualPrice: 90 },
  { tierId: 'tier_max', monthlyPrice: 69, annualPrice: 690 },
  { tierId: 'tier_free', monthlyPrice: 0, annualPrice: 0 },
]

/**
 * Calculate monthly MRR contribution for a subscription
 */
function getMrrForSubscription(tierId: string, priceId: string): number {
  const tier = TIER_PRICES.find((t) => t.tierId === tierId)
  if (!tier) return 0

  // Annual subscriptions: divide by 12 for MRR
  const annualPriceIds = [
    'price_1SrWHY8LghiREdMSyEyzq1j3', // Pro Annual
    'price_1SrWHY8LghiREdMSEJVUeHU7', // Max Annual
  ]

  if (annualPriceIds.some((id) => priceId.includes(id.split('_')[2]))) {
    return tier.annualPrice / 12
  }

  return tier.monthlyPrice
}

/**
 * Calculate comprehensive revenue metrics
 */
async function calculateRevenueMetrics(): Promise<RevenueMetrics> {
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  const endOfLastMonth = new Date(now.getFullYear(), now.getMonth(), 1) // First day of this month = end of last month

  // Get all currently active subscriptions
  const activeSubscriptions = await prisma.subscription.findMany({
    where: {
      status: {
        in: ['active', 'trialing'],
      },
    },
  })

  // Calculate current MRR by tier
  const subscriptionsByTier: Record<string, { count: number; mrr: number }> = {}
  let totalMrr = 0

  for (const sub of activeSubscriptions) {
    const mrr = getMrrForSubscription(sub.tierId, sub.stripePriceId)

    if (!subscriptionsByTier[sub.tierId]) {
      subscriptionsByTier[sub.tierId] = { count: 0, mrr: 0 }
    }

    subscriptionsByTier[sub.tierId].count += 1
    subscriptionsByTier[sub.tierId].mrr += mrr
    totalMrr += mrr
  }

  // Get subscriptions that were active at the end of last month
  // These are subscriptions that were created before this month started
  // AND have not been canceled before this month started
  const lastMonthActiveSubscriptions = await prisma.subscription.findMany({
    where: {
      createdAt: { lt: startOfMonth },
      OR: [
        { status: { in: ['active', 'trialing'] } }, // Still active
        {
          // Canceled this month (was active at end of last month)
          status: { in: ['canceled', 'unpaid'] },
          updatedAt: { gte: startOfMonth },
        },
      ],
    },
  })

  let lastMonthMrr = 0
  for (const sub of lastMonthActiveSubscriptions) {
    lastMonthMrr += getMrrForSubscription(sub.tierId, sub.stripePriceId)
  }

  // Get churned subscriptions this month (with full details for MRR calculation)
  const churnedSubscriptions = await prisma.subscription.findMany({
    where: {
      status: {
        in: ['canceled', 'unpaid'],
      },
      updatedAt: {
        gte: startOfMonth,
      },
    },
  })

  const churnedThisMonth = churnedSubscriptions.length

  // Calculate MRR lost to churn
  let mrrChurned = 0
  for (const sub of churnedSubscriptions) {
    mrrChurned += getMrrForSubscription(sub.tierId, sub.stripePriceId)
  }

  // Customer churn rate (customers lost / customers at start of month)
  const activeAtStartOfMonth = lastMonthActiveSubscriptions.length
  const customerChurnRate = activeAtStartOfMonth > 0
    ? churnedThisMonth / activeAtStartOfMonth
    : 0

  // MRR churn rate (revenue lost / starting MRR)
  const mrrChurnRate = lastMonthMrr > 0
    ? mrrChurned / lastMonthMrr
    : 0

  // Get subscription revenue this month (from transactions)
  const subscriptionRevenueResult = await prisma.transaction.aggregate({
    where: {
      type: 'SUBSCRIPTION_RENEWAL',
      status: 'CONFIRMED',
      createdAt: {
        gte: startOfMonth,
      },
    },
    _sum: {
      amount: true,
    },
  })

  const subscriptionRevenue = subscriptionRevenueResult._sum.amount || 0

  // Get credit pack revenue this month
  const creditPackRevenueResult = await prisma.transaction.aggregate({
    where: {
      type: 'CREDIT_PURCHASE',
      status: 'CONFIRMED',
      createdAt: {
        gte: startOfMonth,
      },
    },
    _sum: {
      amount: true,
    },
  })

  const creditPackRevenue = creditPackRevenueResult._sum.amount || 0

  // Get new subscriptions this month (with MRR contribution)
  const newSubscriptions = await prisma.subscription.findMany({
    where: {
      createdAt: {
        gte: startOfMonth,
      },
    },
  })

  const newSubscriptionsThisMonth = newSubscriptions.length

  let mrrFromNew = 0
  for (const sub of newSubscriptions) {
    mrrFromNew += getMrrForSubscription(sub.tierId, sub.stripePriceId)
  }

  const netNewMrr = totalMrr - lastMonthMrr

  return {
    mrr: Math.round(totalMrr * 100) / 100,
    arr: Math.round(totalMrr * 12 * 100) / 100,
    subscriptionRevenue,
    creditPackRevenue,
    totalRevenue: subscriptionRevenue + creditPackRevenue,
    activeSubscriptions: activeSubscriptions.length,
    subscriptionsByTier,
    churnedThisMonth,
    customerChurnRate: Math.round(customerChurnRate * 1000) / 10, // percentage with 1 decimal
    mrrChurned: Math.round(mrrChurned * 100) / 100,
    mrrChurnRate: Math.round(mrrChurnRate * 1000) / 10, // percentage with 1 decimal
    newSubscriptionsThisMonth,
    mrrFromNew: Math.round(mrrFromNew * 100) / 100,
    netNewMrr: Math.round(netNewMrr * 100) / 100,
    previousMrr: Math.round(lastMonthMrr * 100) / 100,
    calculatedAt: now.toISOString(),
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const databaseUrl = process.env.DATABASE_URL

  if (!databaseUrl) {
    console.error(JSON.stringify({ error: 'DATABASE_URL environment variable required' }, null, 2))
    process.exit(1)
  }

  calculateRevenueMetrics()
    .then((metrics) => {
      console.log(JSON.stringify(metrics, null, 2))
    })
    .catch((error) => {
      console.error(JSON.stringify({ error: error.message }, null, 2))
      process.exit(1)
    })
    .finally(() => prisma.$disconnect())
}

export { calculateRevenueMetrics }
