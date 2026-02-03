<template>
  <span>{{ displayValue }}</span>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

interface Props {
  value: number
  duration?: number
  decimals?: number
  format?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  duration: 1000,
  decimals: 0,
  format: false,
})

const displayValue = ref('0')

let animationFrame: number | null = null
let startTime: number | null = null
let startValue = 0

function animate(timestamp: number) {
  if (!startTime) startTime = timestamp

  const progress = Math.min((timestamp - startTime) / props.duration, 1)
  const currentValue = startValue + (props.value - startValue) * easeOutCubic(progress)

  displayValue.value = formatNumber(currentValue)

  if (progress < 1) {
    animationFrame = requestAnimationFrame(animate)
  } else {
    startTime = null
  }
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

function formatNumber(num: number): string {
  const fixed = num.toFixed(props.decimals)

  if (props.format) {
    return parseFloat(fixed).toLocaleString('zh-CN', {
      minimumFractionDigits: props.decimals,
      maximumFractionDigits: props.decimals,
    })
  }

  return fixed
}

function startAnimation() {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }

  startValue = parseFloat(displayValue.value.replace(/,/g, '')) || 0
  startTime = null
  animationFrame = requestAnimationFrame(animate)
}

watch(
  () => props.value,
  () => {
    startAnimation()
  }
)

onMounted(() => {
  displayValue.value = formatNumber(props.value)
})
</script>
