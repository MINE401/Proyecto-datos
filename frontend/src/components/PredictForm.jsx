import React, { useState } from 'react'

const bandsRevenue = ["<$100K","$100K-$1M","$1M-$10M",">$10M"]
const bandsEmployees = ["1-10","11-50","51-200","200+"]
const bandsYears = ["<1","1-3","3-5","5+"]
const regions = ["Americas","EMEA","APJ","LATAM","North America","Asia"]
const clouds = ["Iaas","Paas","Saas"]
const techScopes = ["Cloud","Data","AI","Security","DevOps"]
const classifications = [
  "Independent Software Vendor (ISV)",
  "Global System Integrator (GSI)",
  "Regional System Integrator (RSI)",
  "Cloud Service Provider (CSP)",
]

export default function PredictForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    company_id: '',
    revenue_band: '',
    employee_band: '',
    years_in_business_band: '',
    global_region: '',
    industry_detail_customer: '',
    cloud_coverage: '',
    technology_scope: '',
    partner_classification: ''
  })

  function update(field, value) {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  function submit(e) {
    e.preventDefault()
    const payload = {
      ...form,
      company_id: form.company_id ? Number(form.company_id) : undefined
    }
    onSubmit(payload)
  }

  function reset() {
    setForm({
      company_id: '', revenue_band: '', employee_band: '', years_in_business_band: '',
      global_region: '', industry_detail_customer: '', cloud_coverage: '', technology_scope: '',
      partner_classification: ''
    })
  }

  return (
    <form onSubmit={submit} style={{ marginTop: 16 }}>
      <div>
        <label>ID Compañía:</label>
        <input type="number" value={form.company_id} onChange={e=>update('company_id', e.target.value)} placeholder="ej: 12345" />
      </div>
      <div>
        <label>Revenue Band:</label>
        <select value={form.revenue_band} onChange={e=>update('revenue_band', e.target.value)}>
          <option value="">-- Selecciona --</option>
          {bandsRevenue.map(o=> <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
      <div>
        <label>Employee Band:</label>
        <select value={form.employee_band} onChange={e=>update('employee_band', e.target.value)}>
          <option value="">-- Selecciona --</option>
          {bandsEmployees.map(o=> <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
      <div>
        <label>Years in Business:</label>
        <select value={form.years_in_business_band} onChange={e=>update('years_in_business_band', e.target.value)}>
          <option value="">-- Selecciona --</option>
          {bandsYears.map(o=> <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
      <div>
        <label>Global Region:</label>
        <select value={form.global_region} onChange={e=>update('global_region', e.target.value)}>
          <option value="">-- Selecciona --</option>
          {regions.map(o=> <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
      <div>
        <label>Industry Detail (Customer):</label>
        <input type="text" value={form.industry_detail_customer} onChange={e=>update('industry_detail_customer', e.target.value)} placeholder="ej: B123" />
      </div>
      <div>
        <label>Cloud Coverage:</label>
        <select value={form.cloud_coverage} onChange={e=>update('cloud_coverage', e.target.value)}>
          <option value="">-- Selecciona --</option>
          {clouds.map(o=> <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
      <div>
        <label>Technology Scope:</label>
        <select value={form.technology_scope} onChange={e=>update('technology_scope', e.target.value)}>
          <option value="">-- Selecciona --</option>
          {techScopes.map(o=> <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
      <div>
        <label>Partner Classification:</label>
        <select value={form.partner_classification} onChange={e=>update('partner_classification', e.target.value)}>
          <option value="">-- Selecciona --</option>
          {classifications.map(o=> <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
      <div>
        <button type="submit" disabled={loading}>⚙️ Calcular score</button>
        <button type="button" className="secondary" onClick={reset} disabled={loading}>Limpiar</button>
      </div>
    </form>
  )
}
