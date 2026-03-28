export interface PriceHistoryPoint {
  retailer: string
  date: string
  price: number
  p20: number
  is_good_time: boolean
}

/**
 * Calculate 20th percentile of price array
 * @param prices Array of prices (unsorted)
 * @returns P20 value
 */
export function percentile20(prices: number[]): number {
  if (prices.length === 0) return 0
  const sorted = [...prices].sort((a, b) => a - b)
  const idx = Math.floor(sorted.length * 0.2)
  return sorted[idx] ?? sorted[sorted.length - 1]
}

/**
 * Check if current price is a good time to buy
 * @param price Current price
 * @param p20 20th percentile (threshold)
 * @returns true if price <= p20
 */
export function isGoodTimeToBuy(price: number, p20: number): boolean {
  return price <= p20
}

/**
 * Fetch price history for a paddle from the API
 * @param paddleId Paddle product ID
 * @param days Number of days to fetch (default 90)
 * @returns Array of price history points
 */
export async function getPriceHistory(
  paddleId: number,
  days: number = 90
): Promise<PriceHistoryPoint[]> {
  try {
    const res = await fetch(`/api/paddles/${paddleId}/price-history?days=${days}`)
    if (!res.ok) return []
    return res.json()
  } catch (error) {
    console.error('Failed to fetch price history:', error)
    return []
  }
}
