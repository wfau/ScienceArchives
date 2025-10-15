import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import QueryView from '@/views/QueryView.vue'
import ResultView from '@/views/ResultView.vue'
import QueryListView from '@/views/QueryListView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // history: createWebHashHistory(),
  routes: [
    // {
    //   path: '/',
    //   name: 'home',
    //   component: HomeView,
    // },
    {
      path: '/',
      name: 'query-list',
      component: QueryListView,
    },
    {
      path: '/query/new',
      name: 'query-form',
      component: QueryView,
    },
    {
      path: '/result/:id(\\d+)',
      name: 'query-result',
      component: ResultView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
