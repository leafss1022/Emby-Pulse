import './assets/theme.css'
import './assets/page-styles.css'
import './assets/animations.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import vuetify from './plugins/vuetify'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(vuetify)

// 滚动显现指令的全局协调器
const revealQueue: HTMLElement[] = []
let isProcessingQueue = false

// 路由切换时清空动画队列，防止旧页面的元素干扰新页面
router.beforeEach(() => {
  revealQueue.length = 0
  isProcessingQueue = false
})

const processRevealQueue = () => {
  if (revealQueue.length === 0) {
    isProcessingQueue = false
    return
  }

  isProcessingQueue = true
  const el = revealQueue.shift()
  if (el) {
    el.classList.add('reveal-active')
  }
  
  // 这里的延迟决定了多个元素同时出现时的交错速度（60ms 是电影感的黄金分割）
  setTimeout(processRevealQueue, 60)
}

const revealObserver = new IntersectionObserver((entries) => {
  const newlyIntersecting = entries
    .filter(entry => entry.isIntersecting)
    .map(entry => entry.target as HTMLElement)

  if (newlyIntersecting.length > 0) {
    // 关键：按页面位置排序，确保从上到下、从左到右显现，彻底解决 index 取模导致的顺序错乱
    newlyIntersecting.sort((a, b) => {
      const rectA = a.getBoundingClientRect()
      const rectB = b.getBoundingClientRect()
      return (rectA.top - rectB.top) || (rectA.left - rectB.left)
    })

    newlyIntersecting.forEach(el => {
      revealObserver.unobserve(el)
      revealQueue.push(el)
    })

    if (!isProcessingQueue) {
      processRevealQueue()
    }
  }
}, {
  threshold: 0.01,
  rootMargin: '0px 0px 85px 0px'
})

app.directive('reveal', {
  mounted(el) {
    if (el.classList.contains('reveal-active')) return
    el.classList.add('reveal-hidden')
    revealObserver.observe(el)
  },
  updated(el) {
    if (el.classList.contains('reveal-active') || el.classList.contains('reveal-hidden')) return
    el.classList.add('reveal-hidden')
    revealObserver.observe(el)
  },
  unmounted(el) {
    revealObserver.unobserve(el)
  }
})

// 初始化主题
const savedTheme = localStorage.getItem('theme')
if (savedTheme && (savedTheme === 'dark' || savedTheme === 'light')) {
  vuetify.theme.global.name.value = savedTheme
}

app.mount('#app')
