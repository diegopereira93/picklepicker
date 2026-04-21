'use client'

import { useState } from 'react'
import { Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PriceAlertModal } from '@/components/ui/price-alert-modal'

interface PriceAlertButtonProps {
  paddle: {
    id: number
    name: string
    brand: string
    price_brl?: number
    price_min_brl?: number
  }
}

export function PriceAlertButton({ paddle }: PriceAlertButtonProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <Button
        variant="ghost"
        className="text-text-secondary hover:bg-surface hover:text-text-primary"
        onClick={() => setIsOpen(true)}
      >
        <Bell size={16} className="mr-2" /> Alerta de Preço
      </Button>
      <PriceAlertModal
        paddle={paddle}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  )
}
