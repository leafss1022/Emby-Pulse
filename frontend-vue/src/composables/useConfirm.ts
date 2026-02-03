import { reactive } from 'vue'

interface ConfirmState {
  show: boolean
  title: string
  message: string
  resolve: ((value: boolean) => void) | null
}

// 全局状态（跨组件共享）
export const confirmState = reactive<ConfirmState>({
  show: false,
  title: '',
  message: '',
  resolve: null,
})

/**
 * 确认对话框 Composable
 * @returns 确认对话框相关方法
 */
export function useConfirm() {
  function confirm(title: string, message: string): Promise<boolean> {
    return new Promise((resolve) => {
      confirmState.show = true
      confirmState.title = title
      confirmState.message = message
      confirmState.resolve = resolve
    })
  }

  return {
    confirm,
  }
}
