<template>
  <router-view v-slot="{ Component }">
    <transition name="page-fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
  <GlobalConfirm />
  <GlobalToast />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores'
import { GlobalConfirm, GlobalToast } from '@/components'

const themeStore = useThemeStore()

// 初始化主题
onMounted(() => {
  // 主题会自动从 localStorage 恢复
  // Vuetify 主题会通过 themeStore 的 watch 自动应用
})
</script>
