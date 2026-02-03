import { useState, useMemo } from 'react'
import { useFilter } from '@/contexts/FilterContext'
import { cn } from '@/lib/utils'
import {
  Filter,
  X,
  Calendar,
  User,
  Monitor,
  Smartphone,
  Film,
  Play,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Search,
} from 'lucide-react'

interface FilterSectionProps {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  defaultOpen?: boolean
}

function FilterSection({ title, icon, children, defaultOpen = false }: FilterSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border-b border-[var(--color-border-light)] last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-[var(--color-foreground)] hover:bg-[var(--color-hover-overlay)] transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span>{title}</span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-4 h-4 text-[var(--color-text-muted)]" />
        ) : (
          <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
        )}
      </button>
      {isOpen && <div className="px-4 pb-3">{children}</div>}
    </div>
  )
}

interface MultiSelectProps {
  options: { value: string; label: string }[]
  selected: string[]
  onChange: (selected: string[]) => void
  placeholder?: string
  searchable?: boolean
  searchPlaceholder?: string
}

function MultiSelect({
  options,
  selected,
  onChange,
  placeholder = '选择...',
  searchable = false,
  searchPlaceholder = '搜索...'
}: MultiSelectProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredOptions = useMemo(() => {
    if (!searchQuery.trim()) return options
    const query = searchQuery.toLowerCase()
    return options.filter(o => o.label.toLowerCase().includes(query))
  }, [options, searchQuery])

  const toggleOption = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter(v => v !== value))
    } else {
      onChange([...selected, value])
    }
  }

  const selectAll = () => {
    // 如果有搜索词，只选中过滤后的结果
    const toSelect = searchQuery.trim() ? filteredOptions.map(o => o.value) : options.map(o => o.value)
    const newSelected = [...new Set([...selected, ...toSelect])]
    onChange(newSelected)
  }

  const clearAll = () => {
    // 如果有搜索词，只清除过滤后的结果
    if (searchQuery.trim()) {
      const filteredValues = new Set(filteredOptions.map(o => o.value))
      onChange(selected.filter(v => !filteredValues.has(v)))
    } else {
      onChange([])
    }
  }

  return (
    <div className="space-y-2">
      {/* 搜索框 */}
      {searchable && options.length > 5 && (
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--color-text-muted)]" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder={searchPlaceholder}
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-primary"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] hover:text-[var(--color-foreground)]"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      )}

      {/* 操作按钮 */}
      {options.length > 3 && (
        <div className="flex gap-2 text-xs">
          <button
            onClick={selectAll}
            className="text-primary hover:underline"
          >
            {searchQuery.trim() ? '全选结果' : '全选'}
          </button>
          <span className="text-[var(--color-text-muted)]">|</span>
          <button
            onClick={clearAll}
            className="text-primary hover:underline"
          >
            {searchQuery.trim() ? '清除结果' : '清除'}
          </button>
          {selected.length > 0 && (
            <>
              <span className="text-[var(--color-text-muted)]">|</span>
              <span className="text-[var(--color-text-muted)]">
                已选 {selected.length}
              </span>
            </>
          )}
        </div>
      )}

      {/* 选项列表 */}
      <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
        {options.length === 0 ? (
          <span className="text-xs text-[var(--color-text-muted)]">{placeholder}</span>
        ) : filteredOptions.length === 0 ? (
          <span className="text-xs text-[var(--color-text-muted)]">无匹配结果</span>
        ) : (
          filteredOptions.map(option => (
            <button
              key={option.value}
              onClick={() => toggleOption(option.value)}
              className={cn(
                'px-2.5 py-1.5 text-xs rounded-lg transition-colors border',
                selected.includes(option.value)
                  ? 'bg-primary text-white border-primary'
                  : 'bg-[var(--color-content1)] text-[var(--color-foreground)] border-[var(--color-border)] hover:bg-[var(--color-content2)]'
              )}
            >
              {option.label}
            </button>
          ))
        )}
      </div>
    </div>
  )
}

interface FilterPanelProps {
  isOpen: boolean
  onClose: () => void
}

export function FilterPanel({ isOpen, onClose }: FilterPanelProps) {
  const {
    filters,
    options,
    optionsLoading,
    hasActiveFilters,
    activeFilterCount,
    setDateRange,
    setUseDateRange,
    setSelectedUsers,
    setSelectedClients,
    setSelectedDevices,
    setSelectedItemTypes,
    setSelectedPlaybackMethods,
    clearFilters,
  } = useFilter()

  if (!isOpen) return null

  const itemTypeLabels: Record<string, string> = {
    Episode: '剧集',
    Movie: '电影',
    Audio: '音频',
    MusicVideo: '音乐视频',
    Video: '视频',
    Trailer: '预告片',
  }

  const methodLabels: Record<string, string> = {
    DirectPlay: '直接播放',
    DirectStream: '直接串流',
    Transcode: '转码',
  }

  return (
    <>
      {/* 遮罩 */}
      <div
        className="fixed inset-0 bg-black/50 z-50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 面板 */}
      <div className="fixed right-0 top-0 h-full w-80 max-w-[90vw] bg-[var(--color-content1)] border-l border-[var(--color-border)] z-50 overflow-hidden flex flex-col shadow-2xl">
        {/* 头部 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-content2)]">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-primary" />
            <span className="font-medium text-[var(--color-foreground)]">筛选器</span>
            {activeFilterCount > 0 && (
              <span className="px-1.5 py-0.5 text-xs bg-primary text-white rounded-full">
                {activeFilterCount}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[var(--color-hover-overlay)] transition-colors text-[var(--color-foreground)]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 内容 */}
        <div className="flex-1 overflow-y-auto">
          {optionsLoading ? (
            <div className="p-4 text-center text-[var(--color-text-muted)]">
              加载中...
            </div>
          ) : (
            <>
              {/* 日期范围 */}
              <FilterSection
                title="自定义日期"
                icon={<Calendar className="w-4 h-4" />}
                defaultOpen={filters.useDateRange}
              >
                <div className="space-y-3">
                  <label className="flex items-center gap-2 text-sm text-[var(--color-foreground)]">
                    <input
                      type="checkbox"
                      checked={filters.useDateRange}
                      onChange={e => setUseDateRange(e.target.checked)}
                      className="rounded border-[var(--color-border)] text-primary focus:ring-primary"
                    />
                    <span>使用自定义日期范围</span>
                  </label>
                  {filters.useDateRange && (
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-xs text-[var(--color-text-muted)]">开始日期</label>
                        <input
                          type="date"
                          value={filters.startDate || ''}
                          onChange={e => setDateRange(e.target.value || null, filters.endDate)}
                          min={options?.date_range.min || undefined}
                          max={options?.date_range.max || undefined}
                          className="w-full mt-1 px-2 py-1.5 text-sm rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] focus:outline-none focus:ring-1 focus:ring-primary"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-[var(--color-text-muted)]">结束日期</label>
                        <input
                          type="date"
                          value={filters.endDate || ''}
                          onChange={e => setDateRange(filters.startDate, e.target.value || null)}
                          min={options?.date_range.min || undefined}
                          max={options?.date_range.max || undefined}
                          className="w-full mt-1 px-2 py-1.5 text-sm rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] focus:outline-none focus:ring-1 focus:ring-primary"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </FilterSection>

              {/* 用户筛选 */}
              <FilterSection
                title={`用户 ${filters.selectedUsers.length > 0 ? `(${filters.selectedUsers.length})` : ''}`}
                icon={<User className="w-4 h-4" />}
              >
                <MultiSelect
                  options={(options?.users || []).map(u => ({ value: u.id, label: u.name }))}
                  selected={filters.selectedUsers}
                  onChange={setSelectedUsers}
                  placeholder="无可用用户"
                  searchable
                  searchPlaceholder="搜索用户..."
                />
              </FilterSection>

              {/* 客户端筛选 */}
              <FilterSection
                title={`客户端 ${filters.selectedClients.length > 0 ? `(${filters.selectedClients.length})` : ''}`}
                icon={<Monitor className="w-4 h-4" />}
              >
                <MultiSelect
                  options={(options?.clients || []).map(c => ({ value: c.original, label: c.display }))}
                  selected={filters.selectedClients}
                  onChange={setSelectedClients}
                  placeholder="无可用客户端"
                  searchable
                  searchPlaceholder="搜索客户端..."
                />
              </FilterSection>

              {/* 设备筛选 */}
              <FilterSection
                title={`设备 ${filters.selectedDevices.length > 0 ? `(${filters.selectedDevices.length})` : ''}`}
                icon={<Smartphone className="w-4 h-4" />}
              >
                <MultiSelect
                  options={(options?.devices || []).map(d => ({ value: d.original, label: d.display }))}
                  selected={filters.selectedDevices}
                  onChange={setSelectedDevices}
                  placeholder="无可用设备"
                  searchable
                  searchPlaceholder="搜索设备..."
                />
              </FilterSection>

              {/* 媒体类型筛选 */}
              <FilterSection
                title={`媒体类型 ${filters.selectedItemTypes.length > 0 ? `(${filters.selectedItemTypes.length})` : ''}`}
                icon={<Film className="w-4 h-4" />}
              >
                <MultiSelect
                  options={(options?.item_types || []).map(t => ({
                    value: t,
                    label: itemTypeLabels[t] || t,
                  }))}
                  selected={filters.selectedItemTypes}
                  onChange={setSelectedItemTypes}
                  placeholder="无可用类型"
                />
              </FilterSection>

              {/* 播放方式筛选 */}
              <FilterSection
                title={`播放方式 ${filters.selectedPlaybackMethods.length > 0 ? `(${filters.selectedPlaybackMethods.length})` : ''}`}
                icon={<Play className="w-4 h-4" />}
              >
                <MultiSelect
                  options={(options?.playback_methods || []).map(m => ({
                    value: m,
                    label: methodLabels[m] || m,
                  }))}
                  selected={filters.selectedPlaybackMethods}
                  onChange={setSelectedPlaybackMethods}
                  placeholder="无可用方式"
                />
              </FilterSection>
            </>
          )}
        </div>

        {/* 底部操作 */}
        {hasActiveFilters && (
          <div className="border-t border-[var(--color-border)] p-4 bg-[var(--color-content2)]">
            <button
              onClick={clearFilters}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm bg-[var(--color-content3)] text-[var(--color-foreground)] rounded-lg hover:bg-[var(--color-content4)] transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              清除所有筛选
            </button>
          </div>
        )}
      </div>
    </>
  )
}
