import { defineStore } from 'pinia'
import { api } from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    menu: []
  }),
  actions: {
    async bootstrap() {
      const [check, menu] = await Promise.all([api.get('/api/auth/check'), api.get('/api/auth/menu')])
      this.user = check.data.user
      this.menu = menu.data
    }
  }
})
