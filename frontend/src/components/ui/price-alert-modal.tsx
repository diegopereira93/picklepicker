"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

interface PriceAlertModalProps {
  paddle: {
    id: number
    name: string
    brand: string
    price_brl?: number
    price_min_brl?: number
  }
  isOpen: boolean
  onClose: () => void
}

export function PriceAlertModal({ paddle, isOpen, onClose }: PriceAlertModalProps) {
  const [email, setEmail] = useState("")
  const [targetPrice, setTargetPrice] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const payload = {
        paddle_id: paddle.id,
        email,
        price_target: targetPrice ? parseFloat(targetPrice) : undefined,
      }

      const response = await fetch("/api/price-alerts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (response.status === 401) {
        toast.error("Entre para criar alertas de preço.")
        onClose()
        return
      }

      if (!response.ok) {
        throw new Error("Failed to create alert")
      }

      toast.success("Alerta criado com sucesso!")
      onClose()
    } catch (error) {
      toast.error("Erro ao criar alerta. Tente novamente.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-surface rounded-xl border-border text-text-primary">
        <DialogHeader>
          <DialogTitle className="text-text-primary">Alerta de Preco</DialogTitle>
          <DialogDescription className="text-text-secondary">
            Receba uma notificacao quando o preco da {paddle.brand} {paddle.name} cair.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label htmlFor="email" className="text-sm font-medium text-text-primary">
              Email
            </label>
            <Input
              id="email"
              type="email"
              placeholder="seu@email.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-base border-border text-text-primary placeholder:text-text-muted"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="targetPrice" className="text-sm font-medium text-text-primary">
              Preco alvo (R$)
            </label>
            <Input
              id="targetPrice"
              type="number"
              step="0.01"
              min="0"
              placeholder="Ex: 450.00"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              className="bg-base border-border text-text-primary placeholder:text-text-muted"
            />
            {paddle.price_brl && (
              <p className="text-xs text-text-muted">
                Sugerido: {Math.round(paddle.price_brl * 0.9)} (10% abaixo do preco atual)
              </p>
            )}
          </div>

          <Button
            type="submit"
            disabled={isLoading || !email}
            className="bg-brand-primary hover:bg-brand-primary/90 text-base mt-2"
          >
            {isLoading ? "Criando..." : "Criar Alerta"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
