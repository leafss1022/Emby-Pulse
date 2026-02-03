<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="12" rounded="lg">
          <!-- Logo 和标题 -->
          <v-card-title class="text-center py-6">
            <div class="d-flex flex-column align-center">
              <v-icon icon="mdi-chart-box" size="64" color="primary" />
              <h1 class="text-h4 mt-4">Emby Stats</h1>
              <p class="text-subtitle-1 text-grey">媒体服务器播放统计分析</p>
            </div>
          </v-card-title>

          <v-divider />

          <v-card-text class="pa-6">
            <v-form ref="formRef" @submit.prevent="handleLogin">
              <!-- 服务器选择 -->
              <v-select
                v-model="selectedServerId"
                :items="serverOptions"
                item-title="name"
                item-value="id"
                label="选择服务器"
                prepend-inner-icon="mdi-server"
                variant="outlined"
                :rules="[rules.required]"
                :disabled="serverStore.servers.length === 0"
                class="mb-4"
              >
                <template #append>
                  <v-tooltip text="管理服务器">
                    <template #activator="{ props }">
                      <v-btn
                        icon="mdi-cog"
                        variant="text"
                        size="small"
                        v-bind="props"
                        @click="showServerManagement = true"
                      />
                    </template>
                  </v-tooltip>
                </template>
              </v-select>

              <!-- 用户名 -->
              <v-text-field
                v-model="username"
                label="用户名"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="[rules.required]"
                :disabled="!selectedServerId"
                class="mb-4"
              />

              <!-- 密码 -->
              <PasswordField
                v-model="password"
                label="密码"
                :rules="[rules.required]"
                :disabled="!selectedServerId"
                field-class="mb-4"
              />

              <!-- 登录按钮 -->
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!selectedServerId"
              >
                登录
              </v-btn>
            </v-form>

            <!-- 提示信息 -->
            <v-alert
              v-if="serverStore.servers.length === 0"
              type="info"
              variant="tonal"
              class="mt-4"
            >
              <template #text>
                <div class="d-flex flex-column">
                  <span class="mb-2">暂无服务器配置，请先添加服务器</span>
                  <v-btn
                    variant="text"
                    prepend-icon="mdi-plus"
                    @click="showServerManagement = true"
                  >
                    添加服务器
                  </v-btn>
                </div>
              </template>
            </v-alert>
          </v-card-text>
        </v-card>

        <!-- 底部信息 -->
        <div class="text-center mt-4 text-grey">
          <p>Powered by Emby Stats</p>
        </div>
      </v-col>
    </v-row>

    <!-- 服务器管理面板 -->
    <ServerManagementPanel v-model="showServerManagement" />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore, useServerStore } from '@/stores'
import { useToast } from '@/composables'
import { PasswordField } from '@/components/ui'
import ServerManagementPanel from '@/components/ServerManagementPanel.vue'
import { VALIDATION_RULES } from '@/constants'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverStore = useServerStore()
const { success, error: showError } = useToast()

const formRef = ref()
const selectedServerId = ref<string>('')
const username = ref('')
const password = ref('')
const loading = ref(false)
const showServerManagement = ref(false)

// 表单验证规则
const rules = VALIDATION_RULES

// 服务器选项
const serverOptions = computed(() => {
  return serverStore.servers.map((server) => ({
    id: server.id,
    name: server.name,
  }))
})

// 处理登录
async function handleLogin() {
  if (!formRef.value) return

  try {
    const result = await formRef.value.validate()
    if (!result.valid) return
  } catch (error) {
    return
  }

  loading.value = true
  try {
    const loginSuccess = await authStore.login(
      selectedServerId.value,
      username.value,
      password.value
    )

    if (loginSuccess) {
      success('登录成功')

      // 设置当前服务器
      serverStore.setCurrentServer(selectedServerId.value)

      // 重定向到目标页面或首页
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } else {
      showError('登录失败，请检查用户名和密码')
    }
  } catch (err) {
    showError('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(async () => {
  // 加载服务器列表
  await serverStore.fetchServers()

  // 如果有默认服务器，自动选中
  const defaultServer = serverStore.servers.find((s) => s.is_default)
  if (defaultServer) {
    selectedServerId.value = defaultServer.id
  } else if (serverStore.servers.length >= 1) {
    // 如果只有一个服务器，自动选中
    const firstServer = serverStore.servers[0]
    if (firstServer) {
      selectedServerId.value = firstServer.id
    }
  }
})
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  background: rgb(var(--v-theme-surface));
}
</style>
