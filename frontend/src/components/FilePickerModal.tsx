import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, Check, Folder, HardDrive, Loader2, RefreshCw, File as FileIcon, Home } from 'lucide-react'
import { Modal } from '@/components/ui'
import { api } from '@/services/api'
import type { FileEntry } from '@/types'

interface FilePickerModalProps {
  open: boolean
  onClose: () => void
  onSelect: (path: string) => void
  initialPath?: string
  title?: string
  description?: string
}

function formatSize(bytes: number): string {
  if (bytes <= 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  return `${(bytes / Math.pow(1024, exponent)).toFixed(exponent === 0 ? 0 : 1)} ${units[exponent]}`
}

export function FilePickerModal({
  open,
  onClose,
  onSelect,
  initialPath = '/data',
  title = '选择文件路径',
  description = '浏览容器内的文件和目录，直接选中数据库路径',
}: FilePickerModalProps) {
  const [currentPath, setCurrentPath] = useState(initialPath)
  const [parentPath, setParentPath] = useState<string | null | undefined>(null)
  const [entries, setEntries] = useState<FileEntry[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [pathInput, setPathInput] = useState(initialPath)

  const quickPaths = useMemo(() => ['/data', '/config', '/app', '/'], [])

  useEffect(() => {
    if (!open) return
    const startPath = initialPath?.trim() || '/data'
    setPathInput(startPath)
    loadPath(startPath)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, initialPath])

  const loadPath = async (path: string) => {
    setIsLoading(true)
    setError('')
    try {
      const data = await api.browseFiles(path)
      setEntries(data.entries)
      setCurrentPath(data.cwd)
      setParentPath(data.parent)
      setPathInput(data.cwd)
    } catch (err: any) {
      setError(err.message || '加载目录失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelect = (path: string) => {
    onSelect(path)
    onClose()
  }

  return (
    <Modal open={open} onClose={onClose}>
      <div className="bg-[var(--color-content1)] text-foreground rounded-2xl shadow-2xl border border-[var(--color-border)] overflow-hidden backdrop-blur-xl">
        <div className="p-4 border-b border-[var(--color-border)] flex items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold">{title}</h3>
            <p className="text-xs text-[var(--color-text-muted)] mt-1">{description}</p>
          </div>
          <button
            className="px-3 py-2 text-sm rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors flex items-center gap-2"
            onClick={() => handleSelect(currentPath)}
          >
            <Check className="w-4 h-4" />
            使用当前路径
          </button>
        </div>

        <div className="p-4 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2 flex-1 min-w-[240px]">
              <HardDrive className="w-4 h-4 text-primary" />
              <input
                value={pathInput}
                onChange={(e) => setPathInput(e.target.value)}
                className="flex-1 px-3 py-2 rounded-lg bg-content2 border border-[var(--color-border)] focus:outline-none focus:border-primary text-sm"
              />
              <button
                type="button"
                onClick={() => loadPath(pathInput)}
                className="px-3 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors text-sm"
              >
                跳转
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => loadPath('/')}
                className="p-2 rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-hover-overlay)]"
                title="回到根目录"
              >
                <Home className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => parentPath && loadPath(parentPath)}
                className="p-2 rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-hover-overlay)] disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!parentPath}
                title="返回上级"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => loadPath(currentPath)}
                className="p-2 rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-hover-overlay)]"
                title="刷新"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {quickPaths.map((path) => (
              <button
                key={path}
                onClick={() => loadPath(path)}
                className="px-3 py-1.5 rounded-lg border border-[var(--color-border)] text-sm text-[var(--color-text-muted)] hover:text-foreground hover:bg-[var(--color-hover-overlay)] transition-colors"
              >
                {path}
              </button>
            ))}
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-danger/10 border border-danger/30 text-danger text-sm">
              {error}
            </div>
          )}

          <div className="h-72 overflow-y-auto rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)]">
            {isLoading ? (
              <div className="h-full flex items-center justify-center text-[var(--color-text-muted)]">
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                加载中...
              </div>
            ) : (
              <div className="divide-y divide-[var(--color-border)]">
                {entries.map((entry) => (
                  <div
                    key={entry.path}
                    className="flex items-center gap-3 px-3 py-2 hover:bg-[var(--color-hover-overlay)]"
                  >
                    <button
                      className="flex items-center gap-3 flex-1 text-left"
                      onClick={() => (entry.is_dir ? loadPath(entry.path) : handleSelect(entry.path))}
                    >
                      {entry.is_dir ? (
                        <Folder className="w-4 h-4 text-primary" />
                      ) : (
                        <FileIcon className="w-4 h-4 text-[var(--color-text-muted)]" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="text-sm truncate">{entry.name}</div>
                        <div className="text-xs text-[var(--color-text-muted)] truncate">
                          {entry.is_dir ? '文件夹' : `文件 · ${formatSize(entry.size)}`} · {new Date(entry.modified * 1000).toLocaleString()}
                        </div>
                      </div>
                    </button>
                    {!entry.is_dir && (
                      <button
                        className="px-3 py-1.5 rounded-lg border border-[var(--color-border)] text-xs hover:bg-[var(--color-hover-overlay)]"
                        onClick={() => handleSelect(entry.path)}
                      >
                        选择
                      </button>
                    )}
                  </div>
                ))}
                {entries.length === 0 && (
                  <div className="p-6 text-center text-[var(--color-text-muted)]">该目录为空</div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  )
}

