<template>
  <v-dialog
    v-model="internalShow"
    :width="width"
    :max-width="maxWidth"
    :persistent="persistent"
    :scrollable="scrollable"
    v-bind="$attrs"
  >
    <v-card>
      <!-- 标题栏 -->
      <v-card-title v-if="title || $slots.title" class="d-flex align-center">
        <slot name="title">
          <span>{{ title }}</span>
        </slot>
        <v-spacer />
        <v-btn
          v-if="showClose"
          icon="mdi-close"
          variant="text"
          size="small"
          @click="handleClose"
        />
      </v-card-title>

      <v-divider v-if="title || $slots.title" />

      <!-- 内容区域 -->
      <v-card-text :class="textClass">
        <slot />
      </v-card-text>

      <!-- 底部操作按钮 -->
      <v-card-actions v-if="$slots.footer || showDefaultFooter">
        <slot name="footer">
          <v-spacer />
          <v-btn
            v-if="showCancel"
            variant="text"
            @click="handleCancel"
          >
            {{ cancelText }}
          </v-btn>
          <v-btn
            v-if="showConfirm"
            color="primary"
            variant="elevated"
            @click="handleConfirm"
          >
            {{ confirmText }}
          </v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  width?: string | number
  maxWidth?: string | number
  persistent?: boolean
  scrollable?: boolean
  showClose?: boolean
  showDefaultFooter?: boolean
  showCancel?: boolean
  showConfirm?: boolean
  cancelText?: string
  confirmText?: string
  noPadding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: 600,
  maxWidth: '90vw',
  persistent: false,
  scrollable: true,
  showClose: true,
  showDefaultFooter: false,
  showCancel: true,
  showConfirm: true,
  cancelText: '取消',
  confirmText: '确定',
  noPadding: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
  cancel: []
  confirm: []
}>()

const internalShow = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const textClass = computed(() => ({
  'pa-0': props.noPadding,
}))

function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

function handleCancel() {
  emit('update:modelValue', false)
  emit('cancel')
}

function handleConfirm() {
  emit('confirm')
}
</script>
