<template>
  <div class="progress-container">
    <v-progress-linear
      :model-value="percentage"
      :color="color"
      :height="height"
      :striped="striped"
      :indeterminate="indeterminate"
      v-bind="$attrs"
    >
      <template v-if="showText && !indeterminate">
        <strong>{{ percentage }}%</strong>
      </template>
    </v-progress-linear>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value?: number
  total?: number
  percentage?: number
  color?: string
  height?: string | number
  showText?: boolean
  striped?: boolean
  indeterminate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  value: 0,
  total: 100,
  color: 'primary',
  height: 4,
  showText: false,
  striped: false,
  indeterminate: false,
})

const percentage = computed(() => {
  if (props.percentage !== undefined) {
    return Math.min(Math.max(props.percentage, 0), 100)
  }

  if (props.total === 0) return 0
  return Math.min(Math.max((props.value / props.total) * 100, 0), 100)
})
</script>

<style scoped>
.progress-container {
  width: 100%;
}
</style>
