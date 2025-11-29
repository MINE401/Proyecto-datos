import React, { useState, useEffect } from 'react'
import { fetchIndustrySectors } from '../services/supabase'

export default function SearchForm({ onSearch }) {
  const [country, setCountry] = useState('')
  const [region, setRegion] = useState('')
  const [city, setCity] = useState('')
  const [clientName, setClientName] = useState('')
  const [industry, setIndustry] = useState('')
  const [industryOptions, setIndustryOptions] = useState([])
  const [loadingIndustries, setLoadingIndustries] = useState(false)

  useEffect(() => {
    let mounted = true
    async function loadIndustries() {
      setLoadingIndustries(true)
      try {
        const sectors = await fetchIndustrySectors()
        if (mounted) setIndustryOptions(sectors)
      } catch (e) {
        console.warn('No se pudieron cargar industrias:', e.message)
      } finally {
        if (mounted) setLoadingIndustries(false)
      }
    }
    loadIndustries()
    return () => { mounted = false }
  }, [])
  const [segment, setSegment] = useState('')
  const [limit, setLimit] = useState(50)

  function submit(e) {
    e.preventDefault()
    const territory = {}
    if (country) territory.country = country
    if (region) territory.region = region
    if (city) territory.city = city
    
    const params = {}
    if (Object.keys(territory).length) params.territory = territory
    if (clientName) params.clientName = clientName
    if (industry) params.industry = industry
    if (segment) params.segment = segment
    
    onSearch({ params, pagination: { limit: Number(limit), offset: 0 } })
  }

  function reset() {
    setCountry('')
    setRegion('')
    setCity('')
    setClientName('')
    setIndustry('')
    setSegment('')
    setLimit(50)
  }

  return (
    <form onSubmit={submit}>
      <div>
        <label>País:</label>
        <input
          type="text"
          placeholder="ej: Argentina"
          value={country}
          onChange={e => setCountry(e.target.value)}
        />
      </div>
      
      <div>
        <label>Región:</label>
        <input
          type="text"
          placeholder="ej: EMEA, LATAM"
          value={region}
          onChange={e => setRegion(e.target.value)}
        />
      </div>
      
      <div>
        <label>Ciudad:</label>
        <input
          type="text"
          placeholder="ej: Buenos Aires"
          value={city}
          onChange={e => setCity(e.target.value)}
        />
      </div>
      
      <div>
        <label>Nombre/Cliente:</label>
        <input
          type="text"
          placeholder="ej: Acme"
          value={clientName}
          onChange={e => setClientName(e.target.value)}
        />
      </div>
      
      <div>
        <label>Industria:</label>
        <select value={industry} onChange={e => setIndustry(e.target.value)}>
          <option value="">-- Todas --</option>
          {industryOptions.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
        {loadingIndustries && <span style={{ fontSize:12, color:'#666' }}> Cargando…</span>}
      </div>
      
      <div>
        <label>Segmento:</label>
        <select value={segment} onChange={e => setSegment(e.target.value)}>
          <option value="">-- Todos --</option>
          <option value="Enterprise">Enterprise</option>
          <option value="MidMarket">Mid Market</option>
          <option value="Territory">Territory</option>
        </select>
      </div>
      
      <div>
        <label>Límite:</label>
        <input
          type="number"
          value={limit}
          onChange={e => setLimit(e.target.value)}
          min="1"
          max="500"
        />
      </div>
      
      <div>
        <button type="submit">🔍 Buscar</button>
        <button type="button" className="secondary" onClick={reset}>Limpiar</button>
      </div>
    </form>
  )
}
