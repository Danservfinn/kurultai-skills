#!/usr/bin/env tsx
/**
 * Payout Tracking & Cash Flow Forecast
 * Tracks Stripe pending balances and projects Mercury payout timing
 *
 * Usage:
 *   STRIPE_SECRET_KEY=... npx tsx payout-tracking.ts
 *
 * Environment Variables:
 *   STRIPE_SECRET_KEY - Stripe secret key (required)
 *
 * Output: JSON with pending payouts, expected dates, and cash forecast
 */

interface PayoutTrackingResult {
  generatedAt: string
  stripePending: {
    available: number
    pending: number
    totalCollected: number
    currency: string
  }
  payoutForecast: {
    expectedDailyPayout: number
    expectedPayoutDays: number
    nextPayoutEstimate: string
    totalPendingArrival: string
  }
  cashPosition: {
    stripeCollectable: number
    inTransit: number
    totalEnRoute: number
  }
  recentActivity: PayoutActivity[]
}

interface PayoutActivity {
  date: string
  amount: number
  status: 'pending' | 'in_transit' | 'completed'
  type: string
}

/**
 * Fetch Stripe balance and payout information
 * Note: Requires Stripe API key with read access
 */
async function getPayoutTracking(stripeKey: string): Promise<PayoutTrackingResult> {
  const baseUrl = 'https://api.stripe.com/v1'

  const headers = {
    'Authorization': `Bearer ${stripeKey}`,
    'Content-Type': 'application/x-www-form-urlencoded',
  }

  try {
    // Fetch current balance
    const balanceRes = await fetch(`${baseUrl}/balance`, { headers })
    if (!balanceRes.ok) {
      throw new Error(`Stripe API error: ${balanceRes.status}`)
    }
    const balanceData = await balanceRes.json()

    // Extract available and pending balances
    const available = balanceData.available?.reduce((sum: number, obj: any) => sum + obj.amount, 0) || 0
    const pending = balanceData.pending?.reduce((sum: number, obj: any) => sum + obj.amount, 0) || 0

    // Fetch recent payouts to understand payout patterns
    const payoutsRes = await fetch(`${baseUrl}/payouts?limit=10`, { headers })
    const payoutsData = await payoutsRes.json()

    // Calculate average daily payout from recent history
    const recentPayouts = (payoutsData.data || []).filter((p: any) => p.status === 'paid')
    const avgPayoutAmount = recentPayouts.length > 0
      ? recentPayouts.reduce((sum: number, p: any) => sum + p.amount, 0) / recentPayouts.length
      : 0

    // Estimate payout timing (Stripe Standard = ~2 business day rolling delay)
    const payoutDelayDays = 2 // Business days for Stripe Standard
    const now = new Date()

    // Calculate next expected payout date (add business days)
    let nextPayoutDate = new Date(now)
    let businessDaysAdded = 0
    while (businessDaysAdded < payoutDelayDays) {
      nextPayoutDate.setDate(nextPayoutDate.getDate() + 1)
      const dayOfWeek = nextPayoutDate.getDay()
      if (dayOfWeek !== 0 && dayOfWeek !== 6) { // Skip weekends
        businessDaysAdded++
      }
    }

    // Add 1 more day for Mercury settlement
    nextPayoutDate.setDate(nextPayoutDate.getDate() + 1)

    // Build recent activity summary
    const recentActivity: PayoutActivity[] = []

    // Add pending balance breakdown
    if (balanceData.pending) {
      for (const pool of balanceData.pending) {
        recentActivity.push({
          date: now.toISOString().split('T')[0],
          amount: pool.amount / 100,
          status: 'pending',
          type: pool.source_types ? Object.keys(pool.source_types).join('+') : 'mixed',
        })
      }
    }

    return {
      generatedAt: now.toISOString(),
      stripePending: {
        available: available / 100,
        pending: pending / 100,
        totalCollected: (available + pending) / 100,
        currency: balanceData.pending?.[0]?.currency || 'usd',
      },
      payoutForecast: {
        expectedDailyPayout: avgPayoutAmount / 100,
        expectedPayoutDays: payoutDelayDays + 1, // Stripe delay + Mercury settlement
        nextPayoutEstimate: nextPayoutDate.toISOString(),
        totalPendingArrival: nextPayoutDate.toISOString(),
      },
      cashPosition: {
        stripeCollectable: available / 100,
        inTransit: pending / 100,
        totalEnRoute: (available + pending) / 100,
      },
      recentActivity,
    }
  } catch (error) {
    console.error('Error fetching payout tracking:', error)
    throw error
  }
}

/**
 * Generate cash flow forecast for next 30 days
 * Projects expected Stripe payouts arriving in Mercury
 */
interface CashFlowForecast {
  forecastDate: string
  days: DailyForecast[]
  totalExpectedPayouts: number
}

interface DailyForecast {
  date: string
  expectedPayout: number
  cumulativeTotal: number
}

async function generateCashFlowForecast(
  stripeKey: string,
  days: number = 30
): Promise<CashFlowForecast> {
  const tracking = await getPayoutTracking(stripeKey)
  const now = new Date()
  const forecasts: DailyForecast[] = []

  // Use recent average as baseline, or pending balance divided by typical delay
  const dailyPayoutBaseline = tracking.payoutForecast.expectedDailyPayout ||
    tracking.stripePending.pending / tracking.payoutForecast.expectedPayoutDays

  let cumulative = 0
  let currentDate = new Date(now)

  // Start forecasting from tomorrow (payouts initiated today won't arrive until delay passes)
  currentDate.setDate(currentDate.getDate() + 1)

  for (let i = 0; i < days; i++) {
    // Skip weekends for payout arrivals (banking days only)
    const dayOfWeek = currentDate.getDay()
    const isBusinessDay = dayOfWeek !== 0 && dayOfWeek !== 6

    // Payouts only arrive on business days
    const expectedPayout = isBusinessDay ? dailyPayoutBaseline : 0

    cumulative += expectedPayout

    forecasts.push({
      date: currentDate.toISOString().split('T')[0],
      expectedPayout: Math.round(expectedPayout * 100) / 100,
      cumulativeTotal: Math.round(cumulative * 100) / 100,
    })

    currentDate.setDate(currentDate.getDate() + 1)
  }

  return {
    forecastDate: now.toISOString(),
    days: forecasts,
    totalExpectedPayouts: Math.round(cumulative * 100) / 100,
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const stripeKey = process.env.STRIPE_SECRET_KEY
  const args = process.argv.slice(2)
  const command = args[0] || 'status'

  if (!stripeKey) {
    console.error(JSON.stringify({ error: 'STRIPE_SECRET_KEY environment variable required' }, null, 2))
    process.exit(1)
  }

  if (command === 'forecast') {
    const days = parseInt(args[1]) || 30
    generateCashFlowForecast(stripeKey, days)
      .then((forecast) => {
        console.log(JSON.stringify(forecast, null, 2))
      })
      .catch((error) => {
        console.error(JSON.stringify({ error: error.message }, null, 2))
        process.exit(1)
      })
  } else {
    getPayoutTracking(stripeKey)
      .then((result) => {
        console.log(JSON.stringify(result, null, 2))
      })
      .catch((error) => {
        console.error(JSON.stringify({ error: error.message }, null, 2))
        process.exit(1)
      })
  }
}

export { getPayoutTracking, generateCashFlowForecast }
