'use client';

import { Paddle } from '@/types/paddle';
import { SafeImage } from '@/components/ui/safe-image';

interface SidebarProductCardProps {
  paddle: Paddle;
  score?: number;
  affiliateUrl?: string;
}

export function SidebarProductCard({ paddle, score, affiliateUrl }: SidebarProductCardProps) {
  const formatPrice = (price: number | null | undefined) => {
    if (price == null) return '';
    return price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Recomendada';
    if (score >= 0.5) return 'Boa opcao';
    return 'Considere';
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'var(--data-green)';
    if (score >= 0.5) return '#FDE047';
    return '#B91C1C';
  };

  const formatSpec = (value: number | string | null | undefined) => {
    if (value == null || value === '') return '—';
    return String(value);
  };

  const scoreColor = score != null ? getScoreColor(score) : null
  const scoreLabel = score != null ? getScoreLabel(score) : null

  return (
    <div className="flex flex-col" style={{ height: '100%' }}>
      <div
        className="flex items-center justify-center overflow-hidden"
        style={{ height: '180px', borderBottom: '1px solid var(--color-gray-border)', backgroundColor: 'var(--color-gray-border)' }}
      >
        {paddle.image_url ? (
          <SafeImage
            src={paddle.image_url}
            alt={paddle.name}
            width={300}
            height={180}
            className="object-contain max-w-full max-h-full"
          />
        ) : (
          <div className="flex items-center justify-center" style={{ color: 'var(--color-gray-500)', fontSize: 'var(--font-size-caption)' }}>
            Foto
          </div>
        )}
      </div>

      <div className="px-4 pt-3">
        <p
          style={{ fontFamily: 'var(--font-body)', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--data-green)' }}
        >
          {paddle.brand}
        </p>

        <h3
          style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '20px', lineHeight: 'var(--line-height-snug)', color: 'var(--color-black)', marginTop: '4px' }}
        >
          {paddle.name}
        </h3>

        <div
          style={{ fontFamily: 'var(--font-data)', fontSize: '20px', fontWeight: 700, color: 'var(--data-green)', marginTop: '8px' }}
        >
          {formatPrice(paddle.price_min_brl)}
        </div>
      </div>

      {paddle.specs && (
        <div
          className="grid px-4 py-3"
          style={{
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '8px',
            borderTop: '1px solid var(--color-gray-border)',
            borderBottom: '1px solid var(--color-gray-border)',
          }}
        >
          {paddle.specs.weight_oz != null && (
            <div>
              <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-gray-500)', marginBottom: '4px' }}>Peso</div>
              <div style={{ fontFamily: 'var(--font-data)', fontSize: '14px', color: 'var(--color-black)' }}>{paddle.specs.weight_oz}oz</div>
            </div>
          )}
          {paddle.specs.face_material && (
            <div>
              <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-gray-500)', marginBottom: '4px' }}>Face</div>
              <div style={{ fontSize: '14px', color: 'var(--color-black)' }}>{paddle.specs.face_material}</div>
            </div>
          )}
          {paddle.specs.core_thickness_mm != null && (
            <div>
              <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-gray-500)', marginBottom: '4px' }}>Core</div>
              <div style={{ fontFamily: 'var(--font-data)', fontSize: '14px', color: 'var(--color-black)' }}>{paddle.specs.core_thickness_mm}mm</div>
            </div>
          )}
        </div>
      )}

      {score != null && score > 0 && (
        <div className="px-4 pt-3">
          <div
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-sm"
            style={{
              backgroundColor: scoreColor,
              color: scoreColor === '#FDE047' ? 'var(--color-black)' : 'var(--color-white)',
              fontSize: 'var(--font-size-caption)',
              fontWeight: 700,
            }}
          >
            {scoreLabel}
            <span style={{ fontFamily: 'var(--font-data)', opacity: 0.8 }}>
              {Math.round(score * 100)}%
            </span>
          </div>
        </div>
      )}

      <div className="mt-auto pt-3">
        {affiliateUrl && (
          <a
            href={affiliateUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="hy-button hy-button-cta w-full text-center py-3 text-base inline-block"
          >
            Comprar na loja →
          </a>
        )}
      </div>
    </div>
  );
}
