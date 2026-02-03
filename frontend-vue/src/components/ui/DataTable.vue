<template>
  <!-- 桌面端表格 -->
  <v-table v-if="!mobile" density="comfortable">
    <thead>
      <tr>
        <th
          v-for="col in columns"
          :key="col.key"
          :class="col.align === 'right' ? 'text-right' : ''"
        >
          {{ col.label }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in data" :key="getItemKey(item, index)">
        <td
          v-for="col in columns"
          :key="col.key"
          :class="col.align === 'right' ? 'text-right' : ''"
        >
          <slot :name="`cell-${col.key}`" :item="item" :value="item[col.key]">
            {{ formatValue(item[col.key], col) }}
          </slot>
        </td>
      </tr>
    </tbody>
  </v-table>

  <!-- 移动端列表 -->
  <v-list v-else>
    <v-list-item
      v-for="(item, index) in data"
      :key="getItemKey(item, index)"
      class="mb-2"
    >
      <template #prepend>
        <slot name="mobile-prepend" :item="item">
          <v-icon :icon="mobileIcon" size="32" class="mr-3" />
        </slot>
      </template>
      <v-list-item-title class="font-weight-medium mb-1">
        <slot name="mobile-title" :item="item">
          {{ columns[0] ? item[columns[0].key] : '' }}
        </slot>
      </v-list-item-title>
      <v-list-item-subtitle>
        <slot name="mobile-subtitle" :item="item">
          <div class="d-flex flex-column">
            <span v-for="col in columns.slice(1)" :key="col.key">
              {{ col.label }}: {{ formatValue(item[col.key], col) }}
            </span>
          </div>
        </slot>
      </v-list-item-subtitle>
    </v-list-item>
  </v-list>
</template>

<script setup lang="ts">
import { useDisplay } from 'vuetify'

export interface Column {
  key: string
  label: string
  align?: 'left' | 'right' | 'center'
  format?: (value: unknown) => string
}

interface Props {
  columns: Column[]
  data: Record<string, unknown>[]
  itemKey?: string
  mobileIcon?: string
}

const props = withDefaults(defineProps<Props>(), {
  itemKey: 'id',
  mobileIcon: 'mdi-circle',
})

const { mobile } = useDisplay()

function getItemKey(item: Record<string, unknown>, index: number): string {
  return String(item[props.itemKey] ?? index)
}

function formatValue(value: unknown, col: Column): string {
  if (col.format) {
    return col.format(value)
  }
  if (value === null || value === undefined) {
    return '-'
  }
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return String(value)
}
</script>

<style scoped>
/* 移动端列表项间距 */
.v-list-item {
  border-radius: 8px;
}
</style>
