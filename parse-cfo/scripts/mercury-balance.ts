#!/usr/bin/env tsx
/**
 * Mercury Balance Check
 * Queries Mercury API for current account balance and recent activity
 *
 * Usage:
 *   MERCURY_API_KEY=... npx tsx mercury-balance.ts
 *
 * Environment Variables:
 *   MERCURY_API_KEY - Mercury API key (required)
 *
 * Output: JSON with balance details and recent transactions
 */

interface MercuryBalanceResult {
  currentBalance: number
  pendingBalance: number
  currency: string
  accountNumberLast4: string
  routingNumber: string
  lastUpdated: string
}

interface MercuryTransaction {
  id: string
  date: string
  description: string
  amount: number
  type: 'debit' | 'credit'
  status: string
}

interface MercuryAccountResult extends MercuryBalanceResult {
  recentTransactions: MercuryTransaction[]
  pendingDeposits: number
  stripePayoutsPending: number
}

/**
 * Fetch Mercury account balance
 * Note: Mercury API key must have read access
 */
async function getMercuryBalance(apiKey: string): Promise<MercuryAccountResult> {
  const baseUrl = 'https://backend.mercury.com/api/v1'

  const headers = {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  }

  try {
    // Fetch account details
    const accountRes = await fetch(`${baseUrl}/accounts`, { headers })
    if (!accountRes.ok) {
      throw new Error(`Mercury API error: ${accountRes.status}`)
    }
    const accountsData = await accountRes.json()

    // Get the primary checking account
    const checkingAccount = accountsData.accounts?.find(
      (a: any) => a.accountType === 'checking'
    )

    if (!checkingAccount) {
      throw new Error('No checking account found')
    }

    const currentBalance = checkingAccount.availableBalance / 100
    const pendingBalance = checkingAccount.currentBalance / 100 - currentBalance

    // Fetch recent transactions
    const txRes = await fetch(`${baseUrl}/transactions?limit=50`, { headers })
    const txData = await txRes.json()

    const recentTransactions: MercuryTransaction[] = (txData.transactions || [])
      .slice(0, 10)
      .map((tx: any) => ({
        id: tx.id,
        date: tx.createdAt || tx.postedAt,
        description: tx.description || tx.counterpartyName || tx.merchantName || 'Unknown',
        amount: Math.abs(tx.amount / 100),
        type: tx.amount < 0 ? 'debit' : 'credit',
        status: tx.status,
      }))

    // Count pending deposits (likely Stripe payouts)
    const pendingDeposits = recentTransactions.filter(
      (tx) => tx.type === 'credit' && tx.status === 'pending'
    ).length

    // Identify Stripe payouts by description
    const stripePayoutsPending = recentTransactions.filter(
      (tx) => tx.description.toLowerCase().includes('stripe') && tx.status === 'pending'
    ).length

    return {
      currentBalance,
      pendingBalance,
      currency: 'USD',
      accountNumberLast4: checkingAccount.accountNumber.slice(-4),
      routingNumber: '121145433', // Parse's Mercury routing
      lastUpdated: new Date().toISOString(),
      recentTransactions,
      pendingDeposits,
      stripePayoutsPending,
    }
  } catch (error) {
    console.error('Error fetching Mercury balance:', error)
    throw error
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const apiKey = process.env.MERCURY_API_KEY

  if (!apiKey) {
    console.error(JSON.stringify({ error: 'MERCURY_API_KEY environment variable required' }, null, 2))
    process.exit(1)
  }

  getMercuryBalance(apiKey)
    .then((result) => {
      console.log(JSON.stringify(result, null, 2))
    })
    .catch((error) => {
      console.error(JSON.stringify({ error: error.message }, null, 2))
      process.exit(1)
    })
}

export { getMercuryBalance }
