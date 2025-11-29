import axios from 'axios'
import { supabase, fetchCompaniesFromSupabase } from '../services/supabase'

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const instance = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' }
})

/**
 * Generic query wrapper.
 * - Si Supabase está configurado, usa Supabase para `list_companies` y `search_company`.
 * - Si NO está configurado, usa POST a `/query` (backend local o remoto).
 */
export async function query(action, params = {}, pagination = {}) {
  // Preferir Supabase si está configurado
  if (supabase && (action === 'list_companies' || action === 'search_company')) {
    const filters = params || {}
    const { data, error } = await fetchCompaniesFromSupabase({ filters, pagination })
    if (error) {
      // No hacer fallback automático: devolver error claro para evitar "Network Error"
      throw new Error(`Supabase error: ${error.message || JSON.stringify(error)}`)
    }
    return { results: data }
  }

  // Si no hay Supabase, usar el backend HTTP
  try {
    const payload = { action, params, pagination }
    const res = await instance.post('/query', payload)
    return res.data
  } catch (err) {
    // Mejorar el mensaje de error
    const msg = err?.message || 'Error desconocido en la petición HTTP'
    // Axios "Network Error" suele indicar CORS/bloqueo de red/backend caído
    throw new Error(`HTTP error: ${msg}. Verifica que el backend esté disponible en ${baseURL} o usa Supabase.`)
  }
}
