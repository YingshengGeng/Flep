import { defineStore } from 'pinia'

export const userStore = defineStore('user', {
  state: () => ({
    token: '',
    info: {}
  }),

  actions: {
    async login() {
      await new Promise(resolve => setTimeout(resolve, 1000))
      this.token = `${Math.random()}_${Date.now()}`
    }
  }
})
