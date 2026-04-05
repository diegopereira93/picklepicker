'use client'

import { FC } from 'react'

interface SelectionBarProps {
  count: number
  onCompare: () => void
  onClear: () => void
}

export const SelectionBar: FC<SelectionBarProps> = ({
  count,
  onCompare,
  onClear,
}) => {
  if (count === 0) return null

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-50"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 50,
      }}
    >
      <div
        className="flex items-center justify-between px-6 py-3"
        style={{
          backgroundColor: 'var(--color-near-black)',
          borderTop: '2px solid var(--sport-primary)',
        }}
      >
        <span
          className="text-sm font-medium"
          style={{ color: 'var(--color-white)' }}
        >
          {count} raquete{count !== 1 ? 's' : ''} selecionada{count !== 1 ? 's' : ''}
        </span>

        <div className="flex items-center">
          <button
            className="text-sm underline"
            onClick={onClear}
            type="button"
            style={{
              color: 'var(--color-gray-300)',
              cursor: 'pointer',
              textDecoration: 'underline',
            }}
          >
            Limpar
          </button>

          <button
            className="hy-button hy-button-cta px-6 py-2 text-sm ml-4"
            onClick={onCompare}
            type="button"
          >
            Comparar
          </button>
        </div>
      </div>
    </div>
  )
}
