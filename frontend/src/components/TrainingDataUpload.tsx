import { useState, useCallback } from 'react'
import {
  Upload,
  FileSpreadsheet,
  AlertCircle,
  CheckCircle2,
  Loader2,
  X,
  Eye,
  Database,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  trainingApi,
  type ValidationResponse,
  type SampleEvent,
  type ProcessingProgressResponse,
} from '@/services/api'

interface TrainingDataUploadProps {
  disabled?: boolean
  onDataProcessed?: () => void
}

type UploadState =
  | 'idle'
  | 'uploading'
  | 'validated'
  | 'processing'
  | 'complete'
  | 'error'

// Entity type to color mapping (8 types optimized for grounding)
const ENTITY_COLORS: Record<string, string> = {
  // WHO (1 type - merged)
  ACTOR: 'bg-red-100 text-red-800 border-red-200',
  // WHOM (1 type)
  VICTIM: 'bg-orange-100 text-orange-800 border-orange-200',
  // WHAT (1 type)
  ACTION: 'bg-violet-100 text-violet-800 border-violet-200',
  // WHEN (1 type)
  DATE: 'bg-blue-100 text-blue-800 border-blue-200',
  // WHERE (3 types)
  REGION: 'bg-teal-100 text-teal-800 border-teal-200',
  CITY: 'bg-cyan-100 text-cyan-800 border-cyan-200',
  DISTRICT: 'bg-sky-100 text-sky-800 border-sky-200',
  // HOW (1 type)
  CASUALTIES: 'bg-rose-100 text-rose-800 border-rose-200',
}

export function TrainingDataUpload({
  disabled = false,
  onDataProcessed,
}: TrainingDataUploadProps) {
  const [state, setState] = useState<UploadState>('idle')
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [validation, setValidation] = useState<ValidationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [processingProgress, setProcessingProgress] = useState<ProcessingProgressResponse | null>(null)

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      if (!disabled) setIsDragging(true)
    },
    [disabled]
  )

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      if (disabled) return

      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile?.name.endsWith('.csv')) {
        handleFileSelect(droppedFile)
      } else {
        setError('Please upload a CSV file')
        setState('error')
      }
    },
    [disabled]
  )

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile)
    setError(null)
    setState('uploading')

    try {
      const result = await trainingApi.validateData(selectedFile)
      setValidation(result)

      if (result.valid) {
        setState('validated')
        setShowPreview(true)
      } else {
        setState('error')
        setError(result.errors.map((e) => e.message).join(', '))
      }
    } catch (e) {
      setState('error')
      setError(e instanceof Error ? e.message : 'Validation failed')
    }
  }

  const handleConfirmProcess = async () => {
    if (!validation?.validation_token) return

    setShowPreview(false)
    setState('processing')
    setProcessingProgress(null)

    // Start polling for progress
    const progressInterval = setInterval(async () => {
      try {
        const progress = await trainingApi.getProcessingProgress()
        setProcessingProgress(progress)
      } catch {
        // Ignore polling errors
      }
    }, 500)

    try {
      const result = await trainingApi.processData(validation.validation_token)
      clearInterval(progressInterval)

      // Fetch final progress state
      const finalProgress = await trainingApi.getProcessingProgress()
      setProcessingProgress(finalProgress)

      if (result.success) {
        setState('complete')
        onDataProcessed?.()
      } else {
        setState('error')
        setError(result.message)
      }
    } catch (e) {
      clearInterval(progressInterval)
      setState('error')
      setError(e instanceof Error ? e.message : 'Processing failed')
    }
  }

  const handleReset = () => {
    setState('idle')
    setFile(null)
    setValidation(null)
    setError(null)
    setProcessingProgress(null)
  }

  const renderEntityBadges = (entities: SampleEvent['entities']) => (
    <div className="flex flex-wrap gap-1 mt-2">
      {entities.map((entity, idx) => (
        <Badge
          key={idx}
          variant="outline"
          className={`text-xs ${ENTITY_COLORS[entity.type] || 'bg-gray-100'}`}
        >
          {entity.text}{' '}
          <span className="opacity-60 ml-1">({entity.type})</span>
        </Badge>
      ))}
    </div>
  )

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Upload Training Data
          </CardTitle>
          <CardDescription>
            Upload a CSV file to replace current training data
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Drop Zone */}
          {(state === 'idle' || state === 'error') && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                border-2 border-dashed rounded-lg p-6 text-center transition-colors
                ${isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <FileSpreadsheet className="mx-auto h-8 w-8 text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground mb-2">
                Drag and drop your CSV file here, or
              </p>
              <label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) =>
                    e.target.files?.[0] && handleFileSelect(e.target.files[0])
                  }
                  className="hidden"
                  disabled={disabled}
                />
                <Button
                  variant="outline"
                  size="sm"
                  asChild
                  disabled={disabled}
                >
                  <span className="cursor-pointer">Browse Files</span>
                </Button>
              </label>
              <p className="text-xs text-muted-foreground mt-2">
                Required columns: Event_ID, Event_Description
              </p>
            </div>
          )}

          {/* Uploading State */}
          {state === 'uploading' && (
            <div className="flex items-center gap-3 p-4 rounded-lg border bg-muted/30">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <div className="flex-1">
                <p className="text-sm font-medium">
                  Validating {file?.name}...
                </p>
                <p className="text-xs text-muted-foreground">
                  Checking format and extracting sample entities
                </p>
              </div>
            </div>
          )}

          {/* Validated State (waiting for confirmation) */}
          {state === 'validated' && validation && (
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-4 rounded-lg border bg-green-50 dark:bg-green-900/20">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-800 dark:text-green-200">
                    {validation.filename} validated
                  </p>
                  <p className="text-xs text-green-700 dark:text-green-300">
                    {validation.total_rows?.toLocaleString()} events found
                  </p>
                </div>
                <Button variant="ghost" size="icon" onClick={handleReset}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => setShowPreview(true)}
                  variant="outline"
                  className="flex-1"
                >
                  <Eye className="mr-2 h-4 w-4" />
                  Preview Entities
                </Button>
                <Button onClick={handleConfirmProcess} className="flex-1">
                  <Upload className="mr-2 h-4 w-4" />
                  Process & Replace Data
                </Button>
              </div>
            </div>
          )}

          {/* Processing State */}
          {state === 'processing' && (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                <div className="flex-1">
                  <p className="text-sm font-medium">
                    {processingProgress?.message || 'Processing training data...'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {processingProgress?.phase === 'saving'
                      ? 'Splitting into train/val and saving files'
                      : 'Converting to BIO-tagged format'}
                  </p>
                </div>
              </div>
              <Progress value={processingProgress?.percent_complete ?? 0} />
            </div>
          )}

          {/* Complete State */}
          {state === 'complete' && (
            <div className="flex items-center gap-3 p-4 rounded-lg border bg-green-50 dark:bg-green-900/20">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-green-800 dark:text-green-200">
                  Training data updated successfully
                </p>
                <p className="text-xs text-green-700 dark:text-green-300">
                  Ready for model training
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={handleReset}>
                Upload New
              </Button>
            </div>
          )}

          {/* Error State */}
          {error && state === 'error' && (
            <div className="flex items-start gap-3 p-4 rounded-lg border bg-destructive/10">
              <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-destructive">
                  Upload Failed
                </p>
                <p className="text-xs text-destructive/80">{error}</p>
              </div>
              <Button variant="ghost" size="icon" onClick={handleReset}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}

          {disabled && (
            <p className="text-xs text-muted-foreground text-center">
              Cannot upload while training is in progress
            </p>
          )}
        </CardContent>
      </Card>

      {/* Preview Dialog */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Entity Extraction Preview</DialogTitle>
            <DialogDescription>
              Preview of entities that will be extracted from your training data
            </DialogDescription>
          </DialogHeader>

          {validation && (
            <div className="space-y-4">
              {/* Entity Statistics */}
              <div>
                <h4 className="text-sm font-medium mb-2">
                  Entity Statistics (Estimated)
                </h4>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(validation.entity_statistics).map(
                    ([type, count]) => (
                      <div
                        key={type}
                        className="text-center p-2 rounded-lg border"
                      >
                        <p className="text-lg font-bold">
                          {count.toLocaleString()}
                        </p>
                        <p className="text-xs text-muted-foreground">{type}</p>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Sample Events */}
              <div>
                <h4 className="text-sm font-medium mb-2">
                  Sample Events ({validation.sample_events.length})
                </h4>
                <div className="space-y-3">
                  {validation.sample_events.map((event, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg border bg-muted/30"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="text-xs">
                          {event.event_id}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {event.text}
                      </p>
                      {renderEntityBadges(event.entities)}
                    </div>
                  ))}
                </div>
              </div>

              {/* Warning about replacement */}
              <div className="flex items-start gap-2 p-3 rounded-lg border bg-yellow-50 dark:bg-yellow-900/20">
                <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                <p className="text-xs text-yellow-800 dark:text-yellow-200">
                  This will replace your existing training data. Make sure to
                  backup if needed.
                </p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPreview(false)}>
              Cancel
            </Button>
            <Button onClick={handleConfirmProcess}>Confirm & Process</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
