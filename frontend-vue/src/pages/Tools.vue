<template>
  <div class="page">
    <PageHeader title="工具箱" subtitle="媒体服务器维护与数据修复工具" />

    <v-fade-transition mode="out-in">
      <div key="tools-content">
        <!-- Item ID 替换工具 -->
        <v-row>
          <v-col cols="12" md="8" lg="6">
            <v-card v-reveal data-delay="100" hover>
              <v-card-title class="card-header">
                <span>Item ID 替换工具</span>
                <v-icon>mdi-swap-horizontal</v-icon>
              </v-card-title>
          <v-card-subtitle>
            用于处理剧集洗版后 ItemId 变化的情况
          </v-card-subtitle>

          <v-card-text>
            <v-alert
              type="info"
              variant="tonal"
              class="mb-4"
              density="compact"
            >
              <div class="text-body-2">
                当剧集重新刮削或洗版后，Emby 会为其分配新的 ItemId。<br>
                此工具可将数据库中的旧 ItemId 批量替换为新 ItemId，保留历史播放记录。
              </div>
            </v-alert>

            <v-alert
              type="warning"
              variant="tonal"
              class="mb-4"
              density="compact"
            >
              <div class="text-body-2">
                <strong>重要提示：</strong>默认情况下，Emby 数据目录建议以只读模式挂载以保护数据安全。<br>
                使用此工具前需要临时修改 <code>docker-compose.yml</code>，将数据挂载点的 <code>:ro</code> 标志移除，然后重启容器。<br>
                操作完成后建议恢复只读模式。
              </div>
            </v-alert>

            <v-form @submit.prevent="handleReplace">
              <v-text-field
                v-model="oldId"
                label="旧 Item ID"
                placeholder="例如：209184"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required, rules.numeric]"
                class="mb-3"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-identifier" size="small" />
                </template>
              </v-text-field>

              <v-text-field
                v-model="newId"
                label="新 Item ID"
                placeholder="例如：209420"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required, rules.numeric]"
                class="mb-4"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-identifier" size="small" />
                </template>
              </v-text-field>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!oldId || !newId"
              >
                <v-icon icon="mdi-swap-horizontal" class="mr-2" />
                执行替换
              </v-btn>
            </v-form>

            <!-- 结果显示 -->
            <v-alert
              v-if="result"
              :type="result.type"
              class="mt-4"
              variant="tonal"
            >
              <div v-html="result.message" />
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 使用说明 -->
      <v-col cols="12" md="4" lg="6">
        <v-card v-reveal data-delay="200" hover>
          <v-card-title class="card-header">
            <span>使用说明</span>
            <v-icon>mdi-information-outline</v-icon>
          </v-card-title>
          <v-card-text>
            <div class="text-body-2">
              <h3 class="text-subtitle-1 font-weight-bold mb-2">如何获取 Item ID？</h3>
              <ol class="mb-4">
                <li class="mb-2">
                  在 Emby 网页端，打开媒体详情页
                </li>
                <li class="mb-2">
                  查看浏览器地址栏，URL 中的 <code>id=xxxxx</code> 就是 Item ID
                </li>
                <li class="mb-2">
                  例如：<code>http://emby.com/web/index.html#!/item?id=<strong>209184</strong></code>
                </li>
              </ol>

              <h3 class="text-subtitle-1 font-weight-bold mb-2">操作步骤</h3>
              <ol class="mb-4">
                <li class="mb-2">
                  找到洗版前的旧内容，获取旧 Item ID
                </li>
                <li class="mb-2">
                  找到洗版后的新内容，获取新 Item ID
                </li>
                <li class="mb-2">
                  在上方输入旧 ID 和新 ID
                </li>
                <li class="mb-2">
                  点击"执行替换"，系统会显示影响的记录数并要求确认
                </li>
              </ol>

              <v-alert type="warning" variant="tonal" density="compact">
                <strong>注意：</strong>此操作会直接修改数据库，请谨慎操作！
              </v-alert>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    </div>
    </v-fade-transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from '@/services/axios'
import { PageHeader } from '@/components/ui'
import { useServerStore } from '@/stores'
import { VALIDATION_RULES } from '@/constants'

const serverStore = useServerStore()

const oldId = ref('')
const newId = ref('')
const loading = ref(false)
const result = ref<{ type: 'success' | 'error' | 'warning', message: string } | null>(null)

// 使用统一的验证规则
const rules = {
  required: VALIDATION_RULES.required,
  numeric: VALIDATION_RULES.numeric,
}

// 执行替换
async function handleReplace() {
  if (!oldId.value || !newId.value) {
    return
  }

  // 检查是否选择了服务器
  if (!serverStore.currentServerId) {
    result.value = {
      type: 'error',
      message: '<strong>✗ 错误</strong><br>请先选择一个服务器',
    }
    return
  }

  try {
    loading.value = true
    result.value = null

    const payload = {
      old_id: oldId.value,
      new_id: newId.value,
      server_id: serverStore.currentServerId,
    }

    console.log('发送请求:', payload)

    const response = await axios.post('/tools/replace-item-id', payload)

    if (response.data.success) {
      result.value = {
        type: 'success',
        message: `<strong>✓ 替换成功</strong><br>共更新了 <strong>${response.data.updated_count}</strong> 条播放记录`,
      }
      // 清空表单
      oldId.value = ''
      newId.value = ''
    } else {
      result.value = {
        type: 'error',
        message: `<strong>✗ 替换失败</strong><br>${response.data.message}`,
      }
    }
  } catch (error: unknown) {
    console.error('替换 Item ID 失败:', error)

    const err = error as { response?: { status?: number; data?: { detail?: unknown } }; message?: string }

    // 处理 422 验证错误
    if (err.response?.status === 422) {
      const detail = err.response?.data?.detail
      let errorMsg = '参数验证失败'

      if (Array.isArray(detail)) {
        // FastAPI 验证错误格式
        errorMsg = detail.map((e: { loc: string[]; msg: string }) => `${e.loc.join('.')}: ${e.msg}`).join('<br>')
      } else if (typeof detail === 'string') {
        errorMsg = detail
      } else if (detail && typeof detail === 'object') {
        errorMsg = JSON.stringify(detail)
      }

      result.value = {
        type: 'error',
        message: `<strong>✗ 参数错误</strong><br>${errorMsg}`,
      }
    } else {
      result.value = {
        type: 'error',
        message: `<strong>✗ 操作失败</strong><br>${err.response?.data?.detail || err.message || '未知错误'}`,
      }
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
code {
  background-color: rgba(var(--v-theme-surface-variant), 0.5);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.875em;
}

ol {
  padding-left: 20px;
}

ol li {
  padding-left: 8px;
}
</style>
