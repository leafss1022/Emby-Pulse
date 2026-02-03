import { Card } from '@/components/ui'
import { PieChart } from '@/components/charts'
import { useClients, usePlaybackMethods, useDevices } from '@/hooks/useStats'
import { Monitor } from 'lucide-react'
import type { FilterParams } from '@/services/api'

interface DevicesProps {
  filterParams: FilterParams
}

export function Devices({ filterParams }: DevicesProps) {
  const { data: clientsData } = useClients(filterParams)
  const { data: methodsData } = usePlaybackMethods(filterParams)
  const { data: devicesData } = useDevices(filterParams)

  const clientsChartData = clientsData?.clients.map((c) => ({
    name: c.client,
    value: c.play_count,
  })) || []

  const methodsChartData = methodsData?.methods.map((m) => ({
    name: m.method,
    value: m.play_count,
  })) || []

  return (
    <div className="fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="p-5 flex flex-col" style={{ minHeight: 320 }}>
          <h3 className="font-semibold mb-4">客户端分布</h3>
          <div className="flex-1" style={{ minHeight: 240 }}>
            {clientsData && <PieChart data={clientsChartData} />}
          </div>
        </Card>

        <Card className="p-5 flex flex-col" style={{ minHeight: 320 }}>
          <h3 className="font-semibold mb-4">播放方式</h3>
          <div className="flex-1" style={{ minHeight: 240 }}>
            {methodsData && (
              <PieChart data={methodsChartData} colors={['#17c964', '#006FEE', '#f5a524']} />
            )}
          </div>
        </Card>

        <Card className="p-5 flex flex-col md:col-span-2 lg:col-span-1" style={{ minHeight: 320 }}>
          <h3 className="font-semibold mb-4">设备列表</h3>
          <div className="space-y-2 flex-1 overflow-y-auto pr-1">
            {devicesData?.devices.map((device, index) => (
              <div
                key={`${device.device}-${device.client}-${index}`}
                className="flex items-center justify-between p-3 bg-content1 rounded-[10px] transition-colors hover:bg-content2"
              >
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-[10px] bg-primary/20 text-primary flex items-center justify-center">
                    <Monitor className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-sm">{device.device}</p>
                    <p className="text-xs text-[var(--color-text-secondary)]">{device.client}</p>
                  </div>
                </div>
                <span className="text-xs text-[var(--color-text-muted)]">{device.play_count}次</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
