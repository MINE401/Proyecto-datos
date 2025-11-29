import React from 'react'

export default function CompanyDetail({ company, onBack }) {
  const score = company.score ?? company.partner_score ?? 0
  const displayScore = typeof score === 'number' ? score.toFixed(1) : 'N/A'
  
  // Score breakdown mock: si existe "score_breakdown" en los datos, lo mostramos
  const breakdown = company.score_breakdown || {
    'Foco de Industria': company.industry_focus ?? 7.5,
    'Relacionamiento': company.relationship ?? 6.0,
    'Histórico de Ventas': company.sales_history ?? 5.0,
    'Certificaciones': company.certifications ?? 8.0
  }
  
  return (
    <div className="detail-page">
      <button className="secondary" onClick={onBack}>← Volver a resultados</button>
      
      <h2>{company.name || 'Partner sin nombre'}</h2>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <div style={{ fontSize: 48, fontWeight: 'bold', color: '#0066cc' }}>
          {displayScore}
        </div>
        <div>
          <div style={{ fontSize: 14, color: '#999' }}>Partner Score</div>
          <div style={{ fontSize: 12, color: '#666' }}>Puntuación compuesta</div>
        </div>
      </div>

      <div className="score-bar" style={{ height: 12, marginBottom: 24 }}>
        <div className="score-fill" style={{ width: `${(parseFloat(displayScore) / 100) * 100}%` }}></div>
      </div>

      <h3 style={{ marginTop: 24, marginBottom: 16 }}>📊 Desglose del Score</h3>
      <div className="score-breakdown">
        {Object.entries(breakdown).map(([label, value]) => {
          const numValue = typeof value === 'number' ? value : 0
          return (
            <div key={label} className="score-item">
              <div className="score-item-label">{label}</div>
              <div className="score-item-value">{numValue.toFixed(1)}</div>
              <div className="score-item-max">de 10.0</div>
              <div className="score-bar" style={{ marginTop: 8 }}>
                <div className="score-fill" style={{ width: `${(numValue / 10) * 100}%` }}></div>
              </div>
            </div>
          )
        })}
      </div>

      <h3 style={{ marginTop: 24, marginBottom: 8 }}>ℹ️ Información General</h3>
      <div className="meta-info">
        <div className="meta-item">
          <div className="meta-label">País</div>
          <div className="meta-value">{company.territory?.country || company.country || 'N/A'}</div>
        </div>
        <div className="meta-item">
          <div className="meta-label">Región</div>
          <div className="meta-value">{company.territory?.global_region || company.territory?.region || company.region || 'N/A'}</div>
        </div>
        <div className="meta-item">
          <div className="meta-label">Ciudad</div>
          <div className="meta-value">{company.territory?.city || company.city || 'N/A'}</div>
        </div>
        <div className="meta-item">
          <div className="meta-label">Industria</div>
          <div className="meta-value">{company.industry || 'N/A'}</div>
        </div>
        <div className="meta-item">
          <div className="meta-label">Segmento</div>
          <div className="meta-value">{company.segment || 'N/A'}</div>
        </div>
        <div className="meta-item">
          <div className="meta-label">Estado</div>
          <div className="meta-value">{company.status || 'Activo'}</div>
        </div>
      </div>

      <h3 style={{ marginTop: 8, marginBottom: 12 }}>🏭 Industrias</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {(company.industry_details || []).map(det => (
          <span key={det} className="badge industry" style={{ marginTop: 0 }}>{det}</span>
        ))}
        {(company.industry_details || []).length === 0 && <span style={{ fontSize: 12, color: '#999' }}>Sin datos</span>}
      </div>

      <h3 style={{ marginTop: 20, marginBottom: 12 }}>👥 Clasificaciones / Segmentos</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {(company.classifications || []).map(cls => (
          <span key={cls} className="badge segment" style={{ marginTop: 0 }}>{cls}</span>
        ))}
        {(company.classifications || []).length === 0 && <span style={{ fontSize: 12, color: '#999' }}>Sin datos</span>}
      </div>

      <h3 style={{ marginTop: 24, marginBottom: 16 }}>📝 Datos Completos</h3>
      <pre style={{
        background: '#f5f5f5',
        padding: 16,
        borderRadius: 8,
        fontSize: 12,
        overflowX: 'auto',
        maxHeight: 300
      }}>
        {JSON.stringify(company, null, 2)}
      </pre>

      <button className="secondary" onClick={onBack} style={{ marginTop: 20 }}>← Volver a resultados</button>
    </div>
  )
}
