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
          const score = company.score ?? company.partner_score ?? Math.random() * 100
          const displayScore = typeof score === 'number' ? score.toFixed(1) : 'N/A'
          return (
            <div key={company.id || company.name || idx} className="card" onClick={() => onSelect(company)}>
              <div className="card-header">
                <div className="card-title">{company.name || 'Sin nombre'}</div>
                <div className="card-score">{displayScore}</div>
              </div>
              <ScoreBar score={parseFloat(displayScore)} max={100} />
              
              {company.territory && (
                <span className="badge territory">
                  📍 {company.territory.country || company.territory.city || 'Global'}
                </span>
              )}
              {company.industry && (
                <span className="badge industry">
                  🏭 {company.industry}
                </span>
              )}
              {company.segment && (
                <span className="badge segment">
                  👥 {company.segment}
                </span>
              )}
              
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
