import axios from 'axios'

export const http = axios.create({
  baseURL: '',
  timeout: 15000,
  headers: {
    'X-User-Uid': 'demo-admin'
  }
})

http.interceptors.response.use((response) => response.data)

export const api = {
  get: (url, config) => http.get(url, config),
  post: (url, data, config) => http.post(url, data, config),
  put: (url, data, config) => http.put(url, data, config),
  patch: (url, data, config) => http.patch(url, data, config),
  delete: (url, config) => http.delete(url, config)
}
