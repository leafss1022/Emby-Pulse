<template>
  <div ref="target" class="lazy-image-container" :style="containerStyle">
    <Transition name="fade">
      <img
        v-if="isLoaded && !hasError"
        :src="src"
        :alt="alt"
        :class="imageClass"
        class="lazy-image"
        @load="onLoad"
        @error="onError"
      />
    </Transition>

    <!-- 占位符 -->
    <div v-if="!isLoaded && !hasError" class="lazy-image-placeholder">
      <slot name="placeholder">
        <v-progress-circular
          v-if="isVisible"
          indeterminate
          size="32"
          color="primary"
        />
        <v-icon v-else icon="mdi-image" size="32" opacity="0.3" />
      </slot>
    </div>

    <!-- 加载失败 -->
    <div v-if="hasError" class="lazy-image-error">
      <slot name="error">
        <v-icon icon="mdi-image-off" size="32" opacity="0.3" />
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'

interface Props {
  src?: string
  alt?: string
  width?: string | number
  height?: string | number
  aspectRatio?: string | number
  cover?: boolean
  rootMargin?: string
}

const props = withDefaults(defineProps<Props>(), {
  src: '',
  alt: '',
  width: '100%',
  height: '100%',
  aspectRatio: undefined,
  cover: true,
  rootMargin: '50px',
})

const target = ref<HTMLElement>()
const isVisible = ref(false)
const isLoaded = ref(false)
const hasError = ref(false)

// 容器样式
const containerStyle = computed(() => {
  const style: Record<string, string> = {
    width: typeof props.width === 'number' ? `${props.width}px` : props.width,
    height: typeof props.height === 'number' ? `${props.height}px` : props.height,
    position: 'relative',
    overflow: 'hidden',
  }

  if (props.aspectRatio) {
    style.aspectRatio = String(props.aspectRatio)
    style.height = 'auto'
  }

  return style
})

// 图片样式类
const imageClass = computed(() => {
  return props.cover ? 'object-cover' : 'object-contain'
})

// 监听元素进入视口
useIntersectionObserver(
  target,
  ([entry]) => {
    if (entry && entry.isIntersecting && !isLoaded.value && !hasError.value) {
      isVisible.value = true
    }
  },
  {
    rootMargin: props.rootMargin,
  }
)

// 监听 src 变化,重置状态
watch(
  () => props.src,
  () => {
    isLoaded.value = false
    hasError.value = false
    if (isVisible.value) {
      // 如果已经可见,重新加载
      loadImage()
    }
  }
)

// 加载图片
watch(isVisible, (visible) => {
  if (visible && props.src && !isLoaded.value && !hasError.value) {
    loadImage()
  }
})

function loadImage() {
  if (!props.src) {
    hasError.value = true
    return
  }

  const img = new Image()
  img.src = props.src
  img.onload = () => {
    isLoaded.value = true
  }
  img.onerror = () => {
    hasError.value = true
  }
}

function onLoad() {
  isLoaded.value = true
}

function onError() {
  hasError.value = true
}
</script>

<style scoped>
.lazy-image-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgb(var(--v-theme-surface-variant));
}

.lazy-image {
  width: 100%;
  height: 100%;
  display: block;
}

.object-cover {
  object-fit: cover;
}

.object-contain {
  object-fit: contain;
}

.lazy-image-placeholder,
.lazy-image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  top: 0;
  left: 0;
}

/* 淡入动画 */
.fade-enter-active {
  transition: opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.fade-enter-from {
  opacity: 0;
}

.fade-enter-to {
  opacity: 1;
}
</style>
