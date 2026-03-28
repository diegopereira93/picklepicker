'use client'

import React, { useState } from 'react'
import type { Paddle } from '@/types/paddle'

interface CatalogTableProps {
  paddles: Paddle[]
  onUpdate: (id: number, data: Partial<Paddle>) => Promise<void>
}

function SpecsStatus({ specs }: { specs: Paddle['specs'] }) {
  if (!specs) {
    return <span className="text-red-500 font-semibold text-xs" title="Sem specs">&#10007; Sem specs</span>
  }
  const fields = [specs.swingweight, specs.twistweight, specs.weight_oz, specs.face_material, specs.core_thickness_mm]
  const filled = fields.filter((f) => f !== undefined && f !== null).length
  const total = fields.length
  if (filled === total) {
    return <span className="text-green-600 font-semibold text-xs" title="Completo">&#10003; Completo</span>
  }
  return (
    <span className="text-yellow-600 font-semibold text-xs" title={`${filled}/${total} campos`}>
      ~ Parcial ({filled}/{total})
    </span>
  )
}

interface EditableRowProps {
  paddle: Paddle
  onUpdate: (id: number, data: Partial<Paddle>) => Promise<void>
}

function EditableRow({ paddle, onUpdate }: EditableRowProps) {
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState(paddle.name)
  const [brand, setBrand] = useState(paddle.brand)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    await onUpdate(paddle.id, { name, brand })
    setSaving(false)
    setSaved(true)
    setEditing(false)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <tr className="border-b hover:bg-muted/30 transition-colors">
      <td className="px-3 py-2 text-xs text-muted-foreground">{paddle.id}</td>
      <td className="px-3 py-2">
        {editing ? (
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border rounded px-2 py-1 text-sm w-full"
          />
        ) : (
          <span className="text-sm">{paddle.name}</span>
        )}
      </td>
      <td className="px-3 py-2">
        {editing ? (
          <input
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            className="border rounded px-2 py-1 text-sm w-full"
          />
        ) : (
          <span className="text-sm">{paddle.brand}</span>
        )}
      </td>
      <td className="px-3 py-2 text-sm">
        {paddle.price_min_brl ? `R$ ${paddle.price_min_brl.toFixed(2)}` : '—'}
      </td>
      <td className="px-3 py-2">
        <SpecsStatus specs={paddle.specs} />
      </td>
      <td className="px-3 py-2">
        {editing ? (
          <div className="flex gap-1">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-2 py-1 text-xs bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50"
            >
              {saving ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={() => { setEditing(false); setName(paddle.name); setBrand(paddle.brand) }}
              className="px-2 py-1 text-xs border rounded hover:bg-muted"
            >
              Cancelar
            </button>
          </div>
        ) : (
          <button
            onClick={() => setEditing(true)}
            className="px-2 py-1 text-xs border rounded hover:bg-muted"
          >
            {saved ? '✓ Salvo' : 'Editar'}
          </button>
        )}
      </td>
    </tr>
  )
}

export function CatalogTable({ paddles, onUpdate }: CatalogTableProps) {
  const [search, setSearch] = useState('')

  const filtered = paddles.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.brand.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-3">
      <input
        type="search"
        placeholder="Buscar por nome ou marca..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-xs border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      />

      <div className="overflow-x-auto border rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 border-b">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-semibold text-muted-foreground">ID</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-muted-foreground">Nome</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-muted-foreground">Marca</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-muted-foreground">Preço</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-muted-foreground">Specs</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-muted-foreground">Ações</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-8 text-center text-sm text-muted-foreground">
                  Nenhuma raquete encontrada
                </td>
              </tr>
            ) : (
              filtered.map((paddle) => (
                <EditableRow key={paddle.id} paddle={paddle} onUpdate={onUpdate} />
              ))
            )}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-muted-foreground">
        {filtered.length} de {paddles.length} raquetes
      </p>
    </div>
  )
}
