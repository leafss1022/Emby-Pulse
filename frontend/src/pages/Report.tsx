import { useState, useEffect, useMemo } from 'react'
import { Card, Avatar } from '@/components/ui'
import { Send, Bot, Clock, Users, Eye, CheckCircle, XCircle, Loader2, Calendar, CalendarDays, CalendarRange, MessageCircle, Trash2, RefreshCw, Link2, Search } from 'lucide-react'
import { api, type ReportConfig, type ReportConfigResponse, type ReportPeriod, type TgBotConfigResponse, type TgBinding } from '@/services/api'
import { cn } from '@/lib/utils'
import { useServer } from '@/contexts/ServerContext'

const defaultSchedule = {
  daily: { enabled: false, cron: '0 21 * * *' },
  weekly: { enabled: false, cron: '0 21 * * 0' },
  monthly: { enabled: false, cron: '0 21 1 * *' },
}

export function Report() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [previewPeriod, setPreviewPeriod] = useState<ReportPeriod>('weekly')
  const [sendPeriod, setSendPeriod] = useState<ReportPeriod>('weekly')

  const { currentServer } = useServer()
  const [config, setConfig] = useState<ReportConfig>({
    telegram: { enabled: false, bot_token: '', chat_id: '', proxy: '' },
    schedule: defaultSchedule,
    users: [],
    content_count: 5,
  })
  const [allUsers, setAllUsers] = useState<Array<{ user_id: string; username: string }>>([])
  const [previewKey, setPreviewKey] = useState(0)

  // Bot 管理相关状态
  const [botConfig, setBotConfig] = useState<TgBotConfigResponse | null>(null)
  const [botToken, setBotToken] = useState('')
  const [botDefaultPeriod, setBotDefaultPeriod] = useState('monthly')
  const [botEnabled, setBotEnabled] = useState(false)
  const [bindings, setBindings] = useState<TgBinding[]>([])
  const [botSaving, setBotSaving] = useState(false)
  const [botRestarting, setBotRestarting] = useState(false)
  const [deletingBinding, setDeletingBinding] = useState<string | null>(null)
  const [bindingSearch, setBindingSearch] = useState('')

  useEffect(() => {
    loadConfig()
    loadBotConfig()
    loadBindings()
  }, [currentServer?.id])

  const loadConfig = async () => {
    try {
      const data: ReportConfigResponse = await api.getReportConfig(currentServer?.id)
      setConfig({
        ...data.config,
        schedule: { ...defaultSchedule, ...data.config.schedule }
      })
      setAllUsers(data.all_users)
    } catch (e) {
      console.error('Failed to load config:', e)
    } finally {
      setLoading(false)
    }
  }

  const loadBotConfig = async () => {
    try {
      const data = await api.getTgBotConfig()
      setBotConfig(data)
      setBotEnabled(data.enabled)
      setBotDefaultPeriod(data.default_period || 'monthly')
    } catch (e) {
      console.error('Failed to load bot config:', e)
    }
  }

  const loadBindings = async () => {
    try {
      const data = await api.getTgBindings(currentServer?.id)
      setBindings(data.bindings)
    } catch (e) {
      console.error('Failed to load bindings:', e)
    }
  }

  // 根据搜索词筛选绑定
  const filteredBindings = useMemo(() => {
    if (!bindingSearch.trim()) {
      return bindings
    }
    const search = bindingSearch.toLowerCase().trim()
    return bindings.filter(b =>
      b.emby_username?.toLowerCase().includes(search) ||
      b.tg_username?.toLowerCase().includes(search) ||
      b.tg_first_name?.toLowerCase().includes(search) ||
      b.tg_user_id?.includes(search)
    )
  }, [bindings, bindingSearch])

  const handleSaveBotConfig = async () => {
    setBotSaving(true)
    setMessage(null)
    try {
      const configToSave: { enabled?: boolean; bot_token?: string; default_period?: string } = {
        enabled: botEnabled,
        default_period: botDefaultPeriod,
      }
      if (botToken) {
        configToSave.bot_token = botToken
      }
      const result = await api.saveTgBotConfig(configToSave)
      if (result.success) {
        setMessage({ type: 'success', text: 'Bot 配置已保存，请重启 Bot 生效' })
        setBotToken('')
        await loadBotConfig()
      } else {
        setMessage({ type: 'error', text: '保存失败' })
      }
    } catch (e) {
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setBotSaving(false)
    }
  }

  const handleRestartBot = async () => {
    setBotRestarting(true)
    setMessage(null)
    try {
      const result = await api.restartTgBot()
      setMessage({
        type: result.is_running ? 'success' : 'error',
        text: result.message || (result.is_running ? 'Bot 已启动' : 'Bot 启动失败')
      })
      await loadBotConfig()
    } catch (e) {
      setMessage({ type: 'error', text: '重启失败' })
    } finally {
      setBotRestarting(false)
    }
  }

  const handleDeleteBinding = async (tgUserId: string) => {
    setDeletingBinding(tgUserId)
    try {
      const result = await api.deleteTgBinding(tgUserId)
      if (result.success) {
        setBindings(prev => prev.filter(b => b.tg_user_id !== tgUserId))
        setMessage({ type: 'success', text: '绑定已删除' })
      } else {
        setMessage({ type: 'error', text: '删除失败' })
      }
    } catch (e) {
      setMessage({ type: 'error', text: '删除失败' })
    } finally {
      setDeletingBinding(null)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)
    try {
      // 保存时传递当前服务器ID
      const result = await api.saveReportConfig({
        ...config,
        server_id: currentServer?.id || ''
      })
      if (result.success) {
        setMessage({ type: 'success', text: '配置已保存' })
        setPreviewKey(prev => prev + 1)
      } else {
        setMessage({ type: 'error', text: '保存失败' })
      }
    } catch (error) {
      console.error('Failed to save report config:', error)
      setMessage({ type: 'error', text: '保存失败' })
    } finally {
      setSaving(false)
    }
  }

  const handleTestTelegram = async () => {
    setTesting(true)
    setMessage(null)
    try {
      const result = await api.testTelegram(currentServer?.id)
      if (result.success) {
        setMessage({ type: 'success', text: '测试消息发送成功！' })
      } else {
        setMessage({ type: 'error', text: result.error || '发送失败' })
      }
    } catch (error) {
      console.error('Failed to send telegram test message:', error)
      setMessage({ type: 'error', text: '测试失败' })
    } finally {
      setTesting(false)
    }
  }

  const handleSendNow = async () => {
    setSending(true)
    setMessage(null)
    try {
      const result = await api.sendReport(sendPeriod, currentServer?.id)
      setMessage({
        type: result.success ? 'success' : 'error',
        text: result.message || result.error || '发送失败'
      })
    } catch (error) {
      console.error('Failed to send report:', error)
      setMessage({ type: 'error', text: '发送失败' })
    } finally {
      setSending(false)
    }
  }

  const toggleUser = (userId: string) => {
    setConfig(prev => ({
      ...prev,
      users: prev.users.includes(userId)
        ? prev.users.filter(id => id !== userId)
        : [...prev.users, userId]
    }))
  }

  const selectAllUsers = () => {
    setConfig(prev => ({ ...prev, users: [] }))
  }

  const updateSchedule = (period: 'daily' | 'weekly' | 'monthly', field: 'enabled' | 'cron', value: boolean | string) => {
    setConfig(prev => ({
      ...prev,
      schedule: {
        ...prev.schedule,
        [period]: {
          ...prev.schedule[period],
          [field]: value
        }
      }
    }))
  }

  const periodLabels: Record<ReportPeriod, string> = {
    daily: '今日',
    weekly: '本周',
    monthly: '本月'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 消息提示 */}
      {message && (
        <div className={cn(
          'flex items-center gap-2 p-4 rounded-xl',
          message.type === 'success' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
        )}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Telegram 配置 */}
        <Card className="p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <Bot className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <h3 className="font-semibold">Telegram 推送</h3>
              <p className="text-xs text-[var(--color-text-secondary)]">配置 Bot 发送观影报告</p>
            </div>
          </div>

          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={config.telegram.enabled}
                onChange={e => setConfig(prev => ({
                  ...prev,
                  telegram: { ...prev.telegram, enabled: e.target.checked }
                }))}
                className="w-4 h-4 rounded border-zinc-600 text-primary focus:ring-primary"
              />
              <span className="text-sm">启用 Telegram 推送</span>
            </label>

            <div>
              <label className="block text-xs text-[var(--color-text-secondary)] mb-1">Bot Token</label>
              <input
                type="password"
                value={config.telegram.bot_token}
                onChange={e => setConfig(prev => ({
                  ...prev,
                  telegram: { ...prev.telegram, bot_token: e.target.value }
                }))}
                placeholder="从 @BotFather 获取"
                className="w-full px-3 py-2 bg-content1 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs text-[var(--color-text-secondary)] mb-1">Chat ID</label>
              <input
                type="text"
                value={config.telegram.chat_id}
                onChange={e => setConfig(prev => ({
                  ...prev,
                  telegram: { ...prev.telegram, chat_id: e.target.value }
                }))}
                placeholder="用户或群组 ID"
                className="w-full px-3 py-2 bg-content1 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs text-[var(--color-text-secondary)] mb-1">代理地址（可选）</label>
              <input
                type="text"
                value={config.telegram.proxy}
                onChange={e => setConfig(prev => ({
                  ...prev,
                  telegram: { ...prev.telegram, proxy: e.target.value }
                }))}
                placeholder="http://127.0.0.1:7890 或 socks5://127.0.0.1:1080"
                className="w-full px-3 py-2 bg-content1 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <button
              onClick={handleTestTelegram}
              disabled={testing || !config.telegram.enabled || !config.telegram.bot_token || !config.telegram.chat_id}
              className="w-full py-2 px-4 bg-blue-500/20 text-blue-500 rounded-lg text-sm font-medium hover:bg-blue-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {testing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              发送测试消息
            </button>
          </div>
        </Card>

        {/* 定时任务配置 */}
        <Card className="p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
              <Clock className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <h3 className="font-semibold">定时推送</h3>
              <p className="text-xs text-[var(--color-text-secondary)]">配置每日/每周/每月自动推送</p>
            </div>
          </div>

          <div className="space-y-4">
            {/* 每日报告 */}
            <div className="p-3 rounded-lg bg-content2/50 space-y-2">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-orange-400" />
                <label className="flex items-center gap-2 cursor-pointer flex-1">
                  <input
                    type="checkbox"
                    checked={config.schedule.daily.enabled}
                    onChange={e => updateSchedule('daily', 'enabled', e.target.checked)}
                    className="w-4 h-4 rounded border-zinc-600 text-primary focus:ring-primary"
                  />
                  <span className="text-sm font-medium">每日报告</span>
                </label>
              </div>
              <input
                type="text"
                value={config.schedule.daily.cron}
                onChange={e => updateSchedule('daily', 'cron', e.target.value)}
                placeholder="0 21 * * *"
                disabled={!config.schedule.daily.enabled}
                className="w-full px-3 py-1.5 bg-content1 border border-[var(--color-border)] rounded-lg text-xs focus:outline-none focus:border-primary font-mono disabled:opacity-50"
              />
              <p className="text-xs text-[var(--color-text-secondary)]">推送当天的观影数据</p>
            </div>

            {/* 每周报告 */}
            <div className="p-3 rounded-lg bg-content2/50 space-y-2">
              <div className="flex items-center gap-2">
                <CalendarDays className="w-4 h-4 text-blue-400" />
                <label className="flex items-center gap-2 cursor-pointer flex-1">
                  <input
                    type="checkbox"
                    checked={config.schedule.weekly.enabled}
                    onChange={e => updateSchedule('weekly', 'enabled', e.target.checked)}
                    className="w-4 h-4 rounded border-zinc-600 text-primary focus:ring-primary"
                  />
                  <span className="text-sm font-medium">每周报告</span>
                </label>
              </div>
              <input
                type="text"
                value={config.schedule.weekly.cron}
                onChange={e => updateSchedule('weekly', 'cron', e.target.value)}
                placeholder="0 21 * * 0"
                disabled={!config.schedule.weekly.enabled}
                className="w-full px-3 py-1.5 bg-content1 border border-[var(--color-border)] rounded-lg text-xs focus:outline-none focus:border-primary font-mono disabled:opacity-50"
              />
              <p className="text-xs text-[var(--color-text-secondary)]">推送本周（周一至今）的观影数据</p>
            </div>

            {/* 每月报告 */}
            <div className="p-3 rounded-lg bg-content2/50 space-y-2">
              <div className="flex items-center gap-2">
                <CalendarRange className="w-4 h-4 text-green-400" />
                <label className="flex items-center gap-2 cursor-pointer flex-1">
                  <input
                    type="checkbox"
                    checked={config.schedule.monthly.enabled}
                    onChange={e => updateSchedule('monthly', 'enabled', e.target.checked)}
                    className="w-4 h-4 rounded border-zinc-600 text-primary focus:ring-primary"
                  />
                  <span className="text-sm font-medium">每月报告</span>
                </label>
              </div>
              <input
                type="text"
                value={config.schedule.monthly.cron}
                onChange={e => updateSchedule('monthly', 'cron', e.target.value)}
                placeholder="0 21 1 * *"
                disabled={!config.schedule.monthly.enabled}
                className="w-full px-3 py-1.5 bg-content1 border border-[var(--color-border)] rounded-lg text-xs focus:outline-none focus:border-primary font-mono disabled:opacity-50"
              />
              <p className="text-xs text-[var(--color-text-secondary)]">推送本月（1号至今）的观影数据</p>
            </div>
          </div>
        </Card>

        {/* 用户选择 */}
        <Card className="p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                <Users className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <h3 className="font-semibold">报告用户</h3>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  {config.users.length === 0 ? '所有用户' : `已选 ${config.users.length} 人`}
                </p>
              </div>
            </div>
            <button
              onClick={selectAllUsers}
              className="text-xs text-primary hover:underline"
            >
              选择全部
            </button>
          </div>

          <div className="space-y-2 max-h-48 overflow-y-auto">
            {allUsers.map((user, index) => (
              <label
                key={user.user_id}
                className={cn(
                  'flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors',
                  (config.users.length === 0 || config.users.includes(user.user_id))
                    ? 'bg-primary/10'
                    : 'hover:bg-content2'
                )}
              >
                <input
                  type="checkbox"
                  checked={config.users.length === 0 || config.users.includes(user.user_id)}
                  onChange={() => toggleUser(user.user_id)}
                  className="w-4 h-4 rounded border-zinc-600 text-primary focus:ring-primary"
                />
                <Avatar name={user.username} index={index} className="w-8 h-8 text-sm" />
                <span className="text-sm">{user.username}</span>
              </label>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-[var(--color-border)]">
            <label className="block text-xs text-[var(--color-text-secondary)] mb-1">热门内容数量</label>
            <input
              type="number"
              min={1}
              max={10}
              value={config.content_count}
              onChange={e => setConfig(prev => ({ ...prev, content_count: parseInt(e.target.value) || 5 }))}
              className="w-full px-3 py-2 bg-content1 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:border-primary"
            />
          </div>
        </Card>

        {/* 预览和发送 */}
        <Card className="p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center">
              <Eye className="w-5 h-5 text-orange-500" />
            </div>
            <div>
              <h3 className="font-semibold">预览和发送</h3>
              <p className="text-xs text-[var(--color-text-secondary)]">查看报告效果（保存配置后刷新预览）</p>
            </div>
          </div>

          <div className="space-y-4">
            {/* 预览周期选择 */}
            <div className="flex gap-2">
              {(['daily', 'weekly', 'monthly'] as ReportPeriod[]).map(period => (
                <button
                  key={period}
                  onClick={() => setPreviewPeriod(period)}
                  className={cn(
                    'flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-colors',
                    previewPeriod === period
                      ? 'bg-primary text-white'
                      : 'bg-content2 text-[var(--color-text-secondary)] hover:bg-content2/80'
                  )}
                >
                  {periodLabels[period]}
                </button>
              ))}
            </div>

            <div className="rounded-lg overflow-hidden border border-[var(--color-border)]">
              <img
                key={`${previewKey}-${previewPeriod}-${currentServer?.id}`}
                src={`${api.getReportPreviewUrl(previewPeriod, currentServer?.id)}&t=${previewKey}`}
                alt="报告预览"
                className="w-full"
              />
            </div>

            {/* 发送周期选择 */}
            <div className="flex gap-2">
              {(['daily', 'weekly', 'monthly'] as ReportPeriod[]).map(period => (
                <button
                  key={period}
                  onClick={() => setSendPeriod(period)}
                  className={cn(
                    'flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-colors',
                    sendPeriod === period
                      ? 'bg-orange-500/20 text-orange-500'
                      : 'bg-content2 text-[var(--color-text-secondary)] hover:bg-content2/80'
                  )}
                >
                  发送{periodLabels[period]}
                </button>
              ))}
            </div>

            <button
              onClick={handleSendNow}
              disabled={sending || !config.telegram.enabled}
              className="w-full py-2 px-4 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              立即发送{periodLabels[sendPeriod]}报告
            </button>
          </div>
        </Card>
      </div>

      {/* 保存按钮 */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="py-2 px-6 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
          保存配置
        </button>
      </div>

      {/* Bot 交互功能 */}
      <div className="mt-8 pt-8 border-t border-[var(--color-border)]">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-primary" />
          Bot 交互功能
        </h2>
        <p className="text-sm text-[var(--color-text-secondary)] mb-6">
          允许用户通过 Telegram Bot 绑定 Emby 账户并查询个人观影报告
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bot 配置 */}
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-cyan-500" />
                </div>
                <div>
                  <h3 className="font-semibold">Bot 配置</h3>
                  <p className="text-xs text-[var(--color-text-secondary)]">
                    {botConfig?.is_running ? (
                      <span className="text-green-500">● 运行中</span>
                    ) : (
                      <span className="text-zinc-500">○ 未运行</span>
                    )}
                  </p>
                </div>
              </div>
              <button
                onClick={handleRestartBot}
                disabled={botRestarting}
                className="p-2 rounded-lg bg-cyan-500/20 text-cyan-500 hover:bg-cyan-500/30 transition-colors disabled:opacity-50"
                title="重启 Bot"
              >
                {botRestarting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
              </button>
            </div>

            <div className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={botEnabled}
                  onChange={e => setBotEnabled(e.target.checked)}
                  className="w-4 h-4 rounded border-zinc-600 text-primary focus:ring-primary"
                />
                <span className="text-sm">启用 Bot 交互功能</span>
              </label>

              <div>
                <label className="block text-xs text-[var(--color-text-secondary)] mb-1">
                  Bot Token {botConfig?.bot_token_configured && <span className="text-green-500">（已配置）</span>}
                </label>
                <input
                  type="password"
                  value={botToken}
                  onChange={e => setBotToken(e.target.value)}
                  placeholder={botConfig?.bot_token_configured ? '留空保持不变' : '从 @BotFather 获取'}
                  className="w-full px-3 py-2 bg-content1 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:border-primary"
                />
                <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                  可与推送功能使用同一个 Bot
                </p>
              </div>

              <div>
                <label className="block text-xs text-[var(--color-text-secondary)] mb-1">默认报告周期</label>
                <select
                  value={botDefaultPeriod}
                  onChange={e => setBotDefaultPeriod(e.target.value)}
                  className="w-full px-3 py-2 bg-content1 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:border-primary"
                >
                  <option value="daily">今日</option>
                  <option value="weekly">本周</option>
                  <option value="monthly">本月</option>
                  <option value="yearly">本年</option>
                </select>
              </div>

              <button
                onClick={handleSaveBotConfig}
                disabled={botSaving}
                className="w-full py-2 px-4 bg-cyan-500/20 text-cyan-500 rounded-lg text-sm font-medium hover:bg-cyan-500/30 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {botSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                保存 Bot 配置
              </button>
            </div>
          </Card>

          {/* 绑定用户列表 */}
          <Card className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-violet-500/20 flex items-center justify-center">
                <Link2 className="w-5 h-5 text-violet-500" />
              </div>
              <div>
                <h3 className="font-semibold">绑定用户</h3>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  共 {bindings.length} 个用户已绑定
                </p>
              </div>
            </div>

            {/* 搜索框 */}
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-secondary)]" />
              <input
                type="text"
                value={bindingSearch}
                onChange={e => setBindingSearch(e.target.value)}
                placeholder="搜索用户名、TG昵称或ID..."
                className="w-full pl-9 pr-3 py-2 bg-content1 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredBindings.length === 0 ? (
                <div className="text-center py-8 text-[var(--color-text-secondary)] text-sm">
                  {bindingSearch ? '未找到匹配的用户' : '暂无绑定用户'}
                </div>
              ) : (
                filteredBindings.map((binding, index) => (
                  <div
                    key={binding.tg_user_id}
                    className="flex items-center justify-between p-3 rounded-lg bg-content2/50"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar name={binding.emby_username} index={index} className="w-8 h-8 text-sm" />
                      <div>
                        <div className="text-sm font-medium">{binding.emby_username}</div>
                        <div className="text-xs text-[var(--color-text-secondary)]">
                          TG: {binding.tg_first_name || binding.tg_username || '未知'}（{binding.tg_user_id}）
                          {binding.server_name && ` · ${binding.server_name}`}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteBinding(binding.tg_user_id)}
                      disabled={deletingBinding === binding.tg_user_id}
                      className="p-2 rounded-lg text-red-500 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                      title="删除绑定"
                    >
                      {deletingBinding === binding.tg_user_id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
