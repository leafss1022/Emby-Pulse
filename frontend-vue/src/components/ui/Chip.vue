<template>
  <v-chip
    :color="color"
    :size="size"
    :closable="closable"
    :variant="variant"
    v-bind="$attrs"
    @click="handleClick"
    @click:close="handleClose"
  >
    <slot>{{ label }}</slot>
  </v-chip>
</template>

<script setup lang="ts">
interface Props {
  label?: string
  color?: string
  size?: 'x-small' | 'small' | 'default' | 'large' | 'x-large'
  closable?: boolean
  variant?: 'flat' | 'elevated' | 'tonal' | 'outlined' | 'text' | 'plain'
}

withDefaults(defineProps<Props>(), {
  size: 'default',
  closable: false,
  variant: 'flat',
})

const emit = defineEmits<{
  click: [event: MouseEvent | KeyboardEvent]
  close: []
}>()

function handleClick(event: MouseEvent | KeyboardEvent) {
  emit('click', event)
}

function handleClose() {
  emit('close')
}
</script>
