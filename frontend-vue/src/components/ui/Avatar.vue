<template>
  <v-avatar
    :size="size"
    :color="color"
    v-bind="$attrs"
  >
    <v-img
      v-if="src"
      :src="src"
      :alt="alt"
      cover
    />
    <span v-else-if="text" class="text-h6">
      {{ getInitials(text) }}
    </span>
    <slot v-else />
  </v-avatar>
</template>

<script setup lang="ts">
interface Props {
  src?: string
  text?: string
  alt?: string
  size?: string | number
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 40,
  color: 'primary',
})

/**
 * 获取名称的首字母
 */
function getInitials(name: string): string {
  if (!name) return ''

  const words = name.trim().split(/\s+/)
  if (words.length === 1) {
    // 单个词，取前两个字符
    return name.substring(0, 2).toUpperCase()
  }

  // 多个词，取每个词的首字母
  return words
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()
}
</script>
