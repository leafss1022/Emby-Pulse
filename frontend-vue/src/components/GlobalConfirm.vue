<template>
  <v-dialog
    v-model="confirmState.show"
    max-width="400"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon icon="mdi-help-circle" color="warning" class="mr-2" />
        {{ confirmState.title }}
      </v-card-title>

      <v-card-text>
        {{ confirmState.message }}
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="handleCancel"
        >
          取消
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="handleConfirm"
        >
          确定
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { confirmState } from '@/composables/useConfirm'

function handleConfirm() {
  confirmState.show = false
  confirmState.resolve?.(true)
}

function handleCancel() {
  confirmState.show = false
  confirmState.resolve?.(false)
}
</script>
