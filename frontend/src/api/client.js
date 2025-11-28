import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const instance = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' }
})

export async function query(action, params = {}, pagination = {}) {
  const payload = { action, params, pagination }
  const res = await instance.post('/query', payload)
  return res.data
}
