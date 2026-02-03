<template>
  <div class="page">
    <PageHeader title="报告配置" subtitle="配置定时推送和 Telegram 机器人" />

    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="report">报告配置</v-tab>
      <v-tab value="telegram">Telegram 机器人</v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <!-- 报告配置 -->
      <v-window-item value="report">
        <v-row>
          <v-col cols="12" lg="8">
            <v-card v-reveal data-delay="100" hover>
              <v-card-title class="card-header">
                <span>报告配置</span>
                <v-icon>mdi-file-document-outline</v-icon>
              </v-card-title>
              <v-card-text>

              <v-form ref="reportFormRef" @submit.prevent="handleSaveReportConfig">
                <!-- Telegram 配置 -->
                <div class="text-subtitle-1 mb-3">Telegram 配置</div>

                <v-switch
                  v-model="reportConfig.telegram.enabled"
                  label="启用 Telegram 推送"
                  color="primary"
                  hide-details
                  class="mb-4"
                />

                <template v-if="reportConfig.telegram.enabled">
                  <PasswordField
                    v-model="reportConfig.telegram.bot_token"
                    label="Bot Token"
                    prepend-icon=""
                    variant="outlined"
                    density="compact"
                    placeholder="从 @BotFather 获取"
                    hint="配置后才能启用 Telegram 推送"
                    :persistent-hint="true"
                    field-class="mb-3"
                  />

                  <v-text-field
                    v-model="reportConfig.telegram.chat_id"
                    label="Chat ID *"
                    variant="outlined"
                    density="compact"
                    :rules="[rules.required]"
                    class="mb-3"
                  />

                  <v-text-field
                    v-model="reportConfig.telegram.proxy"
                    label="代理服务器（可选）"
                    variant="outlined"
                    density="compact"
                    placeholder="http://proxy.example.com:8080"
                    class="mb-4"
                  />
                </template>

                <v-divider class="my-4" />

                <!-- 定时任务配置 -->
                <div class="text-subtitle-1 mb-3">定时推送配置</div>

                <v-expansion-panels variant="accordion" class="mb-4">
                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-calendar-today" class="mr-2" />
                        每日推送
                        <v-chip
                          v-if="reportConfig.schedule.daily.enabled"
                          size="small"
                          color="success"
                          class="ml-2"
                        >
                          已启用
                        </v-chip>
                      </div>
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <v-switch
                        v-model="reportConfig.schedule.daily.enabled"
                        label="启用每日推送"
                        color="primary"
                        hide-details
                        class="mb-3"
                      />
                      <v-text-field
                        v-if="reportConfig.schedule.daily.enabled"
                        v-model="reportConfig.schedule.daily.cron"
                        label="Cron 表达式"
                        variant="outlined"
                        density="compact"
                        placeholder="0 9 * * *"
                        hint="格式：分 时 日 月 周"
                        persistent-hint
                      />
                    </v-expansion-panel-text>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-calendar-week" class="mr-2" />
                        每周推送
                        <v-chip
                          v-if="reportConfig.schedule.weekly.enabled"
                          size="small"
                          color="success"
                          class="ml-2"
                        >
                          已启用
                        </v-chip>
                      </div>
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <v-switch
                        v-model="reportConfig.schedule.weekly.enabled"
                        label="启用每周推送"
                        color="primary"
                        hide-details
                        class="mb-3"
                      />
                      <v-text-field
                        v-if="reportConfig.schedule.weekly.enabled"
                        v-model="reportConfig.schedule.weekly.cron"
                        label="Cron 表达式"
                        variant="outlined"
                        density="compact"
                        placeholder="0 9 * * 1"
                        hint="格式：分 时 日 月 周"
                        persistent-hint
                      />
                    </v-expansion-panel-text>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-calendar-month" class="mr-2" />
                        每月推送
                        <v-chip
                          v-if="reportConfig.schedule.monthly.enabled"
                          size="small"
                          color="success"
                          class="ml-2"
                        >
                          已启用
                        </v-chip>
                      </div>
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <v-switch
                        v-model="reportConfig.schedule.monthly.enabled"
                        label="启用每月推送"
                        color="primary"
                        hide-details
                        class="mb-3"
                      />
                      <v-text-field
                        v-if="reportConfig.schedule.monthly.enabled"
                        v-model="reportConfig.schedule.monthly.cron"
                        label="Cron 表达式"
                        variant="outlined"
                        density="compact"
                        placeholder="0 9 1 * *"
                        hint="格式：分 时 日 月 周"
                        persistent-hint
                      />
                    </v-expansion-panel-text>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-calendar" class="mr-2" />
                        每年推送
                        <v-chip
                          v-if="reportConfig.schedule.yearly.enabled"
                          size="small"
                          color="success"
                          class="ml-2"
                        >
                          已启用
                        </v-chip>
                      </div>
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <v-switch
                        v-model="reportConfig.schedule.yearly.enabled"
                        label="启用每年推送"
                        color="primary"
                        hide-details
                        class="mb-3"
                      />
                      <v-text-field
                        v-if="reportConfig.schedule.yearly.enabled"
                        v-model="reportConfig.schedule.yearly.cron"
                        label="Cron 表达式"
                        variant="outlined"
                        density="compact"
                        placeholder="0 9 1 1 *"
                        hint="格式：分 时 日 月 周"
                        persistent-hint
                      />
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>

                <v-divider class="my-4" />

                <!-- 推送用户 -->
                <div class="text-subtitle-1 mb-3">推送用户</div>
                <v-combobox
                  v-model="reportConfig.users"
                  label="用户 ID 列表"
                  variant="outlined"
                  density="compact"
                  multiple
                  chips
                  closable-chips
                  hint="输入 Emby 用户 ID，按 Enter 添加"
                  persistent-hint
                  class="mb-4"
                />

                <!-- 内容数量 -->
                <v-text-field
                  v-model.number="reportConfig.content_count"
                  label="热门内容显示数量"
                  variant="outlined"
                  density="compact"
                  type="number"
                  min="1"
                  max="50"
                  :rules="[rules.required, rules.positiveNumber]"
                  class="mb-4"
                />

                <!-- 操作按钮 -->
                <div class="d-flex ga-2 flex-wrap">
                  <v-btn
                    type="submit"
                    color="primary"
                    :loading="savingReport"
                  >
                    保存配置
                  </v-btn>
                  <v-btn
                    variant="outlined"
                    color="success"
                    :loading="sendingReport"
                    @click="handleSendReport"
                  >
                    手动发送报告
                  </v-btn>
                  <v-btn
                    variant="outlined"
                    color="secondary"
                    prepend-icon="mdi-send-check"
                    :loading="testingReport"
                    :disabled="!reportConfig.telegram.enabled || !reportConfig.telegram.bot_token || !reportConfig.telegram.chat_id"
                    @click="handleTestReport"
                  >
                    测试推送
                  </v-btn>
                </div>

                <v-divider class="my-4" />

                <!-- 报告预览 -->
                <div class="text-subtitle-1 mb-3">报告预览</div>
                <p class="text-caption text-grey mb-3">保存配置后刷新预览</p>

                <!-- 预览周期选择 -->
                <v-btn-toggle
                  v-model="previewPeriod"
                  mandatory
                  variant="outlined"
                  divided
                  density="comfortable"
                  class="mb-3"
                >
                  <v-btn value="daily">今日</v-btn>
                  <v-btn value="weekly">本周</v-btn>
                  <v-btn value="monthly">本月</v-btn>
                </v-btn-toggle>

                <!-- 预览图片 -->
                <div class="report-preview">
                  <img
                    :key="`${previewKey}-${previewPeriod}-${serverStore.currentServer?.id}`"
                    :src="`/api/report/preview?period=${previewPeriod}&server_id=${serverStore.currentServer?.id}&t=${previewKey}`"
                    alt="报告预览"
                    class="w-100"
                  />
                </div>
              </v-form>
              </v-card-text>
            </v-card>

            <!-- 绑定用户列表 -->
            <v-card v-if="bindings.length > 0" v-reveal data-delay="200" hover class="mt-4">
              <v-card-title class="card-header">
                <span>已绑定用户 ({{ bindings.length }})</span>
                <v-icon>mdi-account-multiple</v-icon>
              </v-card-title>
              <v-card-text>
                <!-- 搜索框 -->
                <v-text-field
                  v-model="bindingSearch"
                  placeholder="搜索用户名、TG昵称或ID..."
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  class="mb-3"
                />

                <!-- 绑定列表 -->
                <div class="binding-list">
                  <div
                    v-for="(binding, index) in filteredBindings"
                    :key="binding.tg_user_id"
                    class="binding-item"
                  >
                    <div class="d-flex align-center">
                      <Avatar :name="binding.emby_username" size="32" class="mr-3" />
                      <div class="flex-grow-1">
                        <div class="text-body-2 font-weight-medium">{{ binding.emby_username }}</div>
                        <div class="text-caption text-grey">
                          TG: {{ binding.tg_first_name || binding.tg_username || '未知' }} ({{ binding.tg_user_id }})
                        </div>
                      </div>
                      <v-btn
                        icon="mdi-delete"
                        size="small"
                        variant="text"
                        color="error"
                        :loading="deletingBinding === binding.tg_user_id"
                        @click="handleDeleteBinding(binding.tg_user_id)"
                      />
                    </div>
                  </div>

                  <!-- 空状态 -->
                  <div v-if="filteredBindings.length === 0" class="text-center py-8 text-grey">
                    {{ bindingSearch ? '未找到匹配的用户' : '暂无绑定用户' }}
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- Telegram 机器人配置 -->
      <v-window-item value="telegram">
        <v-row>
          <v-col cols="12" lg="8">
            <v-card v-reveal data-delay="100" hover>
              <v-card-title class="card-header">
                <span>Telegram 机器人配置</span>
                <v-icon>mdi-robot</v-icon>
              </v-card-title>
              <v-card-text>

              <v-alert type="info" variant="tonal" class="mb-4">
                配置 Telegram 机器人后，用户可以通过私聊机器人来绑定账号并接收个人统计报告
              </v-alert>

              <v-form ref="tgFormRef" @submit.prevent="handleSaveTgConfig">
                <v-switch
                  v-model="tgConfig.enabled"
                  label="启用 Telegram 机器人"
                  color="primary"
                  hide-details
                  class="mb-4"
                />

                <template v-if="tgConfig.enabled">
                  <PasswordField
                    v-model="botTokenInput"
                    label=""
                    prepend-icon=""
                    variant="outlined"
                    density="compact"
                    :placeholder="tgConfig.bot_token_configured ? '留空保持不变' : '从 @BotFather 获取'"
                    hint="可与推送功能使用同一个 Bot"
                    :persistent-hint="true"
                    field-class="mb-4"
                  >
                    <template #prepend>
                      <span class="text-body-2">Bot Token</span>
                      <v-chip v-if="tgConfig.bot_token_configured" size="x-small" color="success" class="ml-2">
                        已配置
                      </v-chip>
                    </template>
                  </PasswordField>

                  <v-select
                    v-model="tgConfig.default_period"
                    :items="periodOptions"
                    label="默认统计周期"
                    variant="outlined"
                    density="compact"
                    hint="用户查询统计时的默认时间范围"
                    persistent-hint
                    class="mb-4"
                  />

                  <v-divider class="my-4" />

                  <div class="text-body-2 mb-3">
                    <strong>使用说明：</strong>
                  </div>
                  <v-list density="compact" class="mb-4">
                    <v-list-item>
                      <template #prepend>
                        <v-icon icon="mdi-numeric-1-circle" />
                      </template>
                      <v-list-item-title>用户搜索并私聊你的机器人</v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template #prepend>
                        <v-icon icon="mdi-numeric-2-circle" />
                      </template>
                      <v-list-item-title>发送 /bind 命令开始绑定</v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template #prepend>
                        <v-icon icon="mdi-numeric-3-circle" />
                      </template>
                      <v-list-item-title>输入 Emby 用户名和密码完成绑定</v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template #prepend>
                        <v-icon icon="mdi-numeric-4-circle" />
                      </template>
                      <v-list-item-title>绑定后可使用 /stats 查询个人统计</v-list-item-title>
                    </v-list-item>
                  </v-list>

                  <div class="d-flex ga-2">
                    <v-btn
                      type="submit"
                      color="primary"
                      :loading="savingTg"
                    >
                      保存配置
                    </v-btn>
                  </div>
                </template>
              </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Avatar, PageHeader, PasswordField } from '@/components/ui'
import { useServerStore } from '@/stores'
import { useToast } from '@/composables'
import { reportApi, tgBotApi } from '@/services'
import { VALIDATION_RULES } from '@/constants'
import type { ReportConfig, TgBotConfig, TgBindingUser } from '@/types'

const serverStore = useServerStore()
const { success, error: showError } = useToast()

const activeTab = ref('report')
const reportFormRef = ref()
const tgFormRef = ref()

const savingReport = ref(false)
const sendingReport = ref(false)
const testingReport = ref(false)
const savingTg = ref(false)
const previewPeriod = ref<'daily' | 'weekly' | 'monthly'>('weekly')
const previewKey = ref(Date.now())

const reportConfig = reactive<ReportConfig>({
  telegram: {
    enabled: false,
    bot_token: '',
    chat_id: '',
    proxy: '',
  },
  schedule: {
    daily: {
      enabled: false,
      cron: '0 9 * * *',
    },
    weekly: {
      enabled: false,
      cron: '0 9 * * 1',
    },
    monthly: {
      enabled: false,
      cron: '0 9 1 * *',
    },
    yearly: {
      enabled: false,
      cron: '0 9 1 1 *',
    },
  },
  users: [],
  content_count: 10,
})

const tgConfig = reactive<TgBotConfig>({
  enabled: false,
  bot_token_configured: false,
  default_period: '7d',
  is_running: false,
})

const botTokenInput = ref('')

const bindings = ref<TgBindingUser[]>([])
const bindingSearch = ref('')
const deletingBinding = ref<string | null>(null)

// 筛选绑定用户
const filteredBindings = computed(() => {
  if (!bindingSearch.value.trim()) {
    return bindings.value
  }
  const search = bindingSearch.value.toLowerCase().trim()
  return bindings.value.filter(b =>
    b.emby_username?.toLowerCase().includes(search) ||
    b.tg_username?.toLowerCase().includes(search) ||
    b.tg_first_name?.toLowerCase().includes(search) ||
    b.tg_user_id?.includes(search)
  )
})

const periodOptions = [
  { title: '最近 7 天', value: '7d' },
  { title: '最近 30 天', value: '30d' },
  { title: '最近 90 天', value: '90d' },
  { title: '最近一年', value: '365d' },
]

// 使用统一的验证规则
const rules = VALIDATION_RULES

// 加载报告配置
async function loadReportConfig() {
  if (!serverStore.currentServer) return

  try {
    const response = await reportApi.getReportConfig(serverStore.currentServer.id)
    const { config } = response.data

    // 深度合并配置，确保 schedule 的嵌套对象正确合并
    reportConfig.telegram = { ...reportConfig.telegram, ...config.telegram }
    reportConfig.schedule = {
      daily: { ...reportConfig.schedule.daily, ...config.schedule?.daily },
      weekly: { ...reportConfig.schedule.weekly, ...config.schedule?.weekly },
      monthly: { ...reportConfig.schedule.monthly, ...config.schedule?.monthly },
      yearly: { ...reportConfig.schedule.yearly, ...config.schedule?.yearly },
    }
    reportConfig.users = config.users || []
    reportConfig.content_count = config.content_count || 10
  } catch (error) {
    console.error('Failed to load report config:', error)
  }
}

// 保存报告配置
async function handleSaveReportConfig() {
  const { valid } = await reportFormRef.value?.validate()
  if (!valid) return

  if (!serverStore.currentServer) return

  savingReport.value = true
  try {
    await reportApi.saveReportConfig(serverStore.currentServer.id, reportConfig)
    success('报告配置已保存')
    // 刷新预览
    previewKey.value++
  } catch (error) {
    showError('保存失败，请稍后重试')
  } finally {
    savingReport.value = false
  }
}

// 发送报告
async function handleSendReport() {
  if (!serverStore.currentServer) return

  sendingReport.value = true
  try {
    const response = await reportApi.sendReport(
      serverStore.currentServer.id,
      'weekly'  // 默认使用本周
    )
    success('报告已发送')
  } catch (error) {
    showError('发送失败，请稍后重试')
  } finally {
    sendingReport.value = false
  }
}

// 测试报告推送
async function handleTestReport() {
  if (!reportConfig.telegram.enabled || !reportConfig.telegram.bot_token || !reportConfig.telegram.chat_id) {
    showError('请先配置 Telegram 推送')
    return
  }

  testingReport.value = true
  try {
    await reportApi.testReportPush(reportConfig.telegram.bot_token, reportConfig.telegram.chat_id)
    success('测试消息已发送！请检查 Telegram 查看')
  } catch (error: unknown) {
    const err = error as { response?: { data?: { error?: string } } }
    const errorMsg = err?.response?.data?.error || '测试失败，请检查 Bot Token 和 Chat ID'
    showError(errorMsg)
  } finally {
    testingReport.value = false
  }
}

// 加载 Telegram 配置
async function loadTgConfig() {
  try {
    const response = await tgBotApi.getTgBotConfig()
    Object.assign(tgConfig, response.data)
  } catch (error) {
    console.error('Failed to load TG config:', error)
  }
}

// 保存 Telegram 配置
async function handleSaveTgConfig() {
  const { valid } = await tgFormRef.value?.validate()
  if (!valid) return

  // 验证：如果没有已配置的token，且用户没有输入新token，则报错
  if (!tgConfig.bot_token_configured && !botTokenInput.value.trim()) {
    showError('请输入 Bot Token')
    return
  }

  savingTg.value = true
  try {
    const configToSave = {
      enabled: tgConfig.enabled,
      default_period: tgConfig.default_period,
      bot_token_configured: tgConfig.bot_token_configured,
      is_running: tgConfig.is_running,
    } as TgBotConfig & { bot_token?: string }

    // 只有在输入了新token时才发送
    if (botTokenInput.value.trim()) {
      configToSave.bot_token = botTokenInput.value.trim()
    }

    await tgBotApi.saveTgBotConfig(configToSave)
    success('Telegram 机器人配置已保存')
    // 清空输入框
    botTokenInput.value = ''
    // 重新加载配置
    await loadTgConfig()
  } catch (error) {
    showError('保存失败，请稍后重试')
  } finally {
    savingTg.value = false
  }
}

// 加载绑定用户
async function loadBindings() {
  if (!serverStore.currentServer) return

  try {
    const response = await reportApi.getBindings(serverStore.currentServer.id)
    bindings.value = response.data.bindings || []
  } catch (error) {
    console.error('Failed to load bindings:', error)
  }
}

// 删除绑定
async function handleDeleteBinding(tgUserId: string) {
  if (!serverStore.currentServer) return

  deletingBinding.value = tgUserId
  try {
    await reportApi.deleteBinding(serverStore.currentServer.id, tgUserId)
    bindings.value = bindings.value.filter(b => b.tg_user_id !== tgUserId)
    success('绑定已删除')
  } catch (error) {
    showError('删除失败，请稍后重试')
  } finally {
    deletingBinding.value = null
  }
}

// 监听服务器切换
watch(
  () => serverStore.currentServer?.id,
  () => {
    loadReportConfig()
    loadTgConfig()
    loadBindings()
  }
)

// 监听预览周期切换，强制刷新图片
watch(previewPeriod, () => {
  previewKey.value = Date.now()
})

onMounted(() => {
  loadReportConfig()
  loadTgConfig()
  loadBindings()
})
</script>

<style scoped>
/* 绑定列表样式 */
.binding-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.binding-item {
  padding: 12px;
  border-radius: 8px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
  transition: background 0.2s;
}

.binding-item:hover {
  background: rgba(var(--v-theme-surface-variant), 0.5);
}

/* 报告预览样式 */
.report-preview {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-surface-variant), 0.3);
}

.report-preview img {
  display: block;
  width: 100%;
  height: auto;
}
</style>
