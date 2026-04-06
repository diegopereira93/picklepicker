export function DataStatsSection() {
  const stats = [
    { value: '147', label: 'raquetes analisadas' },
    { value: '3', label: 'varejistas monitorados' },
    { value: 'Diaria', label: 'atualizacao de precos' },
  ]

  return (
    <section className="bg-[#F5F2EB] py-16">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          {stats.map((stat) => (
            <div key={stat.label} className="p-6">
              <div style={{
                fontSize: '2.5rem',
                fontWeight: 700,
                color: '#4d8c00',
                lineHeight: 1.1,
                marginBottom: '8px',
                fontFamily: 'monospace',
              }}>
                {stat.value}
              </div>
              <div style={{
                fontSize: '1rem',
                color: '#2A2A2A',
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
