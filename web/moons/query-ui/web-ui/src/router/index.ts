import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import QueryView from '@/views/QueryView.vue'
import ResultView from '@/views/ResultView.vue'
import QueryListView from '@/views/QueryListView.vue'
import SchemaView from '@/views/SchemaView.vue'
import QueryTemplateView from '@/views/QueryTemplateView.vue'
import TargetView from '@/views/TargetView.vue'
import GenerateSQLView from '@/views/GenerateSQLView.vue'
import CombinedSQLView from '@/views/CombinedSQLView.vue'

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
      path: '/query/chat',
      name: 'query-chat',
      component: GenerateSQLView,
    },
    {
      path: '/query/:id(\\d+)',
      name: 'query-edit',
      component: QueryView,
    },
    {
      path: '/result/:id(\\d+)',
      name: 'query-result',
      component: ResultView,
    },
    {
      path: '/query/edit-chat',
      name: 'query-new-chat',
      component: CombinedSQLView,
    },
    {
      path: '/query/edit-chat/:id(\\d+)',
      name: 'query-edit-chat',
      component: CombinedSQLView,
    },
    {
      path: '/resultfile/:id(\\d+)',
      name: 'result-file',
      component: TargetView,
    },
    {
      path: '/schema',
      name: 'database-schema',
      component: SchemaView,
    },
    {
      path: '/template',
      name: 'query-templates',
      component: QueryTemplateView,
    },
    {
      path: '/template/:tid(\\d+)',
      name: 'template-edit',
      component: QueryView,
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
