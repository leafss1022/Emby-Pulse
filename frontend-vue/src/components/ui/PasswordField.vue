<template>
  <v-text-field
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :label="label"
    :prepend-inner-icon="prependIcon"
    :variant="variant"
    :density="density"
    :type="showPassword ? 'text' : 'password'"
    :rules="rules"
    :disabled="disabled"
    :placeholder="placeholder"
    :hint="hint"
    :persistent-hint="persistentHint"
    :class="fieldClass"
  >
    <template v-if="$slots.prepend" #prepend>
      <slot name="prepend" />
    </template>
    <template #append-inner>
      <v-btn
        :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
        variant="text"
        size="small"
        tabindex="-1"
        @click="showPassword = !showPassword"
      />
    </template>
    <template v-if="$slots.append" #append>
      <slot name="append" />
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  modelValue: string
  label?: string
  prependIcon?: string
  variant?: 'outlined' | 'filled' | 'underlined' | 'plain' | 'solo' | 'solo-inverted' | 'solo-filled'
  density?: 'default' | 'comfortable' | 'compact'
  rules?: ((v: string) => boolean | string)[]
  disabled?: boolean
  placeholder?: string
  hint?: string
  persistentHint?: boolean
  fieldClass?: string
}

withDefaults(defineProps<Props>(), {
  label: '密码',
  prependIcon: 'mdi-lock',
  variant: 'outlined',
  density: 'default',
  rules: () => [],
  disabled: false,
  placeholder: '',
  hint: '',
  persistentHint: false,
  fieldClass: '',
})

defineEmits<{
  'update:modelValue': [value: string]
}>()

const showPassword = ref(false)
</script>
