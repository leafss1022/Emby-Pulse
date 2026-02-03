<template>
  <v-dialog
    v-model="internalShow"
    max-width="800"
    @click:outside="handleClose"
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>{{ title }}</span>
        <v-spacer />
        <v-btn
          icon="mdi-close"
          variant="text"
          size="small"
          @click="handleClose"
        />
      </v-card-title>

      <v-card-text class="pa-0">
        <v-img
          :src="imageUrl"
          :aspect-ratio="aspectRatio"
          cover
        >
          <template #placeholder>
            <v-skeleton-loader type="image" height="600" />
          </template>
        </v-img>
      </v-card-text>

      <v-card-text v-if="description">
        <div class="text-body-2">{{ description }}</div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  imageUrl?: string
  title?: string
  description?: string
  aspectRatio?: number
}

const props = withDefaults(defineProps<Props>(), {
  aspectRatio: 16 / 9,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
}>()

const internalShow = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}
</script>
