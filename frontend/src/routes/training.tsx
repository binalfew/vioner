import { useState } from 'react'
import { useRevalidator } from 'react-router'
import type { Route } from "./+types/training"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { trainingApi, type TrainingRun } from '@/services/api'
import { useTraining } from '@/context/TrainingContext'
import { TrainingDataUpload } from '@/components/TrainingDataUpload'
import { Play, Square, RefreshCw, Zap, RotateCcw } from 'lucide-react'

// React Router 7 clientLoader - fetches training defaults and previous sessions
export async function clientLoader() {
  const [defaults, runsData] = await Promise.all([
    trainingApi.getDefaults().catch(() => null),
    trainingApi.listRuns().catch(() => ({ trainings: [] }))
  ])
  return {
    defaults,
    previousSessions: runsData.trainings as TrainingRun[]
  }
}

export default function Training({ loaderData }: Route.ComponentProps) {
  const { defaults, previousSessions } = loaderData
  const { status, logs } = useTraining()
  const revalidator = useRevalidator()

  const [config, setConfig] = useState({
    model_name: 'bert-base-cased',
    epochs: 10,
    batch_size: 4,  // Smaller batch size for CPU training (avoids OOM)
    learning_rate: 2e-5,
    warmup_steps: 500,
    weight_decay: 0.01,
    max_length: 128,
    run_epochs: undefined as number | undefined,  // Run only N epochs this session (undefined = all)
    // Don't specify train_file/val_file - let backend use its defaults
    // Backend will use /app/data/processed/ paths in Docker
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Resume from session state
  const [selectedSessionId, setSelectedSessionId] = useState<string>('')
  const [additionalEpochs, setAdditionalEpochs] = useState<number>(0)
  const [runEpochs, setRunEpochs] = useState<number>(1)

  // Get the selected session details
  const selectedSession = previousSessions.find(s => s.id.toString() === selectedSessionId)

  // Filter resumable sessions (those with checkpoint_path)
  // Completed sessions can be resumed with extend_epochs to add more training
  const resumableSessions = previousSessions.filter(s => s.checkpoint_path)

  const handleStart = async () => {
    setLoading(true)
    setError(null)
    try {
      await trainingApi.start(config)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start training')
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      await trainingApi.stop()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to stop training')
    } finally {
      setLoading(false)
    }
  }

  const handleResumeSession = async () => {
    if (!selectedSession || !selectedSession.checkpoint_path) return
    setLoading(true)
    setError(null)
    try {
      await trainingApi.resume(selectedSession.checkpoint_path, {
        extendEpochs: additionalEpochs,
        runEpochs: runEpochs,
      })
      setSelectedSessionId('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to resume session')
    } finally {
      setLoading(false)
    }
  }

  const applyPreset = (preset: { name: string; epochs: number; batch_size: number; learning_rate: number }) => {
    setConfig(prev => ({
      ...prev,
      epochs: preset.epochs,
      batch_size: preset.batch_size,
      learning_rate: preset.learning_rate,
    }))
  }

  const epochProgress = status.totalEpochs > 0
    ? (status.currentEpoch / status.totalEpochs) * 100
    : 0

  const batchProgress = status.totalBatches > 0
    ? (status.currentBatch / status.totalBatches) * 100
    : 0

  const isLoading = revalidator.state === 'loading'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Model Training</h1>
        <p className="text-muted-foreground">
          Fine-tune BERT models for violent event entity recognition
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 p-4 text-destructive">
          {error}
        </div>
      )}

      {/* Resume from Previous Session */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RotateCcw className="h-5 w-5" />
            Resume Training
          </CardTitle>
          <CardDescription>
            Continue training from a previous session ({resumableSessions.length} available)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {resumableSessions.length > 0 ? (
            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-4">
                <div className="space-y-2 sm:col-span-2">
                  <Label>Select Session</Label>
                  <Select
                    value={selectedSessionId}
                    onValueChange={setSelectedSessionId}
                    disabled={status.isRunning}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a session to resume..." />
                    </SelectTrigger>
                    <SelectContent>
                      {resumableSessions.map((session) => (
                        <SelectItem key={session.id} value={session.id.toString()}>
                          <div className="flex items-center gap-2">
                            <span>{session.session_id}</span>
                            <span className="text-xs text-muted-foreground">
                              ({session.epochs_completed}/{session.epochs_total} epochs, {session.status})
                            </span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Run epochs</Label>
                  <Input
                    type="number"
                    value={runEpochs}
                    onChange={(e) => setRunEpochs(Math.max(1, parseInt(e.target.value) || 1))}
                    min={1}
                    max={100}
                    disabled={status.isRunning || !selectedSessionId}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Extend by</Label>
                  <Input
                    type="number"
                    value={additionalEpochs}
                    onChange={(e) => setAdditionalEpochs(Math.max(0, parseInt(e.target.value) || 0))}
                    min={0}
                    max={50}
                    placeholder="0 epochs"
                    disabled={status.isRunning || !selectedSessionId}
                  />
                </div>
              </div>
              {selectedSession && (
                <div className="flex items-center justify-between rounded-lg border bg-muted/30 p-3">
                  <div className="space-y-1">
                    <div className="text-sm font-medium">{selectedSession.model_name}</div>
                    <div className="text-xs text-muted-foreground">
                      Val Loss: {selectedSession.best_val_loss?.toFixed(4) || '-'}
                      {' • '}
                      Status: <span className={selectedSession.status === 'stopped' ? 'text-yellow-600' : selectedSession.status === 'completed' ? 'text-green-600' : ''}>{selectedSession.status}</span>
                      {' • '}
                      <span className="truncate" title={selectedSession.checkpoint_path || ''}>
                        {selectedSession.checkpoint_path?.split('/').pop() || 'N/A'}
                      </span>
                    </div>
                  </div>
                  <Button
                    onClick={handleResumeSession}
                    disabled={loading || status.isRunning}
                  >
                    {loading ? (
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <RotateCcw className="mr-2 h-4 w-4" />
                    )}
                    {additionalEpochs > 0 ? `Resume (+${additionalEpochs})` : 'Continue Training'}
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              No previous sessions found. Go to <span className="font-medium">Models</span> page and click <span className="font-medium">Sync from Disk</span> to load existing checkpoints.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Training Data */}
      <TrainingDataUpload
        disabled={status.isRunning}
        onDataProcessed={() => revalidator.revalidate()}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Training Configuration</CardTitle>
            <CardDescription>Configure model and hyperparameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Presets */}
            {defaults?.presets && (
              <div>
                <Label className="mb-2 block">Quick Presets</Label>
                <div className="flex flex-wrap gap-2">
                  {defaults.presets.map((preset: { name: string; epochs: number; batch_size: number; learning_rate: number }) => (
                    <Button
                      key={preset.name}
                      variant="outline"
                      size="sm"
                      onClick={() => applyPreset(preset)}
                      disabled={status.isRunning}
                    >
                      <Zap className="mr-1 h-3 w-3" />
                      {preset.name}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Model Selection */}
            <div className="space-y-2">
              <Label>Base Model</Label>
              <Select
                value={config.model_name}
                onValueChange={(value) => setConfig(prev => ({ ...prev, model_name: value }))}
                disabled={status.isRunning}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(defaults?.model_options || ['bert-base-cased', 'bert-base-uncased']).map((model: string) => (
                    <SelectItem key={model} value={model}>{model}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Hyperparameters */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Total Epochs</Label>
                <Input
                  type="number"
                  value={config.epochs}
                  onChange={(e) => setConfig(prev => ({ ...prev, epochs: parseInt(e.target.value) || 1 }))}
                  min={1}
                  max={100}
                  disabled={status.isRunning}
                />
              </div>
              <div className="space-y-2">
                <Label>Run This Session</Label>
                <Input
                  type="number"
                  value={config.run_epochs || ''}
                  onChange={(e) => {
                    const val = e.target.value ? parseInt(e.target.value) : undefined
                    setConfig(prev => ({ ...prev, run_epochs: val }))
                  }}
                  min={1}
                  max={config.epochs}
                  placeholder={`All (${config.epochs})`}
                  disabled={status.isRunning}
                />
                <p className="text-xs text-muted-foreground">
                  Leave empty to run all epochs, or set to run fewer now and resume later.
                </p>
              </div>
              <div className="space-y-2">
                <Label>Batch Size</Label>
                <Input
                  type="number"
                  value={config.batch_size}
                  onChange={(e) => setConfig(prev => ({ ...prev, batch_size: parseInt(e.target.value) || 4 }))}
                  min={1}
                  max={64}
                  disabled={status.isRunning}
                />
                <p className="text-xs text-muted-foreground">
                  CPU: 4-8 recommended. Higher values may cause OOM.
                </p>
              </div>
              <div className="space-y-2">
                <Label>Learning Rate</Label>
                <Input
                  type="number"
                  value={config.learning_rate}
                  onChange={(e) => setConfig(prev => ({ ...prev, learning_rate: parseFloat(e.target.value) || 2e-5 }))}
                  step={1e-6}
                  disabled={status.isRunning}
                />
              </div>
              <div className="space-y-2">
                <Label>Max Length</Label>
                <Input
                  type="number"
                  value={config.max_length}
                  onChange={(e) => setConfig(prev => ({ ...prev, max_length: parseInt(e.target.value) || 128 }))}
                  min={32}
                  max={512}
                  disabled={status.isRunning}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-4">
              {!status.isRunning ? (
                <Button onClick={handleStart} disabled={loading} className="flex-1">
                  <Play className="mr-2 h-4 w-4" />
                  Start Training
                </Button>
              ) : (
                <Button onClick={handleStop} disabled={loading} variant="destructive" className="flex-1">
                  <Square className="mr-2 h-4 w-4" />
                  Stop Training
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Training Progress
              {status.isRunning && (
                <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              )}
            </CardTitle>
            <CardDescription>
              {status.isRunning
                ? (status.totalEpochs === 0
                    ? `Loading ${status.modelName || 'model'}...`
                    : 'Training in progress...')
                : 'No active training session'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Loading State */}
            {status.isRunning && status.totalEpochs === 0 && (
              <div className="flex items-center justify-center p-8">
                <div className="flex flex-col items-center gap-3">
                  <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    {status.modelName ? `Loading ${status.modelName}...` : 'Initializing...'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    This may take a minute for first-time model download
                  </p>
                </div>
              </div>
            )}

            {/* Epoch Progress */}
            {(!status.isRunning || status.totalEpochs > 0) && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Epoch Progress</span>
                <span>{status.currentEpoch} / {status.totalEpochs}</span>
              </div>
              <Progress value={epochProgress} />
            </div>
            )}

            {/* Batch Progress */}
            {(!status.isRunning || status.totalEpochs > 0) && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Batch Progress</span>
                <span>{status.currentBatch} / {status.totalBatches}</span>
              </div>
              <Progress value={batchProgress} />
            </div>
            )}

            {/* Metrics - only show when training has started */}
            {(!status.isRunning || status.totalEpochs > 0) && (
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3">
                <p className="text-sm text-muted-foreground">Training Loss</p>
                <p className="text-2xl font-bold">{status.loss.toFixed(4)}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-sm text-muted-foreground">Accuracy</p>
                <p className="text-2xl font-bold">{(status.accuracy * 100).toFixed(2)}%</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-sm text-muted-foreground">Val Loss</p>
                <p className="text-2xl font-bold">{status.valLoss.toFixed(4)}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-sm text-muted-foreground">Best Epoch</p>
                <p className="text-2xl font-bold">{status.bestEpoch || '-'}</p>
              </div>
            </div>
            )}

            {status.eta && status.totalEpochs > 0 && (
              <div className="text-center text-sm text-muted-foreground">
                Estimated time remaining: {status.eta}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Logs */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Training Logs</CardTitle>
            <CardDescription>Real-time training output</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => trainingApi.getLogs()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          <div className="max-h-[400px] overflow-auto rounded-lg bg-muted p-4 font-mono text-sm">
            {logs.length > 0 ? (
              logs.map((log, i) => (
                <div key={i} className="whitespace-pre-wrap">
                  {log}
                </div>
              ))
            ) : (
              <p className="text-muted-foreground">No logs available</p>
            )}
          </div>
        </CardContent>
      </Card>

    </div>
  )
}
