<template>
  <div class="loading-state-wrapper">
    <!-- 预设布局：overview - 4列统计卡片 + 2个图表 -->
    <template v-if="preset === 'overview'">
      <v-row class="mb-6">
        <v-col v-for="i in 4" :key="i" cols="12" sm="6" md="3">
          <v-card>
            <v-skeleton-loader type="article" />
          </v-card>
        </v-col>
      </v-row>
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
    </template>

    <!-- 预设布局：chart-table - 1个图表 + 1个表格 -->
    <template v-else-if="preset === 'chart-table'">
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 预设布局：dual-chart-dual-table - 2个图表 + 2个表格 -->
    <template v-else-if="preset === 'dual-chart-dual-table'">
      <v-row class="mb-6">
        <v-col cols="12" md="6">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card><v-skeleton-loader type="table" /></v-card>
        </v-col>
      </v-row>
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 预设布局：stats-table - 3列统计卡片 + 1个表格 -->
    <template v-else-if="preset === 'stats-table'">
      <v-row class="mb-6">
        <v-col v-for="i in 3" :key="i" cols="12" sm="4">
          <v-card><v-skeleton-loader type="article" /></v-card>
        </v-col>
      </v-row>
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 预设布局：table - 单个表格 -->
    <template v-else-if="preset === 'table'">
      <v-card><v-skeleton-loader type="table" /></v-card>
    </template>

    <!-- 预设布局：spinner - 居中加载指示器 -->
    <template v-else-if="preset === 'spinner'">
      <div class="d-flex justify-center align-center" :style="{ minHeight: minHeight }">
        <v-progress-circular indeterminate color="primary" :size="size" />
      </div>
    </template>

    <!-- 默认：自定义插槽 -->
    <template v-else>
      <slot />
    </template>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  preset?: 'overview' | 'chart-table' | 'dual-chart-dual-table' | 'stats-table' | 'table' | 'spinner' | 'custom'
  minHeight?: string
  size?: number
}>(), {
  preset: 'custom',
  minHeight: '200px',
  size: 48
})
</script>

<style scoped>
.loading-state-wrapper {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>