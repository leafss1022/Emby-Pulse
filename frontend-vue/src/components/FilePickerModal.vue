<template>
  <Modal
    v-model="internalShow"
    title="选择文件"
    width="700"
    :show-default-footer="false"
    @close="handleClose"
  >
    <!-- 面包屑导航 -->
    <div class="d-flex align-center mb-2">
      <v-btn
        v-for="(item, index) in breadcrumbs"
        :key="item.value"
        variant="text"
        size="small"
        :disabled="item.disabled"
        @click="item.disabled ? undefined : navigateTo(item.value)"
      >
        {{ item.title }}
        <v-icon v-if="index < breadcrumbs.length - 1" icon="mdi-chevron-right" class="ml-1" />
      </v-btn>
    </div>

    <v-divider class="mb-2" />

    <!-- 文件列表 -->
    <v-list density="compact" max-height="400" class="overflow-y-auto">
      <v-list-item
        v-if="loading"
        prepend-icon="mdi-loading"
        title="加载中..."
      />

      <template v-else>
        <!-- 上级目录 -->
        <v-list-item
          v-if="currentPath !== '/'"
          prepend-icon="mdi-arrow-up"
          title=".."
          @click="goToParent"
        />

        <!-- 文件/目录列表 -->
        <v-list-item
          v-for="entry in entries"
          :key="entry.path"
          :prepend-icon="entry.is_dir ? 'mdi-folder' : 'mdi-file'"
          :title="entry.name"
          @click="handleEntryClick(entry)"
        >
          <template #append>
            <v-chip
              v-if="!entry.is_dir && entry.name.endsWith('.db')"
              size="x-small"
              color="primary"
              variant="flat"
            >
              DB
            </v-chip>
          </template>
        </v-list-item>

        <!-- 空状态 -->
        <v-list-item v-if="entries.length === 0" class="text-center">
          <v-list-item-title class="text-grey">
            此目录为空
          </v-list-item-title>
        </v-list-item>
      </template>
    </v-list>

    <v-divider class="my-3" />

    <!-- 当前选择 -->
    <v-text-field
      v-model="selectedPath"
      label="选择的文件路径"
      density="compact"
      variant="outlined"
      readonly
      hide-details
    />

    <!-- 底部按钮 -->
    <template #footer>
      <v-spacer />
      <v-btn variant="text" @click="handleClose">
        取消
      </v-btn>
      <v-btn
        color="primary"
        variant="elevated"
        :disabled="!selectedPath"
        @click="handleConfirm"
      >
        确定
      </v-btn>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Modal } from '@/components/ui'
import { filesApi } from '@/services'
import type { FileEntry } from '@/types'

interface Props {
  modelValue: boolean
  initialPath?: string
}

const props = withDefaults(defineProps<Props>(), {
  initialPath: '/',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  select: [path: string]
}>()

const internalShow = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const currentPath = ref(props.initialPath)
const entries = ref<FileEntry[]>([])
const selectedPath = ref('')
const loading = ref(false)

const breadcrumbs = computed(() => {
  const parts = currentPath.value.split('/').filter(Boolean)
  const items: Array<{ title: string; value: string; disabled: boolean }> = [
    { title: '根目录', value: '/', disabled: false },
  ]

  let path = ''
  for (const part of parts) {
    path += `/${part}`
    items.push({
      title: part,
      value: path,
      disabled: false,
    })
  }

  // 最后一项禁用（当前位置）
  const lastIndex = items.length - 1
  if (lastIndex >= 0 && items[lastIndex]) {
    const lastItem = items[lastIndex]
    items[lastIndex] = {
      title: lastItem.title,
      value: lastItem.value,
      disabled: true,
    }
  }

  return items
})

async function browseDirectory(path: string) {
  loading.value = true
  try {
    const response = await filesApi.browseFiles(path)
    currentPath.value = response.data.cwd
    entries.value = response.data.entries || []
  } catch (error) {
    console.error('Failed to browse directory:', error)
  } finally {
    loading.value = false
  }
}

function navigateTo(path: string) {
  browseDirectory(path)
}

function goToParent() {
  const parts = currentPath.value.split('/').filter(Boolean)
  parts.pop()
  const parentPath = parts.length > 0 ? `/${parts.join('/')}` : '/'
  browseDirectory(parentPath)
}

function handleEntryClick(entry: FileEntry) {
  if (entry.is_dir) {
    browseDirectory(entry.path)
  } else {
    selectedPath.value = entry.path
  }
}

function handleConfirm() {
  if (selectedPath.value) {
    emit('select', selectedPath.value)
    handleClose()
  }
}

function handleClose() {
  emit('update:modelValue', false)
}

// 当对话框打开时，加载初始目录
watch(
  () => props.modelValue,
  (show) => {
    if (show) {
      browseDirectory(currentPath.value)
    }
  }
)
</script>
