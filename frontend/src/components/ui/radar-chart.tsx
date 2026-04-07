'use client'

import { cn } from '@/lib/utils'
import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

interface RadarDataPoint {
  attribute: string
  fullMark: number
  valueA: number
  valueB: number
}

interface RadarChartProps {
  data: RadarDataPoint[]
  className?: string
}

const CHART_COLORS = {
  paddleA: { fill: '#84CC16', fillOpacity: 0.3, stroke: '#84CC16' },
  paddleB: { fill: '#F97316', fillOpacity: 0.3, stroke: '#F97316' },
}

function RadarChart({ data, className }: RadarChartProps) {
  return (
    <div className={cn('w-full h-72', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid stroke="#525252" />
          <PolarAngleAxis
            dataKey="attribute"
            tick={{ fill: '#737373', fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 10]}
            tick={false}
            axisLine={false}
          />
          <Radar
            name="Paddle A"
            dataKey="valueA"
            stroke={CHART_COLORS.paddleA.stroke}
            fill={CHART_COLORS.paddleA.fill}
            fillOpacity={CHART_COLORS.paddleA.fillOpacity}
            dot={{ r: 3, fill: CHART_COLORS.paddleA.stroke }}
          />
          <Radar
            name="Paddle B"
            dataKey="valueB"
            stroke={CHART_COLORS.paddleB.stroke}
            fill={CHART_COLORS.paddleB.fill}
            fillOpacity={CHART_COLORS.paddleB.fillOpacity}
            dot={{ r: 3, fill: CHART_COLORS.paddleB.stroke }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#141414',
              border: '1px solid #262626',
              borderRadius: '8px',
              color: '#FAFAFA',
              fontSize: 12,
            }}
            itemStyle={{ color: '#FAFAFA' }}
          />
        </RechartsRadarChart>
      </ResponsiveContainer>
    </div>
  )
}

function RadarChartSkeleton() {
  return (
    <div className="w-full h-72 animate-shimmer rounded-rounded bg-elevated" />
  )
}

export { RadarChart, RadarChartSkeleton }
export type { RadarChartProps, RadarDataPoint }
