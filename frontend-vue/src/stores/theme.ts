import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore(
  'theme',
  () => {
    // State
    const isDark = ref(true)

    // Actions
    function toggleTheme() {
      isDark.value = !isDark.value
      // Vuetify 主题将在组件中通过 watch 响应变化
    }

    function setTheme(dark: boolean) {
      isDark.value = dark
    }

    return {
      // State
      isDark,
      // Actions
      toggleTheme,
      setTheme,
    }
  },
  {
    persist: {
      storage: localStorage,
    },
  }
)
