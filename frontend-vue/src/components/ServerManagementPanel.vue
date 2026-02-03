<template>
  <Modal
    v-model="internalShow"
    title="服务器管理"
    width="800"
    max-width="95vw"
    :show-default-footer="false"
    @close="handleClose"
  >
    <!-- 服务器列表 -->
    <v-list lines="two">
      <v-list-item
        v-for="server in serverStore.servers"
        :key="server.id"
        :active="server.id === serverStore.currentServerId"
      >
        <template #prepend>
          <v-avatar color="primary" size="40">
            <v-icon icon="mdi-server" />
          </v-avatar>
        </template>

        <v-list-item-title>
          {{ server.name }}
          <v-chip
            v-if="server.is_default"
            size="x-small"
            color="success"
            class="ml-2"
          >
            默认
          </v-chip>
        </v-list-item-title>

        <v-list-item-subtitle>
          {{ server.emby_url }}
        </v-list-item-subtitle>

        <template #append>
          <v-btn
            icon="mdi-pencil"
            variant="text"
            size="small"
            @click="handleEdit(server)"
          />
          <v-btn
            icon="mdi-delete"
            variant="text"
            size="small"
            color="error"
            @click="handleDelete(server)"
          />
        </template>
      </v-list-item>

      <v-list-item v-if="serverStore.servers.length === 0">
        <v-list-item-title class="text-center text-grey">
          暂无服务器
        </v-list-item-title>
      </v-list-item>
    </v-list>

    <v-divider class="my-3" />

    <!-- 添加/编辑表单 -->
    <v-card variant="outlined" class="pa-3">
      <v-card-title class="px-0">
        {{ editingServer ? '编辑服务器' : '添加服务器' }}
      </v-card-title>

      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <v-text-field
          v-model="formData.name"
          label="服务器名称 *"
          density="compact"
          variant="outlined"
          :rules="[rules.required]"
          class="mb-2"
        />

        <v-text-field
          v-model="formData.emby_url"
          label="Emby 服务器地址 *"
          density="compact"
          variant="outlined"
          placeholder="http://localhost:8096"
          :rules="[rules.required, rules.url]"
          class="mb-2"
        />

        <v-text-field
          v-model="formData.emby_api_key"
          label="API Key（可选）"
          density="compact"
          variant="outlined"
          placeholder="如果不填，将从数据库获取"
          class="mb-2"
        />

        <!-- 数据库路径选择 -->
        <v-text-field
          v-model="formData.playback_db"
          label="播放记录数据库（playback_reporting.db）*"
          density="compact"
          variant="outlined"
          readonly
          :rules="[rules.required]"
          hint="示例: /data/playback_reporting.db"
          persistent-hint
          class="mb-3"
        >
          <template #append-inner>
            <v-btn
              icon="mdi-folder-open"
              variant="text"
              size="small"
              @click="openFilePicker('playback_db')"
            />
          </template>
        </v-text-field>

        <v-text-field
          v-model="formData.users_db"
          label="用户数据库（users.db）*"
          density="compact"
          variant="outlined"
          readonly
          :rules="[rules.required]"
          hint="示例: /data/users.db"
          persistent-hint
          class="mb-3"
        >
          <template #append-inner>
            <v-btn
              icon="mdi-folder-open"
              variant="text"
              size="small"
              @click="openFilePicker('users_db')"
            />
          </template>
        </v-text-field>

        <v-text-field
          v-model="formData.auth_db"
          label="认证数据库（authentication.db）*"
          density="compact"
          variant="outlined"
          readonly
          :rules="[rules.required]"
          hint="示例: /data/authentication.db"
          persistent-hint
          class="mb-3"
        >
          <template #append-inner>
            <v-btn
              icon="mdi-folder-open"
              variant="text"
              size="small"
              @click="openFilePicker('auth_db')"
            />
          </template>
        </v-text-field>

        <v-checkbox
          v-model="formData.is_default"
          label="设为默认服务器"
          density="compact"
          hide-details
        />

        <v-card-actions class="px-0 pt-3">
          <v-btn
            v-if="editingServer"
            variant="text"
            @click="handleCancelEdit"
          >
            取消编辑
          </v-btn>
          <v-spacer />
          <v-btn
            type="submit"
            color="primary"
            variant="elevated"
            :loading="submitting"
          >
            {{ editingServer ? '保存' : '添加' }}
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>

    <!-- 文件选择器 -->
    <FilePickerModal
      v-model="showFilePicker"
      :initial-path="'/data'"
      @select="handleFileSelect"
    />
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Modal } from '@/components/ui'
import FilePickerModal from './FilePickerModal.vue'
import { useServerStore } from '@/stores'
import { useToast, useConfirm } from '@/composables'
import type { Server, ServerConfig } from '@/types'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const serverStore = useServerStore()
const { success, error: showError } = useToast()
const { confirm } = useConfirm()

const internalShow = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const formRef = ref()
const editingServer = ref<Server | null>(null)
const submitting = ref(false)
const showFilePicker = ref(false)
const currentField = ref<string>('')

const formData = reactive<ServerConfig>({
  name: '',
  emby_url: '',
  playback_db: '',
  users_db: '',
  auth_db: '',
  emby_api_key: '',
  is_default: false,
})

// 表单验证规则
const rules = {
  required: (v: string) => !!v || '此字段为必填项',
  url: (v: string) => {
    if (!v) return true
    try {
      new URL(v)
      return true
    } catch {
      return '请输入有效的 URL'
    }
  },
}

function openFilePicker(field: string) {
  currentField.value = field
  showFilePicker.value = true
}

function handleFileSelect(path: string) {
  if (currentField.value && formData[currentField.value as keyof ServerConfig] !== undefined) {
    (formData as any)[currentField.value] = path
  }
}

function handleEdit(server: Server) {
  editingServer.value = server
  Object.assign(formData, {
    name: server.name,
    emby_url: server.emby_url,
    playback_db: server.playback_db || '',
    users_db: server.users_db || '',
    auth_db: server.auth_db || '',
    emby_api_key: server.emby_api_key || '',
    is_default: server.is_default,
  })
}

function handleCancelEdit() {
  editingServer.value = null
  resetForm()
}

async function handleSubmit() {
  const { valid } = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (editingServer.value) {
      // 编辑服务器
      await serverStore.updateServer(editingServer.value.id, formData)
      success('服务器更新成功')
      editingServer.value = null
    } else {
      // 添加服务器
      await serverStore.addServer(formData)
      success('服务器添加成功')
    }
    resetForm()
    // 关闭对话框
    internalShow.value = false
  } catch (err) {
    showError('操作失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(server: Server) {
  const confirmed = await confirm('删除服务器', `确定要删除服务器 "${server.name}" 吗？`)
  if (!confirmed) return

  try {
    await serverStore.deleteServer(server.id)
    success('服务器删除成功')
  } catch (err) {
    showError('删除失败，请稍后重试')
  }
}

function resetForm() {
  formData.name = ''
  formData.emby_url = ''
  formData.playback_db = ''
  formData.users_db = ''
  formData.auth_db = ''
  formData.emby_api_key = ''
  formData.is_default = false
  formRef.value?.resetValidation()
}

function handleClose() {
  if (editingServer.value) {
    handleCancelEdit()
  }
  emit('update:modelValue', false)
}
</script>
