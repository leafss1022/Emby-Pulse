<template>
  <v-app>
    <!-- 桌面端侧边栏 -->
    <v-navigation-drawer
      v-if="!mobile"
      permanent
      width="240"
      class="sidebar"
      style="overflow-y: hidden;"
    >
      <div class="sidebar-content" style="overflow-y: auto; height: 100%;">
        <!-- Logo Header -->
        <div class="sidebar-header pa-4">
          <div class="logo-container">
            <div class="logo-mark">
              <LogoMark class="logo-mark-icon" :size="20" title="Emby Stats" />
            </div>
            <div class="logo-info">
              <span class="logo-title">Emby Stats</span>
              <v-chip size="x-small" color="primary">v2.32.17</v-chip>
            </div>
          </div>
        </div>

        <!-- Navigation Menu -->
        <v-list density="compact" nav class="px-2 flex-grow-1">
          <v-list-item
            v-for="item in menuItems"
            :key="item.to"
            :to="item.to"
            :prepend-icon="item.icon"
            :title="item.title"
            :active="isActiveRoute(item.to)"
            rounded="lg"
          />
        </v-list>

        <!-- Footer -->
        <div class="sidebar-footer pa-4">
          <!-- 服务器选择器 -->
          <v-select
            v-if="serverOptions.length > 1"
            v-model="serverStore.currentServerId"
            :items="serverOptions"
            item-title="name"
            item-value="id"
            label="选择服务器"
            density="compact"
            variant="outlined"
            hide-details
            class="mb-3"
          >
            <template #append-inner>
              <v-icon
                icon="mdi-cog"
                size="small"
                @click.stop="showServerManagement = true"
              />
            </template>
          </v-select>

          <!-- 筛选按钮 -->
          <v-btn
            variant="text"
            block
            @click="openFilter"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-filter-outline" />
            </template>
            筛选器
            <v-badge
              v-if="filterStore.hasActiveFilters"
              :content="filterStore.activeFilterCount"
              color="primary"
              inline
              class="ml-2"
            />
          </v-btn>

          <!-- 名称映射按钮 -->
          <v-btn
            variant="text"
            block
            @click="openNameMapping"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-tag-text" />
            </template>
            名称映射
          </v-btn>

          <!-- 主题切换 -->
          <v-btn
            variant="text"
            block
            @click="toggleTheme"
            class="mb-2"
          >
            <template #prepend>
              <v-icon :icon="isDark ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent'" />
            </template>
            {{ isDark ? '浅色模式' : '深色模式' }}
          </v-btn>

          <!-- 登出按钮 -->
          <v-btn
            variant="text"
            block
            @click="handleLogout"
            class="mb-3 logout-button"
          >
            <template #prepend>
              <v-icon icon="mdi-logout" />
            </template>
            登出
          </v-btn>

          <!-- 状态指示器 -->
          <div class="status-container">
            <v-badge color="success" dot inline />
            <span class="status-text ml-2">服务运行中</span>
          </div>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- 移动端顶栏 -->
    <v-app-bar v-if="mobile" elevation="1" class="mobile-header">
      <v-app-bar-nav-icon @click="drawer = true" />
      <v-app-bar-title>
        <div class="mobile-logo-container">
          <div class="logo-mark small">
            <LogoMark class="logo-mark-icon" :size="18" title="Emby Stats" />
          </div>
          <span class="ml-2 font-weight-medium">Emby Stats</span>
        </div>
      </v-app-bar-title>
      <template #append>
        <!-- 服务器选择 -->
        <v-select
          v-if="serverOptions.length > 1"
          v-model="serverStore.currentServerId"
          :items="serverOptions"
          item-title="name"
          item-value="id"
          label="服务器"
          density="compact"
          variant="outlined"
          hide-details
          style="max-width: 120px"
          class="mr-2"
        />
        <v-btn
          icon="mdi-filter-outline"
          @click="openFilter"
        >
          <v-badge
            v-if="filterStore.hasActiveFilters"
            :content="filterStore.activeFilterCount"
            color="primary"
            dot
          >
            <v-icon>mdi-filter-outline</v-icon>
          </v-badge>
          <v-icon v-else>mdi-filter-outline</v-icon>
        </v-btn>
      </template>
    </v-app-bar>

    <!-- 移动端抽屉 -->
    <v-navigation-drawer
      v-if="mobile"
      v-model="drawer"
      temporary
      width="280"
    >
      <div class="sidebar-content">
        <div class="sidebar-header pa-4">
          <div class="logo-container">
            <div class="logo-mark">
              <LogoMark class="logo-mark-icon" :size="20" title="Emby Stats" />
            </div>
            <div class="logo-info">
              <span class="logo-title">Emby Stats</span>
              <v-chip size="x-small" color="primary">v2.32.17</v-chip>
            </div>
          </div>
        </div>

        <v-list density="compact" nav class="px-2 flex-grow-1">
          <v-list-item
            v-for="item in menuItems"
            :key="item.to"
            :to="item.to"
            :prepend-icon="item.icon"
            :title="item.title"
            :active="isActiveRoute(item.to)"
            rounded="lg"
            @click="drawer = false"
          />
        </v-list>

        <div class="sidebar-footer pa-4">
          <!-- 服务器选择器 -->
          <v-select
            v-if="serverOptions.length > 1"
            v-model="serverStore.currentServerId"
            :items="serverOptions"
            item-title="name"
            item-value="id"
            label="选择服务器"
            density="compact"
            variant="outlined"
            hide-details
            class="mb-3"
          >
            <template #append-inner>
              <v-icon
                icon="mdi-cog"
                size="small"
                @click.stop="showServerManagement = true; drawer = false"
              />
            </template>
          </v-select>

          <!-- 筛选按钮 -->
          <v-btn
            variant="text"
            block
            @click="openFilter(); drawer = false"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-filter-outline" />
            </template>
            筛选器
            <v-badge
              v-if="filterStore.hasActiveFilters"
              :content="filterStore.activeFilterCount"
              color="primary"
              inline
              class="ml-2"
            />
          </v-btn>

          <v-btn
            variant="text"
            block
            @click="openNameMapping(); drawer = false"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-tag-text" />
            </template>
            名称映射
          </v-btn>

          <v-btn
            variant="text"
            block
            @click="toggleTheme"
            class="mb-2"
          >
            <template #prepend>
              <v-icon :icon="isDark ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent'" />
            </template>
            {{ isDark ? '浅色模式' : '深色模式' }}
          </v-btn>
          <v-btn
            variant="text"
            block
            @click="handleLogout"
            class="mb-3 logout-button"
          >
            <template #prepend>
              <v-icon icon="mdi-logout" />
            </template>
            登出
          </v-btn>
          <div class="status-container">
            <v-badge color="success" dot inline />
            <span class="status-text ml-2">服务运行中</span>
          </div>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- 主内容区 -->
    <v-main>
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </v-main>

    <!-- 筛选面板 -->
    <FilterPanel
      v-model="showFilter"
      @close="showFilter = false"
    />

    <!-- 服务器管理面板 -->
    <ServerManagementPanel
      v-model="showServerManagement"
      @close="showServerManagement = false"
    />

    <!-- 名称映射面板 -->
    <NameMappingPanel
      :is-open="showNameMapping"
      @update:is-open="showNameMapping = $event"
    />
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDisplay, useTheme } from 'vuetify'
import { useAuthStore, useServerStore, useFilterStore } from '@/stores'
import FilterPanel from '@/components/FilterPanel.vue'
import ServerManagementPanel from '@/components/ServerManagementPanel.vue'
import NameMappingPanel from '@/components/NameMappingPanel.vue'
import LogoMark from '@/components/ui/LogoMark.vue'

const router = useRouter()
const route = useRoute()
const { mobile } = useDisplay()
const theme = useTheme()
const authStore = useAuthStore()
const serverStore = useServerStore()
const filterStore = useFilterStore()

const drawer = ref(!mobile.value)

// 初始化：确保服务器列表已加载
onMounted(async () => {
  // 如果服务器列表为空，需要重新获取
  if (serverStore.servers.length === 0) {
    await serverStore.fetchServers()
  }
})

const showFilter = ref(false)
const showServerManagement = ref(false)
const showNameMapping = ref(false)

// 主题切换
const isDark = computed(() => theme.global.name.value === 'dark')
function toggleTheme() {
  theme.global.name.value = isDark.value ? 'light' : 'dark'
  localStorage.setItem('theme', theme.global.name.value)
}

// 菜单项配置
const menuItems = [
  { to: '/', icon: 'mdi-view-dashboard', title: '总览' },
  { to: '/content', icon: 'mdi-filmstrip', title: '内容统计' },
  { to: '/users', icon: 'mdi-account-group', title: '用户统计' },
  { to: '/devices', icon: 'mdi-devices', title: '设备统计' },
  { to: '/history', icon: 'mdi-history', title: '播放历史' },
  { to: '/favorites', icon: 'mdi-star', title: '收藏统计' },
  { to: '/report', icon: 'mdi-file-document', title: '报告配置' },
  { to: '/tools', icon: 'mdi-tools', title: '工具箱' },
]

// 服务器选项
const serverOptions = computed(() => {
  return serverStore.servers.map((server) => ({
    id: server.id,
    name: server.name,
  }))
})

// 打开筛选面板（关闭名称映射）
function openFilter() {
  showNameMapping.value = false
  showFilter.value = true
}

// 打开名称映射面板(关闭筛选器)
function openNameMapping() {
  showFilter.value = false
  showNameMapping.value = true
}

// 判断路由是否激活（精确匹配）
function isActiveRoute(to: string): boolean {
  return route.path === to
}

// 处理退出登录
async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* 确保侧边栏可以独立滚动 */
.sidebar :deep(.v-navigation-drawer__content) {
  overflow-y: auto !important;
  overflow-x: hidden;
  height: 100%;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  touch-action: pan-y;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}

.sidebar-header {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-logo-container {
  display: flex;
  align-items: center;
}

.logo-mark {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #93c5fd 0%, rgb(var(--v-theme-primary)) 55%, #1d4ed8 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0b1220;
  font-weight: 700;
  font-size: 13px;
  flex-shrink: 0;
}

.logo-mark.small {
  width: 32px;
  height: 32px;
  font-size: 11px;
}

.logo-mark :deep(.logo-mark-icon) {
  display: block;
}

.logo-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.logo-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.2;
}

.sidebar-footer {
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.status-container {
  display: flex;
  align-items: center;
  padding: 12px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 8px;
}

.status-text {
  font-size: 13px;
  opacity: 0.8;
}

.logout-button:hover {
  color: rgb(var(--v-theme-error)) !important;
}
</style>
