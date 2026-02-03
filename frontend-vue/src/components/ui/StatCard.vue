<template>
  <v-card class="stat-card pulse-card hover-lift" hover>
    <v-card-text>
      <div class="stat-content">
        <div class="stat-icon" :style="{ background: iconBgColor }">
          <v-icon size="24" :color="iconColor">{{ icon }}</v-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">{{ label }}</div>
          <AnimatedNumber
            v-if="animated && typeof value === 'number'"
            :value="value"
            class="stat-value"
            :class="valueColorClass"
          />
          <div v-else class="stat-value" :class="valueColorClass">
            {{ displayValue }}
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AnimatedNumber from './AnimatedNumber.vue'

interface Props {
  icon: string
  iconColor?: string
  iconBgColor?: string
  label: string
  value: number | string
  valueColor?: 'primary' | 'success' | 'warning' | 'error' | 'info'
  animated?: boolean
  suffix?: string
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'primary',
  iconBgColor: 'rgba(29, 78, 216, 0.1)',
  valueColor: 'primary',
  animated: true,
  suffix: '',
})

const valueColorClass = computed(() => `text-${props.valueColor}`)

const displayValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.suffix ? `${props.value}${props.suffix}` : props.value
  }
  return props.value
})
</script>

<style scoped>
.stat-card {
  cursor: pointer;
  /* Global .v-card style provides base "stereo" look */
}

/* Custom icon container with depth */
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px; /* Slightly softer than base 8px */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  will-change: transform;
  backface-visibility: hidden;
  
  /* Add depth to the icon box itself */
  box-shadow: 
    inset 0 1px 1px rgba(255, 255, 255, 0.1),
    0 4px 10px rgba(0, 0, 0, 0.1);
}

.pulse-card:hover .stat-icon {
  transform: translate3d(0, 0, 0) scale(1.1) rotate(5deg);
  box-shadow: 
    inset 0 1px 1px rgba(255, 255, 255, 0.2),
    0 8px 15px rgba(0, 0, 0, 0.15);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  opacity: 0.7;
  font-weight: 500;
  margin-bottom: 4px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.stat-value {
  font-size: 26px; /* Slightly larger */
  font-weight: 800; /* Bolder */
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
  
  /* Optional: Gradient text for value */
  background: linear-gradient(135deg, currentColor 0%, currentColor 100%);
  -webkit-background-clip: text;
}

/* Dark mode enhancements */
.v-theme--dark .stat-icon {
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 4px 12px rgba(0, 0, 0, 0.3);
}

.v-theme--dark .stat-value {
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .stat-value {
    font-size: 22px;
  }
}
</style>