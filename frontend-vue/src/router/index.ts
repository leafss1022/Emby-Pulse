import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'Overview',
        component: () => import('@/pages/Overview.vue'),
        meta: {
          title: '总览',
        },
      },
      {
        path: 'content',
        name: 'Content',
        component: () => import('@/pages/Content.vue'),
        meta: {
          title: '内容统计',
        },
      },
      {
        path: 'content/:id',
        name: 'ContentDetail',
        component: () => import('@/pages/ContentDetail.vue'),
        meta: {
          title: '内容详情',
        },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/pages/Users.vue'),
        meta: {
          title: '用户统计',
        },
      },
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('@/pages/Devices.vue'),
        meta: {
          title: '设备统计',
        },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/pages/History.vue'),
        meta: {
          title: '播放历史',
        },
      },
      {
        path: 'favorites',
        name: 'Favorites',
        component: () => import('@/pages/Favorites.vue'),
        meta: {
          title: '收藏统计',
        },
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('@/pages/Report.vue'),
        meta: {
          title: '报告配置',
        },
      },
      {
        path: 'tools',
        name: 'Tools',
        component: () => import('@/pages/Tools.vue'),
        meta: {
          title: '工具箱',
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 全局路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Emby Stats`
  } else {
    document.title = 'Emby Stats'
  }

  // 检查是否需要认证
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth !== false)

  if (requiresAuth) {
    // 需要认证的路由
    if (!authStore.isAuthenticated) {
      // 未登录，检查会话
      try {
        await authStore.checkAuth()
        if (authStore.isAuthenticated) {
          next()
        } else {
          // 会话无效，跳转到登录页
          next({
            name: 'Login',
            query: { redirect: to.fullPath },
          })
        }
      } catch (error) {
        // 检查失败，跳转到登录页
        next({
          name: 'Login',
          query: { redirect: to.fullPath },
        })
      }
    } else {
      next()
    }
  } else {
    // 不需要认证的路由（如登录页）
    if (to.name === 'Login' && authStore.isAuthenticated) {
      // 已登录用户访问登录页，重定向到首页
      next({ name: 'Overview' })
    } else {
      next()
    }
  }
})

export default router
