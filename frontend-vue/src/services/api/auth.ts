import axios from '../axios'
import type { LoginResponse, CheckAuthResponse } from '@/types'

export const authApi = {
  /**
   * 用户登录
   */
  login: (serverId: string, username: string, password: string) =>
    axios.post<LoginResponse>('/auth/login', {
      server_id: serverId,
      username,
      password,
    }),

  /**
   * 用户登出
   */
  logout: () => axios.post('/auth/logout'),

  /**
   * 检查认证状态
   */
  checkAuth: () => axios.get<CheckAuthResponse>('/auth/check'),
}
