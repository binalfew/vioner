import { useRevalidator } from 'react-router'
import type { Route } from "./+types/settings"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { systemApi, inferenceApi } from '@/services/api'
import { Settings as SettingsIcon, Server, Brain, Cpu, HardDrive, RefreshCw } from 'lucide-react'

interface Health {
  status: string
  model_loaded: boolean
  database_enabled: boolean
  database_connected: boolean | null
  version: string
}

interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  memory_used_mb: number
  memory_available_mb: number
  disk_percent: number
  disk_used_gb: number
  disk_free_gb: number
}

interface GpuInfo {
  available: boolean
  device: string
  name: string | null
  memory_total_mb: number | null
  memory_used_mb: number | null
}

interface ModelInfo {
  model_path: string | null
  model_type: string | null
  num_labels: number
  device: string
  loaded: boolean
}

// React Router 7 clientLoader - fetches all system info in parallel
export async function clientLoader() {
  const [health, systemMetrics, gpuInfo, modelInfo] = await Promise.all([
    systemApi.getHealth().catch(() => null),
    systemApi.getMetrics().catch(() => null),
    systemApi.getGpuInfo().catch(() => null),
    inferenceApi.getModelInfo().catch(() => null),
  ])

  return {
    health: health as Health | null,
    systemMetrics: systemMetrics as SystemMetrics | null,
    gpuInfo: gpuInfo as GpuInfo | null,
    modelInfo: modelInfo as ModelInfo | null
  }
}

export default function Settings({ loaderData }: Route.ComponentProps) {
  const { health, systemMetrics, gpuInfo, modelInfo } = loaderData
  const revalidator = useRevalidator()

  const isLoading = revalidator.state === 'loading'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">
            System configuration and status
          </p>
        </div>
        <Button variant="outline" onClick={() => revalidator.revalidate()} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center gap-3">
              <div className={`h-3 w-3 rounded-full ${
                health?.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
              }`} />
              <div>
                <p className="font-medium">API Status</p>
                <p className="text-sm text-muted-foreground capitalize">{health?.status || 'Unknown'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className={`h-3 w-3 rounded-full ${
                health?.database_connected ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <div>
                <p className="font-medium">Database</p>
                <p className="text-sm text-muted-foreground">
                  {health?.database_connected ? 'Connected' : 'Disconnected'}
                </p>
              </div>
            </div>
            <div>
              <p className="font-medium">API Version</p>
              <p className="text-sm text-muted-foreground">{health?.version || '-'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Model Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            NER Model
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-sm text-muted-foreground">Status</p>
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${
                  modelInfo?.loaded ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <p className="font-medium">{modelInfo?.loaded ? 'Loaded' : 'Not Loaded'}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Model Type</p>
              <p className="font-medium">{modelInfo?.model_type || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Device</p>
              <p className="font-medium">{modelInfo?.device || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Labels</p>
              <p className="font-medium">{modelInfo?.num_labels || '-'}</p>
            </div>
          </div>
          {modelInfo?.model_path && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-muted-foreground">Model Path</p>
              <p className="font-mono text-sm">{modelInfo.model_path}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* System Resources */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5" />
            System Resources
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-3">
            {/* CPU */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">CPU Usage</span>
                <span className="text-sm">{systemMetrics?.cpu_percent?.toFixed(1) || 0}%</span>
              </div>
              <div className="h-2 rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary transition-all"
                  style={{ width: `${systemMetrics?.cpu_percent || 0}%` }}
                />
              </div>
            </div>

            {/* Memory */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Memory Usage</span>
                <span className="text-sm">{systemMetrics?.memory_percent?.toFixed(1) || 0}%</span>
              </div>
              <div className="h-2 rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-blue-500 transition-all"
                  style={{ width: `${systemMetrics?.memory_percent || 0}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                {((systemMetrics?.memory_used_mb || 0) / 1024).toFixed(1)} GB /
                {(((systemMetrics?.memory_used_mb || 0) + (systemMetrics?.memory_available_mb || 0)) / 1024).toFixed(1)} GB
              </p>
            </div>

            {/* Disk */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Disk Usage</span>
                <span className="text-sm">{systemMetrics?.disk_percent?.toFixed(1) || 0}%</span>
              </div>
              <div className="h-2 rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-orange-500 transition-all"
                  style={{ width: `${systemMetrics?.disk_percent || 0}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                {systemMetrics?.disk_used_gb?.toFixed(1) || 0} GB used,
                {systemMetrics?.disk_free_gb?.toFixed(1) || 0} GB free
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* GPU Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HardDrive className="h-5 w-5" />
            GPU Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          {gpuInfo?.available ? (
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm text-muted-foreground">Device</p>
                <p className="font-medium">{gpuInfo.device}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="font-medium">{gpuInfo.name || '-'}</p>
              </div>
              {gpuInfo.memory_total_mb && (
                <div>
                  <p className="text-sm text-muted-foreground">Memory</p>
                  <p className="font-medium">
                    {((gpuInfo.memory_used_mb || 0) / 1024).toFixed(1)} GB /
                    {(gpuInfo.memory_total_mb / 1024).toFixed(1)} GB
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2 text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-gray-500" />
              <span>No GPU available - using CPU</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* API Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            API Endpoints
          </CardTitle>
          <CardDescription>Available API routes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 text-sm font-mono">
            <div className="flex gap-2">
              <span className="rounded bg-green-500/10 px-2 py-0.5 text-green-500">GET</span>
              <span>/api/system/health</span>
            </div>
            <div className="flex gap-2">
              <span className="rounded bg-blue-500/10 px-2 py-0.5 text-blue-500">POST</span>
              <span>/api/inference</span>
            </div>
            <div className="flex gap-2">
              <span className="rounded bg-blue-500/10 px-2 py-0.5 text-blue-500">POST</span>
              <span>/api/training/start</span>
            </div>
            <div className="flex gap-2">
              <span className="rounded bg-green-500/10 px-2 py-0.5 text-green-500">GET</span>
              <span>/api/events</span>
            </div>
            <div className="flex gap-2">
              <span className="rounded bg-green-500/10 px-2 py-0.5 text-green-500">GET</span>
              <span>/api/analytics/stats</span>
            </div>
            <div className="flex gap-2">
              <span className="rounded bg-purple-500/10 px-2 py-0.5 text-purple-500">WS</span>
              <span>/ws/training/progress</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              Full API documentation available at{' '}
              <a href="/docs" target="_blank" className="text-primary hover:underline">/docs</a>
              {' '}or{' '}
              <a href="/redoc" target="_blank" className="text-primary hover:underline">/redoc</a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
