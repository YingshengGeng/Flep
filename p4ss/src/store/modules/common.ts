import { defineStore } from 'pinia'

export const commonStore = defineStore('common', {
  state: () => ({
    resource: {
      is: [
        { label: '是', value: true },
        { label: '否', value: false }
      ]
    }
  }),

  actions: {}
})
