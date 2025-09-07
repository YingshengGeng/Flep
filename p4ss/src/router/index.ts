import { createRouter, createWebHashHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const router = createRouter({
  history: createWebHashHistory('/'),
  routes: [
    {
      path: '/',
      component: Layout,
      redirect: '/reliable-communication',
      children: [
        {
          path: '/reliable-communication',
          name: 'ReliableCommunication',
          meta: { title: '可靠通信网络调度' },
          component: () => import('@/views/reliable-communication.vue')
        },
        {
          path: '/network-node',
          name: 'NetworkNode',
          meta: { title: '网络节点信息' },
          component: () => import('@/views/network-node.vue')
        },
        {
          path: '/system-api',
          name: 'SystemApi',
          meta: { title: '系统调度接口' },
          component: () => import('@/views/system-api.vue')
        }
      ]
    },

    { path: '/:catchAll(.*)', redirect: '/' }
  ],
  scrollBehavior(_to, _from, savedPosition) {
    return savedPosition ? savedPosition : { top: 0, left: 0 }
  }
})

export default router
