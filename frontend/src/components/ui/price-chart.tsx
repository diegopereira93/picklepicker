'use client'

import { cn } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

interface PricePoint {
  date: string
  price: number
}

interface PriceChartProps {
  data: PricePoint[]
  variant: 'sparkline' | 'full'
  currentPrice?: number
  className?: string
}

function PriceChart({ data, variant, currentPrice, className }: PriceChartProps) {
  const formatCurrency = (value: number) => `R$${value.toFixed(0)}`

  if (variant === 'sparkline') {
    return (
      <div className={cn('w-24 h-12', className)}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <Line type="monotone" dataKey="price" stroke="#84CC16" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return (
    <div className={cn('w-full h-64', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <XAxis
            dataKey="date"
            stroke="#525252"
            tick={{ fill: '#737373', fontSize: 12 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#525252"
            tick={{ fill: '#737373', fontSize: 12, fontFamily: 'var(--font-mono)' }}
            tickFormatter={formatCurrency}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#141414',
              border: '1px solid #1f1f1f',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#FAFAFA', fontFamily: 'var(--font-mono)', fontSize: 12 }}
            formatter={(value: number) => [`R$ ${value.toFixed(2)}`, 'Price']}
          />
          {currentPrice && (
            <ReferenceLine
              y={currentPrice}
              stroke="#84CC16"
              strokeDasharray="5 5"
              label={{ value: 'Current', fill: '#84CC16', fontSize: 12, position: 'right' }}
            />
          )}
          <Line
            type="monotone"
            dataKey="price"
            stroke="#84CC16"
            strokeWidth={3}
            dot={{ fill: '#84CC16', r: 4, strokeWidth: 0 }}
            activeDot={{ r: 6, fill: '#F97316', stroke: '#141414', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function PriceChartSkeleton({ variant }: { variant: 'sparkline' | 'full' }) {
  return (
    <div
      className={cn(
        'animate-shimmer rounded-rounded bg-gradient-to-r from-surface via-elevated to-surface bg-[length:200%_100%]',
        variant === 'sparkline' ? 'w-24 h-12' : 'w-full h-64'
      )}
    />
  )
}

export { PriceChart, PriceChartSkeleton }
export type { PriceChartProps, PricePoint }
