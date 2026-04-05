export function DataStatsSection() {
  const stats = [
    { value: '147', label: 'raquetes analisadas' },
    { value: '3', label: 'varejistas monitorados' },
    { value: 'Diaria', label: 'atualizacao de precos' },
  ]

  return (
    <section className="hy-near-black-section hy-section">
      <div className="hy-container">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          {stats.map((stat) => (
            <div key={stat.label} className="p-6">
              <div className="hy-data" style={{
                fontSize: '2.5rem',
                fontWeight: 700,
                color: 'var(--data-green)',
                lineHeight: 1.1,
                marginBottom: '8px',
              }}>
                {stat.value}
              </div>
              <div style={{
                fontSize: 'var(--font-size-body)',
                color: 'var(--color-gray-300)',
                fontWeight: 500,
              }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
