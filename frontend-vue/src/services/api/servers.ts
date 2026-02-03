import axios from '../axios'
import type { Server, ServerConfig, ServersResponse } from '@/types'

export const serversApi = {
  /**
   * 获取服务器列表
   */
  getServers: () => axios.get<ServersResponse>('/servers'),

  /**
   * 添加服务器
   */
  addServer: (config: ServerConfig) =>
    axios.post<Server>('/servers', config),

  /**
   * 更新服务器
   */
  updateServer: (id: string, config: ServerConfig) =>
    axios.put<Server>(`/servers/${id}`, config),

  /**
   * 删除服务器
   */
  deleteServer: (id: string) => axios.delete(`/servers/${id}`),
}
