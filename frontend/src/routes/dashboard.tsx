import type { Route } from "./+types/dashboard"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { analyticsApi, systemApi, checkpointsApi } from '@/services/api'
import { useTraining } from '@/context/TrainingContext'
import {
  Calendar,
  Users,
  MapPin,
  Skull,
  Activity,
  Brain,
  Database,
  Cpu,
  TrendingDown,
  Award,
  Zap,
  Download,
  Globe,
  BarChart3
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658']

interface Checkpoint {
  name: string
  model_name: string
  current_epoch: number
  total_epochs: number
  best_epoch: number
  best_val_loss: number
  val_loss: number
  is_complete: boolean
  batch_size: number
  learning_rate: number
  available_epochs: number[]
  has_best: boolean
}

interface MonthlyTrend {
  period: string
  events: number
  deaths: number
  injuries: number
}

interface CountryStat {
  country: string
  events: number
  deaths: number
}

interface ActorStat {
  actor: string
  events: number
  deaths: number
  countries_affected: number
}

export async function clientLoader() {
  const [stats, trends, health, systemMetrics, checkpointsData, monthlyTrends, countryStats, actorStats] = await Promise.all([
    analyticsApi.getStats().catch(() => null),
    analyticsApi.getTimeline('month', 6).catch(() => []),
    systemApi.getHealth().catch(() => null),
    systemApi.getMetrics().catch(() => null),
    checkpointsApi.list().catch(() => ({ checkpoints: [], total: 0 })),
    analyticsApi.getMonthlyTrends(12).catch(() => []),
    analyticsApi.getByCountry().catch(() => []),
    analyticsApi.getByActor(15).catch(() => []),
  ])

  return {
    stats,
    trends,
    health,
    systemMetrics,
    checkpoints: checkpointsData.checkpoints as Checkpoint[],
    monthlyTrends: monthlyTrends as MonthlyTrend[],
    countryStats: countryStats as CountryStat[],
    actorStats: actorStats as ActorStat[]
  }
}

export default function Dashboard({ loaderData }: Route.ComponentProps) {
  const { stats, trends, health, systemMetrics, checkpoints, monthlyTrends, countryStats, actorStats } = loaderData
  const { status: trainingStatus, metrics: liveMetrics } = useTraining()

  const severityData = stats?.events_by_severity
    ? Object.entries(stats.events_by_severity).map(([name, value]) => ({ name, value }))
    : []

  const taxonomyData = stats?.events_by_taxonomy?.slice(0, 5) || []

  const bestCheckpoint = checkpoints.reduce((best: Checkpoint | null, cp: Checkpoint) => {
    if (!best) return cp
    return cp.best_val_loss < best.best_val_loss ? cp : best
  }, null as Checkpoint | null)

  const checkpointChartData = checkpoints.map((cp: Checkpoint) => ({
    name: cp.name.split('_').slice(-2).join('_'),
    epochs: cp.current_epoch,
    bestValLoss: cp.best_val_loss,
    valLoss: cp.val_loss,
    isComplete: cp.is_complete
  }))

  const hasLiveMetrics = liveMetrics.length > 0
  const isTraining = trainingStatus.isRunning

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      const response = await analyticsApi.export(format)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `events_export.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Export failed:', e)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            VioNER - Violent Event Named Entity Recognition
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
            <Download className="mr-2 h-4 w-4" />
            CSV
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
            <Download className="mr-2 h-4 w-4" />
            JSON
          </Button>
        </div>
      </div>

      {/* Event Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Events</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_events?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">
              Across {stats?.countries_covered || 0} countries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Deaths</CardTitle>
            <Skull className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{stats?.total_deaths?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.total_injuries?.toLocaleString() || 0} injuries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Actors</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_actors?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">Armed groups tracked</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Locations</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_locations?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">Cities & regions</p>
          </CardContent>
        </Card>
      </div>

      {/* System & Model Status */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${
                health?.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
              }`} />
              <span className="text-lg font-medium capitalize">{health?.status || 'Unknown'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">NER Model</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${
                health?.model_loaded ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-lg font-medium">
                {health?.model_loaded ? 'Loaded' : 'Not Loaded'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${
                health?.database_connected ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-lg font-medium">
                {health?.database_connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resources</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>CPU</span>
                <span>{systemMetrics?.cpu_percent?.toFixed(1) || 0}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Memory</span>
                <span>{systemMetrics?.memory_percent?.toFixed(1) || 0}%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Training Status */}
      {isTraining ? (
        <Card className="border-green-500/50 bg-green-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              Training in Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div>
                <p className="text-sm text-muted-foreground">Model</p>
                <p className="font-medium">{trainingStatus.modelName || 'bert-base-cased'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Epoch</p>
                <p className="font-medium">{trainingStatus.currentEpoch} / {trainingStatus.totalEpochs}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Loss</p>
                <p className="font-medium">{trainingStatus.loss.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Accuracy</p>
                <p className="font-medium">{(trainingStatus.accuracy * 100).toFixed(2)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : checkpoints.length > 0 && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Model Checkpoints
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{checkpoints.length}</div>
              <p className="text-xs text-muted-foreground">
                {checkpoints.filter((c: Checkpoint) => c.is_complete).length} complete
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingDown className="h-4 w-4" />
                Best Val Loss
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {bestCheckpoint?.best_val_loss?.toFixed(4) || '-'}
              </div>
              <p className="text-xs text-muted-foreground">
                Epoch {bestCheckpoint?.best_epoch || '-'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Award className="h-4 w-4" />
                Best Model
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold truncate">
                {bestCheckpoint?.model_name || '-'}
              </div>
              <p className="text-xs text-muted-foreground font-mono">
                {bestCheckpoint?.name?.split('_').slice(-2).join('_') || '-'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Total Epochs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {checkpoints.reduce((sum: number, c: Checkpoint) => sum + c.current_epoch, 0)}
              </div>
              <p className="text-xs text-muted-foreground">
                across all checkpoints
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Live Training Metrics */}
      {hasLiveMetrics && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Training Loss</CardTitle>
              <CardDescription>Live training and validation loss</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={liveMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="loss" name="Train" stroke="#8884d8" strokeWidth={2} />
                    <Line type="monotone" dataKey="valLoss" name="Val" stroke="#82ca9d" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Training Accuracy</CardTitle>
              <CardDescription>Live training and validation accuracy</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={liveMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" />
                    <YAxis domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                    <Tooltip formatter={(v: number) => `${(v * 100).toFixed(2)}%`} />
                    <Legend />
                    <Area type="monotone" dataKey="accuracy" name="Train" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="valAccuracy" name="Val" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analytics Tabs */}
      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList>
          <TabsTrigger value="trends" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Trends
          </TabsTrigger>
          <TabsTrigger value="geography" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Geography
          </TabsTrigger>
          <TabsTrigger value="actors" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Actors
          </TabsTrigger>
          <TabsTrigger value="severity" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Severity
          </TabsTrigger>
        </TabsList>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Monthly Trends</CardTitle>
                <CardDescription>Events and casualties over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={monthlyTrends}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="period" fontSize={12} />
                      <YAxis yAxisId="left" fontSize={12} />
                      <YAxis yAxisId="right" orientation="right" fontSize={12} />
                      <Tooltip />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="events" stroke="#8884d8" strokeWidth={2} name="Events" />
                      <Line yAxisId="right" type="monotone" dataKey="deaths" stroke="#ff7300" strokeWidth={2} name="Deaths" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {!hasLiveMetrics && checkpoints.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Model Performance</CardTitle>
                  <CardDescription>Checkpoint comparison</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={checkpointChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="bestValLoss" name="Best Val Loss" fill="#82ca9d" />
                        <Bar dataKey="epochs" name="Epochs" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}

            {(hasLiveMetrics || checkpoints.length === 0) && (
              <Card>
                <CardHeader>
                  <CardTitle>Events by Category</CardTitle>
                </CardHeader>
                <CardContent>
                  {taxonomyData.length > 0 ? (
                    <div className="space-y-4">
                      {taxonomyData.map((item, index) => (
                        <div key={item.taxonomy} className="flex items-center gap-4">
                          <div className="w-24 truncate text-sm font-medium">{item.taxonomy}</div>
                          <div className="flex-1">
                            <div className="h-2 rounded-full bg-muted">
                              <div
                                className="h-full rounded-full"
                                style={{
                                  width: `${(item.count / (taxonomyData[0]?.count || 1)) * 100}%`,
                                  backgroundColor: COLORS[index % COLORS.length],
                                }}
                              />
                            </div>
                          </div>
                          <div className="w-12 text-right text-sm text-muted-foreground">
                            {item.count.toLocaleString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">No category data</p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Geography Tab */}
        <TabsContent value="geography" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Events by Country</CardTitle>
              <CardDescription>Top 10 affected countries</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={countryStats.slice(0, 10)} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" fontSize={12} />
                    <YAxis type="category" dataKey="country" width={100} fontSize={12} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="events" fill="#8884d8" name="Events" />
                    <Bar dataKey="deaths" fill="#ff7300" name="Deaths" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Actors Tab */}
        <TabsContent value="actors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Actors</CardTitle>
              <CardDescription>Most active armed groups</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={actorStats.slice(0, 10)} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" fontSize={12} />
                    <YAxis type="category" dataKey="actor" width={150} fontSize={11} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="events" fill="#8884d8" name="Events" />
                    <Bar dataKey="deaths" fill="#ff7300" name="Deaths" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Actor Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="pb-2 text-left font-medium">Actor</th>
                      <th className="pb-2 text-right font-medium">Events</th>
                      <th className="pb-2 text-right font-medium">Deaths</th>
                      <th className="pb-2 text-right font-medium">Countries</th>
                    </tr>
                  </thead>
                  <tbody>
                    {actorStats.map((a, i) => (
                      <tr key={i} className="border-b last:border-0">
                        <td className="py-2">{a.actor}</td>
                        <td className="py-2 text-right">{a.events.toLocaleString()}</td>
                        <td className="py-2 text-right text-red-500">{a.deaths.toLocaleString()}</td>
                        <td className="py-2 text-right">{a.countries_affected}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Severity Tab */}
        <TabsContent value="severity" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Events by Severity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={severityData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={2}
                        dataKey="value"
                        label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                      >
                        {severityData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Severity Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {severityData.map((item, index) => (
                    <div key={item.name} className="flex items-center gap-4">
                      <div
                        className="h-4 w-4 rounded"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <div className="flex-1">
                        <div className="flex justify-between">
                          <span className="font-medium">{item.name}</span>
                          <span>{item.value.toLocaleString()}</span>
                        </div>
                        <div className="mt-1 h-2 rounded-full bg-muted">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${(item.value / (stats?.total_events || 1)) * 100}%`,
                              backgroundColor: COLORS[index % COLORS.length],
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
