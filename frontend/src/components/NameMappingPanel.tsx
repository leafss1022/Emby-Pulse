import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Save, Monitor, Smartphone, Loader2, AlertCircle, Check } from 'lucide-react'
import { api } from '@/services/api'
import { cn } from '@/lib/utils'

interface MappingEntry {
  original: string
  display: string
}

interface NameMappingPanelProps {
  isOpen: boolean
  onClose: () => void
  availableClients?: { original: string; display: string }[]
  availableDevices?: { original: string; display: string }[]
}

export function NameMappingPanel({ isOpen, onClose, availableClients = [], availableDevices = [] }: NameMappingPanelProps) {
  const [clientMappings, setClientMappings] = useState<MappingEntry[]>([])
  const [deviceMappings, setDeviceMappings] = useState<MappingEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [activeTab, setActiveTab] = useState<'clients' | 'devices'>('clients')

  // 加载现有映射配置
  useEffect(() => {
    if (isOpen) {
      loadMappings()
    }
  }, [isOpen])

  const loadMappings = async () => {
    setLoading(true)
    try {
      const data = await api.getNameMappings()
      // 转换为数组格式
      setClientMappings(
        Object.entries(data.clients || {}).map(([original, display]) => ({ original, display }))
      )
      setDeviceMappings(
        Object.entries(data.devices || {}).map(([original, display]) => ({ original, display }))
      )
    } catch (error) {
      console.error('加载映射配置失败:', error)
      setMessage({ type: 'error', text: '加载配置失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)
    try {
      // 转换回对象格式
      const mappings = {
        clients: Object.fromEntries(
          clientMappings
            .filter(m => m.original && m.display)
            .map(m => [m.original, m.display])
        ),
        devices: Object.fromEntries(
          deviceMappings
            .filter(m => m.original && m.display)
            .map(m => [m.original, m.display])
        ),
      }
      const result = await api.saveNameMappings(mappings)
      if (result.status === 'ok') {
        setMessage({ type: 'success', text: '保存成功，刷新页面后生效' })
      } else {
        setMessage({ type: 'error', text: result.message || '保存失败' })
      }
    } catch (error) {
      console.error('保存映射配置失败:', error)
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setSaving(false)
    }
  }

  const addClientMapping = (original?: string) => {
    setClientMappings([...clientMappings, { original: original || '', display: '' }])
  }

  const addDeviceMapping = (original?: string) => {
    setDeviceMappings([...deviceMappings, { original: original || '', display: '' }])
  }

  const updateClientMapping = (index: number, field: 'original' | 'display', value: string) => {
    const updated = [...clientMappings]
    updated[index][field] = value
    setClientMappings(updated)
  }

  const updateDeviceMapping = (index: number, field: 'original' | 'display', value: string) => {
    const updated = [...deviceMappings]
    updated[index][field] = value
    setDeviceMappings(updated)
  }

  const removeClientMapping = (index: number) => {
    setClientMappings(clientMappings.filter((_, i) => i !== index))
  }

  const removeDeviceMapping = (index: number) => {
    setDeviceMappings(deviceMappings.filter((_, i) => i !== index))
  }

  // 获取未映射的原始名称
  const unmappedClients = availableClients.filter(
    c => !clientMappings.some(m => m.original === c.original)
  )
  const unmappedDevices = availableDevices.filter(
    d => !deviceMappings.some(m => m.original === d.original)
  )

  if (!isOpen) return null

  return (
    <>
      {/* 遮罩 */}
      <div
        className="fixed inset-0 bg-black/50 z-50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 面板 */}
      <div className="fixed right-0 top-0 h-full w-[480px] max-w-[95vw] bg-[var(--color-content1)] border-l border-[var(--color-border)] z-50 overflow-hidden flex flex-col shadow-2xl">
        {/* 头部 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-content2)]">
          <div className="flex items-center gap-2">
            <span className="font-medium text-[var(--color-foreground)]">名称映射设置</span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[var(--color-hover-overlay)] transition-colors text-[var(--color-foreground)]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab 切换 */}
        <div className="flex border-b border-[var(--color-border)]">
          <button
            onClick={() => setActiveTab('clients')}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors',
              activeTab === 'clients'
                ? 'text-primary border-b-2 border-primary bg-primary/5'
                : 'text-[var(--color-text-muted)] hover:text-[var(--color-foreground)]'
            )}
          >
            <Monitor className="w-4 h-4" />
            客户端 ({clientMappings.length})
          </button>
          <button
            onClick={() => setActiveTab('devices')}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors',
              activeTab === 'devices'
                ? 'text-primary border-b-2 border-primary bg-primary/5'
                : 'text-[var(--color-text-muted)] hover:text-[var(--color-foreground)]'
            )}
          >
            <Smartphone className="w-4 h-4" />
            设备 ({deviceMappings.length})
          </button>
        </div>

        {/* 内容 */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : (
            <>
              {activeTab === 'clients' && (
                <div className="space-y-4">
                  {/* 说明 */}
                  <p className="text-xs text-[var(--color-text-muted)]">
                    将长客户端名称映射为简短的显示名称。左侧填写原始名称，右侧填写显示名称。
                  </p>

                  {/* 映射列表 */}
                  <div className="space-y-2">
                    {clientMappings.map((mapping, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <input
                          type="text"
                          value={mapping.original}
                          onChange={(e) => updateClientMapping(index, 'original', e.target.value)}
                          placeholder="原始名称"
                          className="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-primary"
                        />
                        <span className="text-[var(--color-text-muted)]">→</span>
                        <input
                          type="text"
                          value={mapping.display}
                          onChange={(e) => updateClientMapping(index, 'display', e.target.value)}
                          placeholder="显示名称"
                          className="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-primary"
                        />
                        <button
                          onClick={() => removeClientMapping(index)}
                          className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* 添加按钮 */}
                  <button
                    onClick={() => addClientMapping()}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    添加映射
                  </button>

                  {/* 未映射的名称快捷添加 */}
                  {unmappedClients.length > 0 && (
                    <div className="mt-6 pt-4 border-t border-[var(--color-border)]">
                      <p className="text-xs text-[var(--color-text-muted)] mb-2">
                        点击下方名称快速添加映射:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {unmappedClients.map((client) => (
                          <button
                            key={client.original}
                            onClick={() => addClientMapping(client.original)}
                            className="px-2 py-1 text-xs bg-[var(--color-content2)] text-[var(--color-foreground)] rounded-lg hover:bg-[var(--color-content3)] transition-colors border border-[var(--color-border)] truncate max-w-[200px]"
                            title={client.original}
                          >
                            {client.original}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'devices' && (
                <div className="space-y-4">
                  {/* 说明 */}
                  <p className="text-xs text-[var(--color-text-muted)]">
                    将长设备名称映射为简短的显示名称。左侧填写原始名称，右侧填写显示名称。
                  </p>

                  {/* 映射列表 */}
                  <div className="space-y-2">
                    {deviceMappings.map((mapping, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <input
                          type="text"
                          value={mapping.original}
                          onChange={(e) => updateDeviceMapping(index, 'original', e.target.value)}
                          placeholder="原始名称"
                          className="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-primary"
                        />
                        <span className="text-[var(--color-text-muted)]">→</span>
                        <input
                          type="text"
                          value={mapping.display}
                          onChange={(e) => updateDeviceMapping(index, 'display', e.target.value)}
                          placeholder="显示名称"
                          className="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-primary"
                        />
                        <button
                          onClick={() => removeDeviceMapping(index)}
                          className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* 添加按钮 */}
                  <button
                    onClick={() => addDeviceMapping()}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    添加映射
                  </button>

                  {/* 未映射的名称快捷添加 */}
                  {unmappedDevices.length > 0 && (
                    <div className="mt-6 pt-4 border-t border-[var(--color-border)]">
                      <p className="text-xs text-[var(--color-text-muted)] mb-2">
                        点击下方名称快速添加映射:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {unmappedDevices.map((device) => (
                          <button
                            key={device.original}
                            onClick={() => addDeviceMapping(device.original)}
                            className="px-2 py-1 text-xs bg-[var(--color-content2)] text-[var(--color-foreground)] rounded-lg hover:bg-[var(--color-content3)] transition-colors border border-[var(--color-border)] truncate max-w-[200px]"
                            title={device.original}
                          >
                            {device.original}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* 底部操作栏 */}
        <div className="border-t border-[var(--color-border)] p-4 bg-[var(--color-content2)]">
          {message && (
            <div
              className={cn(
                'flex items-center gap-2 px-3 py-2 mb-3 text-sm rounded-lg',
                message.type === 'success'
                  ? 'bg-green-500/10 text-green-500'
                  : 'bg-red-500/10 text-red-500'
              )}
            >
              {message.type === 'success' ? (
                <Check className="w-4 h-4" />
              ) : (
                <AlertCircle className="w-4 h-4" />
              )}
              {message.text}
            </div>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {saving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            保存配置
          </button>
        </div>
      </div>
    </>
  )
}
