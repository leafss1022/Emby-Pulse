<template>
  <v-row>
    <v-col cols="12">
      <v-alert :type="type" variant="tonal">
        {{ message }}
      </v-alert>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  message?: string
  type?: 'info' | 'warning' | 'error' | 'success'
}>(), {
  message: '暂无数据',
  type: 'info'
})
</script>
