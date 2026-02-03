<template>
  <v-skeleton-loader
    :type="type"
    :width="width"
    :height="height"
    :loading="loading"
    v-bind="$attrs"
  >
    <slot />
  </v-skeleton-loader>
</template>

<script setup lang="ts">
interface Props {
  type?:
    | 'text'
    | 'avatar'
    | 'card'
    | 'image'
    | 'article'
    | 'list-item'
    | 'list-item-avatar'
    | 'table'
    | string
  width?: string | number
  height?: string | number
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  type: 'text',
  loading: true,
})
</script>
