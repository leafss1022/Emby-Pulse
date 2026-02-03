import { reactive } from 'vue'

interface ToastState {
  show: boolean
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
  duration: number
}

// 全局状态（跨组件共享）
export const toastState = reactive<ToastState>({
  show: false,
  message: '',
  type: 'info',
  duration: 3000,
})

/**
 * Toast 消息提示 Composable
 * @returns Toast 相关方法
 */
export function useToast() {
  function showToast(
    message: string,
    type: 'success' | 'error' | 'info' | 'warning' = 'info',
    duration: number = 3000
  ) {
    toastState.show = true
    toastState.message = message
    toastState.type = type
    toastState.duration = duration
  }

  function success(message: string, duration?: number) {
    showToast(message, 'success', duration)
  }

  function error(message: string, duration?: number) {
    showToast(message, 'error', duration)
  }

  function info(message: string, duration?: number) {
    showToast(message, 'info', duration)
  }

  function warning(message: string, duration?: number) {
    showToast(message, 'warning', duration)
  }

  function close() {
    toastState.show = false
  }

  return {
    showToast,
    success,
    error,
    info,
    warning,
    close,
  }
}
