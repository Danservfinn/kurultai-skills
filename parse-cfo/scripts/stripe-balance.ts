#!/usr/bin/env tsx
/**
 * Stripe Balance Check
 * Queries Stripe API for current and pending balances
 *
 * Usage:
 *   STRIPE_SECRET_KEY=sk_live_... npx tsx stripe-balance.ts
 *
 * Environment Variables:
 *   STRIPE_SECRET_KEY - Stripe secret key (required)
 *
 * Output: JSON with balance details
 */

import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-12-18.acacia',
  typescript: true,
})

interface BalanceResult {
  available: number
  pending: number
  currency: string
  availableBreakdown: Record<string, number>
  pendingBreakdown: Record<string, number>
  lastUpdated: string
}

async function getStripeBalance(): Promise<BalanceResult> {
  try {
    const balance = await stripe.balance.retrieve()

    // Aggregate available balance by source type
    const availableBreakdown: Record<string, number> = {}
    for (const funds of balance.available) {
      const source = funds.source_types?.[0] || 'other'
      availableBreakdown[source] = (availableBreakdown[source] || 0) + (funds.amount / 100)
    }

    // Aggregate pending balance by source type
    const pendingBreakdown: Record<string, number> = {}
    for (const funds of balance.pending) {
      const source = funds.source_types?.[0] || 'other'
      pendingBreakdown[source] = (pendingBreakdown[source] || 0) + (funds.amount / 100)
    }

    // Total available across all currencies (typically USD)
    const available = balance.available.reduce((sum, funds) => sum + funds.amount / 100, 0)
    const pending = balance.pending.reduce((sum, funds) => sum + funds.amount / 100, 0)

    return {
      available,
      pending,
      currency: balance.available[0]?.currency || 'usd',
      availableBreakdown,
      pendingBreakdown,
      lastUpdated: new Date().toISOString(),
    }
  } catch (error) {
    console.error('Error fetching Stripe balance:', error)
    throw error
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  getStripeBalance()
    .then((result) => {
      console.log(JSON.stringify(result, null, 2))
    })
    .catch((error) => {
      console.error(JSON.stringify({ error: error.message }, null, 2))
      process.exit(1)
    })
}

export { getStripeBalance }
