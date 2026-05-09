import { useState, useEffect } from 'react'
import { useRevalidator } from 'react-router'
import type { Route } from './+types/analytics'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import {
  evaluationApi,
  checkpointsApi,
  type EvaluationResult,
  type EntityMetrics,
  type ConfusionEntry,
  type ErrorExample,
} from '@/services/api'
import {
  BarChart3,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  RefreshCw,
  Zap,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts'

// Colors for 8 entity types (optimized for grounding)
const ENTITY_COLORS: Record<string, string> = {
  // WHO (1 type - merged)
  ACTOR: '#ef4444',
  // WHOM (1 type)
  VICTIM: '#f97316',
  // WHAT (1 type)
  ACTION: '#8b5cf6',
  // WHEN (1 type)
  DATE: '#3b82f6',
  // WHERE (3 types)
  REGION: '#14b8a6',
  CITY: '#06b6d4',
  DISTRICT: '#0ea5e9',
  // HOW (1 type)
  CASUALTIES: '#f43f5e',
}

const getEntityColor = (entityType: string): string => {
  return ENTITY_COLORS[entityType] || '#94a3b8'
}

export async function clientLoader() {
  const [checkpointsData, evaluationsData] = await Promise.all([
    checkpointsApi.list(),
    evaluationApi.list(),
  ])
  return {
    checkpoints: checkpointsData.checkpoints as Array<{ name: string; best_val_loss: number }>,
    cachedEvaluations: evaluationsData.evaluations,
  }
}

export default function Analytics({ loaderData }: Route.ComponentProps) {
  const { checkpoints, cachedEvaluations } = loaderData
  const revalidator = useRevalidator()

  const [selectedCheckpoint, setSelectedCheckpoint] = useState<string>(
    checkpoints[0]?.name || ''
  )
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [evalStatus, setEvalStatus] = useState<string>('idle')

  // Check for cached evaluation on checkpoint change
  useEffect(() => {
    if (selectedCheckpoint) {
      const cached = cachedEvaluations.find(
        (e) => e.checkpoint_name === selectedCheckpoint
      )
      if (cached) {
        // Load cached results
        loadCachedResults()
      } else {
        setEvaluationResult(null)
      }
    }
  }, [selectedCheckpoint])

  const loadCachedResults = async () => {
    try {
      const results = await evaluationApi.getResults(selectedCheckpoint)
      setEvaluationResult(results)
      setEvalStatus('complete')
    } catch {
      setEvaluationResult(null)
    }
  }

  const runQuickEvaluation = async () => {
    setLoading(true)
    setError(null)
    setEvalStatus('running')
    try {
      const results = await evaluationApi.quickEval(selectedCheckpoint, 1000)
      setEvaluationResult(results)
      setEvalStatus('complete')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Evaluation failed')
      setEvalStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const runFullEvaluation = async () => {
    setLoading(true)
    setError(null)
    setEvalStatus('running')
    try {
      // Start full evaluation
      await evaluationApi.run(selectedCheckpoint)

      // Poll for completion
      const pollInterval = setInterval(async () => {
        const status = await evaluationApi.getStatus(selectedCheckpoint)
        if (status.status === 'complete') {
          clearInterval(pollInterval)
          const results = await evaluationApi.getResults(selectedCheckpoint)
          setEvaluationResult(results)
          setEvalStatus('complete')
          setLoading(false)
          revalidator.revalidate()
        } else if (status.status === 'error') {
          clearInterval(pollInterval)
          setError(status.error || 'Evaluation failed')
          setEvalStatus('error')
          setLoading(false)
        }
      }, 2000)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Evaluation failed')
      setEvalStatus('error')
      setLoading(false)
    }
  }

  const formatPercent = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`
  }

  const getF1Color = (f1: number): string => {
    if (f1 >= 0.9) return 'text-green-600'
    if (f1 >= 0.7) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart3 className="h-8 w-8" />
            Model Analytics
          </h1>
          <p className="text-muted-foreground">
            Evaluate model performance with per-entity metrics
          </p>
        </div>
      </div>

      {/* Checkpoint Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Select Model</CardTitle>
          <CardDescription>
            Choose a trained model to evaluate
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Select
                value={selectedCheckpoint}
                onValueChange={setSelectedCheckpoint}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select checkpoint" />
                </SelectTrigger>
                <SelectContent>
                  {checkpoints.map((cp) => (
                    <SelectItem key={cp.name} value={cp.name}>
                      {cp.name} (loss: {cp.best_val_loss?.toFixed(4) || 'N/A'})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={runQuickEvaluation}
              disabled={loading || !selectedCheckpoint}
              variant="outline"
            >
              {loading && evalStatus === 'running' ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Zap className="mr-2 h-4 w-4" />
              )}
              Quick Eval (1k samples)
            </Button>
            <Button
              onClick={runFullEvaluation}
              disabled={loading || !selectedCheckpoint}
            >
              {loading && evalStatus === 'running' ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Target className="mr-2 h-4 w-4" />
              )}
              Full Evaluation
            </Button>
          </div>
          {error && (
            <p className="text-sm text-destructive mt-2">{error}</p>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {evaluationResult && (
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="entities">Entity Metrics</TabsTrigger>
            <TabsTrigger value="confusion">Confusion Matrix</TabsTrigger>
            <TabsTrigger value="errors">Error Analysis</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            {/* Overall Metrics */}
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Overall F1 Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-3xl font-bold ${getF1Color(evaluationResult.overall_f1)}`}>
                    {formatPercent(evaluationResult.overall_f1)}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Precision
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {formatPercent(evaluationResult.overall_precision)}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Recall
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {formatPercent(evaluationResult.overall_recall)}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Samples Evaluated
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {evaluationResult.total_samples.toLocaleString()}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Entity Distribution Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Entity Distribution</CardTitle>
                <CardDescription>
                  Number of entities by type in validation data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(evaluationResult.entity_distribution).map(
                        ([type, count]) => ({ type, count })
                      )}
                      margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="type"
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        fontSize={12}
                      />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" name="Count">
                        {Object.entries(evaluationResult.entity_distribution).map(
                          ([type], index) => (
                            <Cell key={index} fill={getEntityColor(type)} />
                          )
                        )}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* F1 by Entity Type Chart */}
            <Card>
              <CardHeader>
                <CardTitle>F1 Score by Entity Type</CardTitle>
                <CardDescription>
                  Performance breakdown for each entity category
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={evaluationResult.entity_metrics.map((m) => ({
                        type: m.entity_type,
                        f1: m.f1 * 100,
                        precision: m.precision * 100,
                        recall: m.recall * 100,
                      }))}
                      margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="type"
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        fontSize={12}
                      />
                      <YAxis domain={[0, 100]} unit="%" />
                      <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                      <Legend />
                      <Bar dataKey="precision" name="Precision" fill="#3b82f6" />
                      <Bar dataKey="recall" name="Recall" fill="#22c55e" />
                      <Bar dataKey="f1" name="F1" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Entity Metrics Tab */}
          <TabsContent value="entities">
            <Card>
              <CardHeader>
                <CardTitle>Per-Entity Metrics</CardTitle>
                <CardDescription>
                  Detailed precision, recall, and F1 for each entity type
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Entity Type</TableHead>
                      <TableHead className="text-right">Precision</TableHead>
                      <TableHead className="text-right">Recall</TableHead>
                      <TableHead className="text-right">F1 Score</TableHead>
                      <TableHead className="text-right">Support</TableHead>
                      <TableHead className="text-right">Predicted</TableHead>
                      <TableHead className="text-right">Correct</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {evaluationResult.entity_metrics
                      .sort((a, b) => b.f1 - a.f1)
                      .map((metric) => (
                        <TableRow key={metric.entity_type}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <div
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: getEntityColor(metric.entity_type) }}
                              />
                              <span className="font-medium">{metric.entity_type}</span>
                            </div>
                          </TableCell>
                          <TableCell className="text-right">
                            {formatPercent(metric.precision)}
                          </TableCell>
                          <TableCell className="text-right">
                            {formatPercent(metric.recall)}
                          </TableCell>
                          <TableCell className={`text-right font-bold ${getF1Color(metric.f1)}`}>
                            {formatPercent(metric.f1)}
                          </TableCell>
                          <TableCell className="text-right text-muted-foreground">
                            {metric.support.toLocaleString()}
                          </TableCell>
                          <TableCell className="text-right text-muted-foreground">
                            {metric.predicted.toLocaleString()}
                          </TableCell>
                          <TableCell className="text-right text-muted-foreground">
                            {metric.correct.toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Confusion Matrix Tab */}
          <TabsContent value="confusion">
            <Card>
              <CardHeader>
                <CardTitle>Confusion Analysis</CardTitle>
                <CardDescription>
                  Most common prediction errors (what gets confused with what)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>True Label</TableHead>
                      <TableHead>Predicted As</TableHead>
                      <TableHead className="text-right">Count</TableHead>
                      <TableHead>Example</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {evaluationResult.confusion_matrix.slice(0, 20).map((entry, idx) => (
                      <TableRow key={idx}>
                        <TableCell>
                          <Badge
                            variant="outline"
                            style={{
                              borderColor: getEntityColor(entry.true_label),
                              color: getEntityColor(entry.true_label),
                            }}
                          >
                            {entry.true_label}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            style={{
                              borderColor: getEntityColor(entry.predicted_label),
                              color: getEntityColor(entry.predicted_label),
                            }}
                          >
                            {entry.predicted_label}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {entry.count.toLocaleString()}
                        </TableCell>
                        <TableCell className="max-w-md truncate text-sm text-muted-foreground">
                          {entry.examples[0]?.entity && (
                            <span className="font-medium">"{entry.examples[0].entity}"</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Error Analysis Tab */}
          <TabsContent value="errors">
            <Card>
              <CardHeader>
                <CardTitle>Error Examples</CardTitle>
                <CardDescription>
                  Sample false positives and false negatives for review
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {evaluationResult.error_examples.slice(0, 15).map((example, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-lg border bg-muted/30"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {example.error_type === 'false_negative' ? (
                          <Badge variant="destructive" className="flex items-center gap-1">
                            <XCircle className="h-3 w-3" />
                            Missed
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="flex items-center gap-1 border-yellow-500 text-yellow-600">
                            <AlertTriangle className="h-3 w-3" />
                            Extra
                          </Badge>
                        )}
                        <Badge
                          variant="outline"
                          style={{
                            borderColor: getEntityColor(example.entity_type),
                            color: getEntityColor(example.entity_type),
                          }}
                        >
                          {example.entity_type}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {example.text}
                      </p>
                      <div className="mt-2 flex gap-4 text-xs">
                        {example.true_entities.length > 0 && (
                          <div>
                            <span className="text-muted-foreground">Expected: </span>
                            <span className="font-medium text-green-600">
                              {example.true_entities.map((e) => e.text).join(', ')}
                            </span>
                          </div>
                        )}
                        {example.predicted_entities.length > 0 && (
                          <div>
                            <span className="text-muted-foreground">Predicted: </span>
                            <span className="font-medium text-red-600">
                              {example.predicted_entities.map((e) => e.text).join(', ')}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* No results state */}
      {!evaluationResult && !loading && (
        <Card>
          <CardContent className="py-12 text-center">
            <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Evaluation Results</h3>
            <p className="text-muted-foreground mb-4">
              Select a checkpoint and run an evaluation to see detailed metrics
            </p>
          </CardContent>
        </Card>
      )}

      {/* Loading state */}
      {loading && (
        <Card>
          <CardContent className="py-12 text-center">
            <Loader2 className="mx-auto h-12 w-12 text-primary animate-spin mb-4" />
            <h3 className="text-lg font-medium mb-2">Running Evaluation</h3>
            <p className="text-muted-foreground">
              Processing validation samples... This may take a few minutes for full evaluation.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
