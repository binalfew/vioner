import { useState, useCallback } from 'react'
import { Upload, X, FileText, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { inferenceApi } from '@/services/api'
import { toast } from 'sonner'

interface UploadedFile {
  id: string
  file: File
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  result?: {
    entities: Array<{ text: string; label: string }>
    entity_count: number
  }
  error?: string
}

interface BatchUploadProps {
  onComplete?: (results: UploadedFile[]) => void
}

export function BatchUpload({ onComplete }: BatchUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === 'text/plain' || file.name.endsWith('.txt')
    )
    addFiles(droppedFiles)
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files))
    }
  }, [])

  const addFiles = (newFiles: File[]) => {
    const uploadedFiles: UploadedFile[] = newFiles.map((file) => ({
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      file,
      status: 'pending',
      progress: 0,
    }))
    setFiles((prev) => [...prev, ...uploadedFiles])
  }

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  const processFiles = async () => {
    if (files.length === 0) return

    setIsProcessing(true)
    const updatedFiles = [...files]

    for (let i = 0; i < updatedFiles.length; i++) {
      const file = updatedFiles[i]
      if (file.status !== 'pending') continue

      // Update status to processing
      updatedFiles[i] = { ...file, status: 'processing', progress: 0 }
      setFiles([...updatedFiles])

      try {
        // Read file content
        const text = await file.file.text()

        // Update progress
        updatedFiles[i] = { ...updatedFiles[i], progress: 50 }
        setFiles([...updatedFiles])

        // Call API
        const result = await inferenceApi.extract(text)

        // Update with result
        updatedFiles[i] = {
          ...updatedFiles[i],
          status: 'completed',
          progress: 100,
          result: {
            entities: result.entities || [],
            entity_count: result.entities?.length || 0,
          },
        }
        setFiles([...updatedFiles])

      } catch (error) {
        updatedFiles[i] = {
          ...updatedFiles[i],
          status: 'error',
          progress: 0,
          error: error instanceof Error ? error.message : 'Processing failed',
        }
        setFiles([...updatedFiles])
      }
    }

    setIsProcessing(false)

    const completedCount = updatedFiles.filter((f) => f.status === 'completed').length
    const errorCount = updatedFiles.filter((f) => f.status === 'error').length

    if (completedCount > 0) {
      toast.success(`Processed ${completedCount} file(s) successfully`)
    }
    if (errorCount > 0) {
      toast.error(`${errorCount} file(s) failed to process`)
    }

    onComplete?.(updatedFiles)
  }

  const clearAll = () => {
    setFiles([])
  }

  const totalEntities = files.reduce(
    (sum, f) => sum + (f.result?.entity_count || 0),
    0
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Batch Upload
        </CardTitle>
        <CardDescription>
          Upload multiple text files for batch entity extraction
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center transition-colors
            ${isDragging
              ? 'border-primary bg-primary/5'
              : 'border-border hover:border-primary/50'
            }
          `}
        >
          <Upload className="mx-auto h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-sm text-muted-foreground mb-2">
            Drag and drop text files here, or
          </p>
          <label>
            <input
              type="file"
              accept=".txt,text/plain"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />
            <Button variant="outline" asChild>
              <span className="cursor-pointer">Browse Files</span>
            </Button>
          </label>
          <p className="text-xs text-muted-foreground mt-2">
            Supports .txt files (max 50 files)
          </p>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                {files.length} file(s) • {totalEntities} entities extracted
              </span>
              <Button variant="ghost" size="sm" onClick={clearAll}>
                Clear All
              </Button>
            </div>

            <div className="max-h-[300px] overflow-y-auto space-y-2">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center gap-3 p-3 rounded-lg border bg-card"
                >
                  <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.file.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {file.status === 'pending' && (
                        <span className="text-xs text-muted-foreground">Ready</span>
                      )}
                      {file.status === 'processing' && (
                        <>
                          <Loader2 className="h-3 w-3 animate-spin text-primary" />
                          <Progress value={file.progress} className="flex-1 h-1" />
                        </>
                      )}
                      {file.status === 'completed' && (
                        <>
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                          <span className="text-xs text-green-600">
                            {file.result?.entity_count} entities
                          </span>
                        </>
                      )}
                      {file.status === 'error' && (
                        <>
                          <AlertCircle className="h-3 w-3 text-destructive" />
                          <span className="text-xs text-destructive">{file.error}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(file.id)}
                    disabled={file.status === 'processing'}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        {files.length > 0 && (
          <Button
            onClick={processFiles}
            disabled={isProcessing || files.every((f) => f.status !== 'pending')}
            className="w-full"
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Process {files.filter((f) => f.status === 'pending').length} File(s)
              </>
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
