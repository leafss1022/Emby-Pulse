<template>
  <v-card
    :class="cardClass"
    :elevation="elevation"
    :loading="loading"
    v-bind="$attrs"
  >
    <!-- 卡片标题 -->
    <v-card-title v-if="title || $slots.title" class="d-flex align-center">
      <slot name="title">
        <span>{{ title }}</span>
      </slot>
      <v-spacer v-if="$slots.actions" />
      <slot name="actions" />
    </v-card-title>

    <!-- 卡片副标题 -->
    <v-card-subtitle v-if="subtitle || $slots.subtitle">
      <slot name="subtitle">
        {{ subtitle }}
      </slot>
    </v-card-subtitle>

    <!-- 卡片内容 -->
    <v-card-text v-if="$slots.default" :class="textClass">
      <slot />
    </v-card-text>

    <!-- 卡片操作按钮区域 -->
    <v-card-actions v-if="$slots.footer">
      <slot name="footer" />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  loading?: boolean
  elevation?: number | string
  noPadding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  elevation: 2,
  loading: false,
  noPadding: false,
})

const cardClass = computed(() => ({
  'mb-4': true,
}))

const textClass = computed(() => ({
  'pa-0': props.noPadding,
}))
</script>

<style scoped>
/* 自定义样式（如果需要） */
</style>
