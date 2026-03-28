'use client'

import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  CartesianGrid,
  Tooltip,
  Legend,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from 'recharts'
import { getPriceHistory, PriceHistoryPoint } from '@/lib/price-history'

const RETAILER_COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

interface PriceHistoryChartProps {
  paddleId: number
  days?: number
}

interface ChartDataPoint {
  date: string
  [key: string]: string | number | boolean | undefined
}

function transformForRecharts(points: PriceHistoryPoint[]): ChartDataPoint[] {
  const map = new Map<string, ChartDataPoint>()

  for (const point of points) {
    const existing = map.get(point.date) ?? { date: point.date }
    existing[`${point.retailer}_price`] = point.price
    existing[`${point.retailer}_is_good`] = point.is_good_time
    map.set(point.date, existing)
  }

  return Array.from(map.values()).sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  )
}

function extractRetailers(points: PriceHistoryPoint[]): string[] {
  return Array.from(new Set(points.map((p) => p.retailer)))
}

function hasAnyGoodTimeToBuy(points: PriceHistoryPoint[]): boolean {
  return points.some((p) => p.is_good_time)
}

export default function PriceHistoryChart({
  paddleId,
  days = 90,
}: PriceHistoryChartProps) {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<PriceHistoryPoint[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getPriceHistory(paddleId, days)
      .then((result) => {
        setData(result)
      })
      .catch(() => {
        setError('Erro ao carregar histórico de preços.')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [paddleId, days])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-500">
        Carregando histórico de preços...
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-32 text-red-500">
        {error}
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-400">
        Sem dados de preço disponíveis.
      </div>
    )
  }

  const chartData = transformForRecharts(data)
  const retailers = extractRetailers(data)
  const showGoodTimeBadge = hasAnyGoodTimeToBuy(data)

  return (
    <section className="mt-6">
      <div className="flex items-center gap-3 mb-4">
        <h2 className="text-xl font-semibold">Histórico de Preços ({days} dias)</h2>
        {showGoodTimeBadge && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Bom momento para comprar!
          </span>
        )}
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(val: string) => {
              const d = new Date(val)
              return `${d.getDate()}/${d.getMonth() + 1}`
            }}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={(val: number) => `R$${val}`}
            label={{
              value: 'Preço (R$)',
              angle: -90,
              position: 'insideLeft',
              offset: 10,
              style: { fontSize: 12 },
            }}
          />
          <Tooltip
            formatter={(value: number, name: string) => [
              `R$ ${value.toFixed(2)}`,
              name.replace('_price', ''),
            ]}
            labelFormatter={(label: string) => `Data: ${label}`}
          />
          <Legend
            formatter={(value: string) => value.replace('_price', '')}
          />
          {retailers.map((retailer, idx) => (
            <Line
              key={`${retailer}_price`}
              type="monotone"
              dataKey={`${retailer}_price`}
              stroke={RETAILER_COLORS[idx % RETAILER_COLORS.length]}
              name={`${retailer}_price`}
              dot={false}
              connectNulls
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </section>
  )
}
