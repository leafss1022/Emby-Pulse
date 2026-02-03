import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// 定义蓝色主题（与 api-cache-proxy 保持一致）
const lightTheme = {
  dark: false,
  colors: {
    background: '#f2f4f7',      // 优化：更深的灰调背景，增加对比度
    surface: '#ffffff',
    'surface-variant': '#f1f5f9',
    'on-surface-variant': '#64748b',
    primary: '#1d4ed8',
    'primary-darken-1': '#1e40af',
    secondary: '#3b82f6',
    'secondary-darken-1': '#2563eb',
    error: '#ef4444',
    info: '#3b82f6',
    success: '#22c55e',
    warning: '#f59e0b',
    'on-primary': '#ffffff',
    'on-secondary': '#ffffff',
    'on-success': '#ffffff',
    'on-error': '#ffffff',
    'on-info': '#ffffff',
    'on-warning': '#ffffff',
  },
}

const darkTheme = {
  dark: true,
  colors: {
    background: '#0a0d14',      // 深黑背景（微量蓝调平衡）
    surface: '#13161f',         // 深灰卡片（适度蓝调）
    'surface-variant': '#1a1d2a',  // 灰色带少量蓝
    'on-surface-variant': '#94a3b8',  // 更亮的文字
    primary: '#3b82f6',
    'primary-darken-1': '#2563eb',
    secondary: '#60a5fa',
    'secondary-darken-1': '#3b82f6',
    error: '#ef4444',
    info: '#3b82f6',
    success: '#22c55e',
    warning: '#f59e0b',
    'on-primary': '#ffffff',
    'on-secondary': '#ffffff',
    'on-success': '#ffffff',
    'on-error': '#ffffff',
    'on-info': '#ffffff',
    'on-warning': '#ffffff',
  },
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
  theme: {
    defaultTheme: 'dark',
    themes: {
      light: lightTheme,
      dark: darkTheme,
    },
  },
  defaults: {
    VCard: {
      elevation: 0,
      rounded: 'lg',
    },
    VBtn: {
      rounded: 'lg',
      elevation: 0,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VSwitch: {
      color: 'primary',
    },
    VCheckbox: {
      color: 'primary',
    },
  },
})
