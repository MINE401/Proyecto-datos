import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = (SUPABASE_URL && SUPABASE_ANON_KEY)
  ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  : null

/**
 * Fetch companies from a Supabase table (assumes a `company` table exists).
 * Applies simple pagination (range) and returns { data, error }.
 */

if (supabase) {
  supabase
    .from('company')
    .select('*')
    .limit(1)
    .then(({ data, error }) => {
      if (error) {
        console.error('Supabase error:', error);
      } else {
        console.log('Supabase test data:', data);
      }
    });
}

export async function fetchCompaniesFromSupabase({ table = 'company', filters = {}, pagination = { limit: 50, offset: 0 } } = {}) {
  if (!supabase) throw new Error('Supabase no está configurado. Configure VITE_SUPABASE_URL y VITE_SUPABASE_ANON_KEY')

  const limit = pagination.limit || 50
  const offset = pagination.offset || 0

  // Selección con joins a tablas relacionadas para permitir filtros ricos
  // Usar embedded resources explícitas con !inner para habilitar filtros por foreignTable
  // Construir select dinámico: si se filtra por industria usar inner join para excluir compañías sin industria
  const industryJoin = filters.industry
    ? 'company_industry!inner( industry_master!inner(sector,detail) )'
    : 'company_industry( industry_master(sector,detail) )'

  let builder = supabase
    .from(table)
    .select(`
      id,
      name,
      website,
      employee_band,
      revenue_band,
      company_location!inner(
        address_type,
        location_master!inner(city,country,region,global_region,state)
      ),
      ${industryJoin},
      partner_classification(classification),
      score(relevance,partner_classification)
    `)
  
  // Debug: log configuración inicial de selección
  console.log('[Supabase] select config: company + joins to location, industry, classification, score')

  // Aplicar filtros simples si existen (territory.country, industry, segment, clientName)
  // Nombre del cliente / compañía (prueba múltiples columnas posibles)
  if (filters.clientName) {
    const v = filters.clientName
    builder = builder.or([
      `name.ilike.%${v}%`
    ].join(','))
    console.log('[Supabase] filter name.ilike', v)
  }

  // Industria (prueba múltiples columnas posibles)
  if (filters.industry) {
    const v = filters.industry
    builder = builder.eq('company_industry.industry_master.sector', v)
    console.log('[Supabase] filter industry_master.sector (inner join aplicado)', v)
  }

  // Segmento (Enterprise, MidMarket, Territory) — múltiples columnas posibles
  if (filters.segment) {
    const v = filters.segment
    // Asumimos segmento en partner_classification.classification
    builder = builder.eq('partner_classification.classification', v)
    console.log('[Supabase] filter partner_classification.classification', v)
  }

  // Territorio: país / región / ciudad — probar nombres alternativos
  if (filters.territory) {
    const t = filters.territory
    // Usar filtros con foreignTable para evitar errores de lógica en PostgREST
    if (t.country) {
      builder = builder.eq('company_location.location_master.country', t.country)
      console.log('[Supabase] filter company_location.location_master.country', t.country)
    }
    if (t.region) {
      builder = builder.eq('company_location.location_master.global_region', t.region)
      console.log('[Supabase] filter company_location.location_master.global_region', t.region)
    }
    if (t.city) {
      builder = builder.eq('company_location.location_master.city', t.city)
      console.log('[Supabase] filter company_location.location_master.city', t.city)
    }
  }

  const from = offset
  const to = offset + limit - 1
  const { data, error } = await builder.range(from, to)
  if (error) {
    return { data: null, error }
  }

  // Normalizar estructura para que el UI pueda mostrar país, región, ciudad, industria y segmento.
  const normalized = (data || []).map(c => {
    const firstLocation = Array.isArray(c.company_location) && c.company_location.length > 0 ? c.company_location[0] : null
    const locMaster = firstLocation?.location_master || {}
    const industries = Array.isArray(c.company_industry)
      ? c.company_industry.map(i => i?.industry_master?.sector).filter(Boolean)
      : []
    const industryDetails = Array.isArray(c.company_industry)
      ? c.company_industry.map(i => i?.industry_master?.detail).filter(Boolean)
      : []
    const classifications = Array.isArray(c.partner_classification)
      ? c.partner_classification.map(pc => pc?.classification).filter(Boolean)
      : []
    // Derivar un score simple si existe arreglo score con relevance
    let partner_score = c.score
    if (Array.isArray(c.score) && c.score.length > 0) {
      const relevances = c.score.map(s => s?.relevance).filter(v => typeof v === 'number')
      if (relevances.length > 0) {
        partner_score = relevances.reduce((a, b) => a + b, 0) / relevances.length
      } else {
        partner_score = undefined
      }
    } else if (typeof c.score === 'object' && c.score !== null) {
      partner_score = c.score.relevance || undefined
    } else if (!c.score || (Array.isArray(c.score) && c.score.length === 0)) {
      partner_score = undefined
    }

    return {
      ...c,
      partner_score,
      territory: {
        country: locMaster.country || null,
        region: locMaster.region || null,
        global_region: locMaster.global_region || null,
        city: locMaster.city || null,
        state: locMaster.state || null
      },
      industry: industries.length > 0 ? industries.join(' | ') : (industryDetails[0] || null),
      industry_details: industryDetails,
      segment: classifications.length > 0 ? classifications.join(' | ') : null,
      classifications
    }
  })

  return { data: normalized, error: null }
}

// Obtener lista de sectores (industrias) únicas desde industry_master (con fallback a company_industry)
export async function fetchIndustrySectors(max = 1000) {
  if (!supabase) return []
  // Intento directo a industry_master
  let { data, error } = await supabase
    .from('industry_master')
    .select('sector')
    .limit(max)
  if (error) {
    console.warn('[Supabase] industry_master error, usando fallback company_industry:', error.message)
    const fallback = await supabase
      .from('company_industry')
      .select('industry_master!inner(sector)')
      .limit(max)
    data = fallback.data?.map(r => r.industry_master) || []
  }
  const sectors = Array.isArray(data) ? Array.from(new Set(data.map(r => r?.sector).filter(Boolean))) : []
  return sectors.sort()
}
