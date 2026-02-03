<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    :width="size"
    :height="size"
    role="img"
    :aria-hidden="title ? 'false' : 'true'"
    focusable="false"
  >
    <title v-if="title">{{ title }}</title>
    <path
      d="M7 6.8c0-.7.8-1.1 1.4-.7l7.1 4.2c.6.3.6 1.1 0 1.4l-7.1 4.2c-.6.4-1.4 0-1.4-.7V6.8Z"
      fill="currentColor"
    />
    <rect x="16.2" y="11.2" width="1.9" height="6.8" rx="0.95" fill="currentColor" />
    <rect x="18.8" y="8.2" width="1.9" height="9.8" rx="0.95" fill="currentColor" />
    <rect x="21.4" y="13" width="1.9" height="5" rx="0.95" fill="currentColor" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: number
    title?: string
  }>(),
  {
    size: 20,
    title: undefined,
  },
)
</script>

