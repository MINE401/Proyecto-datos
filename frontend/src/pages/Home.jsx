import React, { useState } from 'react'
import SearchForm from '../components/SearchForm'
import CompanyList from '../components/CompanyList'
import { query } from '../api/client'
import CompanyDetail from './CompanyDetail'

export default function Home() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [totalResults, setTotalResults] = useState(0)

  async function handleSearch({ params = {}, pagination = {} }) {
    setLoading(true)
    setError(null)
    setSelected(null)
    try {
      // Determinar la acción según si hay filtros
      const hasFilters = Object.keys(params).some(k => {
        const v = params[k]
        return v && (typeof v !== 'object' || Object.keys(v).length > 0)
      })
      
      const action = hasFilters ? 'search_company' : 'list_companies'
      const res = await query(action, params, pagination)
      
      // Adaptarse a diferentes formatos de respuesta
      let companiesList = []
      let count = 0
      
      if (Array.isArray(res)) {
        companiesList = res
        count = res.length
      } else if (res.results) {
        companiesList = res.results
        count = res.total || res.results.length
      } else if (res.items) {
        companiesList = res.items
        count = res.count || res.items.length
      } else if (res.data) {
        companiesList = Array.isArray(res.data) ? res.data : [res.data]
        count = companiesList.length
      }
      
      setCompanies(companiesList)
      setTotalResults(count)
    } catch (err) {
      setError(err.message || 'Error al conectar con el servidor')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header style={{ marginBottom: 32 }}>
        <h1>🤝 Partner Finder</h1>
        <p style={{ color: '#666', fontSize: 14 }}>
          Encuentra los partners ideales para tu estrategia comercial
        </p>
      </header>

      {!selected ? (
        <>
          <SearchForm onSearch={handleSearch} />
          
          {loading && <div className="message loading">⏳ Buscando partners...</div>}
          {error && <div className="message error">❌ Error: {error}</div>}
          
          {!loading && companies.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <CompanyList companies={companies} onSelect={setSelected} />
            </div>
          )}
          
          {!loading && !error && companies.length === 0 && totalResults === 0 && (
            <div className="message">
              👋 Comienza una búsqueda llenando los filtros arriba
            </div>
          )}
        </>
      ) : (
        <CompanyDetail company={selected} onBack={() => setSelected(null)} />
      )}
    </div>
  )
}
