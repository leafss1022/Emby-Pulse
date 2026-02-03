<template>
  <Teleport to="body">
    <v-snackbar
      v-model="toastState.show"
      :color="toastState.type"
      :timeout="toastState.duration"
      location="top right"
      variant="elevated"
    >
      <div class="d-flex align-center">
        <v-icon
          :icon="toastIcon"
          class="mr-2"
        />
        {{ toastState.message }}
      </div>

      <template #actions>
        <v-btn
          icon="mdi-close"
          variant="text"
          size="small"
          @click="toastState.show = false"
        />
      </template>
    </v-snackbar>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { toastState } from '@/composables/useToast'

const toastIcon = computed(() => {
  switch (toastState.type) {
    case 'success':
      return 'mdi-check-circle'
    case 'error':
      return 'mdi-alert-circle'
    case 'warning':
      return 'mdi-alert'
    case 'info':
      return 'mdi-information'
    default:
      return 'mdi-information'
  }
})
</script>
