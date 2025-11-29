import React from 'react'

function ScoreBar({ score, max = 100 }) {
  const percentage = (score / max) * 100
  return (
    <div className="score-bar">
      <div className="score-fill" style={{ width: `${percentage}%` }}></div>
    </div>
  )
}

export default function CompanyList({ companies, onSelect }) {
  if (!companies || companies.length === 0) {
    return <div className="empty">No hay resultados. Intenta ajustar los filtros.</div>
  }
  
  return (
    <div>
      <p style={{ marginBottom: 16, color: '#666' }}>
        Se encontraron <strong>{companies.length}</strong> partner(s)
      </p>
      <div className="results">
        {companies.map((company, idx) => {
          const rawScore = company.partner_score ?? company.score ?? Math.random() * 100
          const displayScore = typeof rawScore === 'number' ? rawScore.toFixed(1) : 'N/A'
          const industries = company.industry_details || []
          const classifications = company.classifications || []
          const territory = company.territory || {}
          return (
            <div key={company.id || company.name || idx} className="card" onClick={() => onSelect(company)}>
              <div className="card-header">
                <div className="card-title">{company.name || 'Sin nombre'}</div>
                <div className="card-score">{displayScore}</div>
              </div>
              <ScoreBar score={parseFloat(displayScore)} max={100} />

              <div className="badges-group">
                {territory.country || territory.city ? (
                  <span className="badge territory" title={`${territory.city || ''} ${territory.state || ''}`.trim()}>
                    📍 {territory.city ? `${territory.city}, ${territory.country || ''}` : territory.country || 'Global'}
                  </span>
                ) : null}

                {industries.slice(0,2).map(ind => (
                  <span key={ind} className="badge industry" title={ind}>🏭 {ind.length > 28 ? ind.slice(0,25)+'…' : ind}</span>
                ))}
                {industries.length > 2 && (
                  <span className="badge industry" title={industries.join(' | ')}>+{industries.length - 2} ind.</span>
                )}

                {classifications.slice(0,2).map(cls => (
                  <span key={cls} className="badge segment" title={cls}>👥 {cls.length > 26 ? cls.slice(0,23)+'…' : cls}</span>
                ))}
                {classifications.length > 2 && (
                  <span className="badge segment" title={classifications.join(' | ')}>+{classifications.length - 2} seg.</span>
                )}
              </div>

              <div style={{ marginTop: 12, fontSize: 12, color: '#999' }}>
                Haz clic para ver detalles
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
