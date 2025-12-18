import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'

interface TrainingStatus {
  isRunning: boolean
  currentEpoch: number
  totalEpochs: number
  currentBatch: number
  totalBatches: number
  loss: number
  accuracy: number
  valLoss: number
  valAccuracy: number
  learningRate: number
  bestEpoch: number
  bestValLoss: number
  modelName: string
  startTime: string | null
  eta: string | null
}

interface TrainingContextType {
  status: TrainingStatus
  logs: string[]
  metrics: Array<{
    epoch: number
    loss: number
    accuracy: number
    valLoss: number
    valAccuracy: number
  }>
  connect: () => void
  disconnect: () => void
  isConnected: boolean
}

const defaultStatus: TrainingStatus = {
  isRunning: false,
  currentEpoch: 0,
  totalEpochs: 0,
  currentBatch: 0,
  totalBatches: 0,
  loss: 0,
  accuracy: 0,
  valLoss: 0,
  valAccuracy: 0,
  learningRate: 0,
  bestEpoch: 0,
  bestValLoss: 0,
  modelName: '',
  startTime: null,
  eta: null,
}

const TrainingContext = createContext<TrainingContextType | undefined>(undefined)

export function TrainingProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<TrainingStatus>(defaultStatus)
  const [logs, setLogs] = useState<string[]>([])
  const [metrics, setMetrics] = useState<TrainingContextType['metrics']>([])
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const connect = useCallback(() => {
    if (ws?.readyState === WebSocket.OPEN) return

    // Use proper protocol and port based on current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host // includes port if non-standard
    // In Docker/production, nginx proxies /ws/ to backend
    // In development, connect directly to port 8000
    const wsPort = window.location.port === '5173' ? ':8000' : ''
    const socket = new WebSocket(`${protocol}//${window.location.hostname}${wsPort}/ws/training/progress`)

    socket.onopen = () => {
      setIsConnected(true)
      console.log('WebSocket connected')
    }

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        if (message.type === 'init' || message.type === 'status') {
          const data = message.data
          // Backend returns status as string ("idle", "running", "completed", "stopped", etc.)
          const isRunning = data.status === 'running'
          const newStatus: TrainingStatus = {
            isRunning,
            currentEpoch: data.current_epoch || 0,
            totalEpochs: data.total_epochs || 0,
            currentBatch: data.current_batch || 0,
            totalBatches: data.total_batches || 0,
            loss: data.train_loss || 0,
            accuracy: data.accuracy || 0,
            valLoss: data.val_loss || 0,
            valAccuracy: data.val_accuracy || 0,
            learningRate: data.learning_rate || 0,
            bestEpoch: data.best_epoch || 0,
            bestValLoss: data.best_val_loss || 0,
            modelName: data.model_name || '',
            startTime: data.start_time || null,
            eta: data.eta ? `${Math.round(data.eta / 60)} min` : null,
          }
          setStatus(newStatus)

          // Log status changes for debugging
          if (data.status === 'stopped') {
            console.log('Training stopped, received status:', data.current_epoch, '/', data.total_epochs)
          }
        }

        if (message.type === 'progress') {
          const data = message.data
          setStatus(prev => ({
            ...prev,
            currentEpoch: data.epoch || prev.currentEpoch,
            currentBatch: data.batch || prev.currentBatch,
            totalBatches: data.total_batches || prev.totalBatches,
            loss: data.loss || prev.loss,
            accuracy: data.accuracy || prev.accuracy,
          }))
        }

        if (message.type === 'epoch_complete') {
          const data = message.data
          setMetrics(prev => [
            ...prev,
            {
              epoch: data.epoch,
              loss: data.train_loss,
              accuracy: data.train_accuracy,
              valLoss: data.val_loss,
              valAccuracy: data.val_accuracy,
            }
          ])
          setStatus(prev => ({
            ...prev,
            valLoss: data.val_loss,
            valAccuracy: data.val_accuracy,
            bestEpoch: data.best_epoch || prev.bestEpoch,
            bestValLoss: data.best_val_loss || prev.bestValLoss,
          }))
        }

        if (message.type === 'logs') {
          setLogs(message.data || [])
        }

        if (message.type === 'log') {
          setLogs(prev => [...prev, message.data])
        }

      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    socket.onclose = () => {
      setIsConnected(false)
      console.log('WebSocket disconnected')
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    setWs(socket)
  }, [ws])

  const disconnect = useCallback(() => {
    if (ws) {
      ws.close()
      setWs(null)
      setIsConnected(false)
    }
  }, [ws])

  // Auto-connect on mount
  useEffect(() => {
    connect()
    return () => {
      disconnect()
    }
  }, [])

  // Ping to keep connection alive
  useEffect(() => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return

    const interval = setInterval(() => {
      ws.send(JSON.stringify({ type: 'ping' }))
    }, 25000)

    return () => clearInterval(interval)
  }, [ws])

  return (
    <TrainingContext.Provider value={{ status, logs, metrics, connect, disconnect, isConnected }}>
      {children}
    </TrainingContext.Provider>
  )
}

export function useTraining() {
  const context = useContext(TrainingContext)
  if (context === undefined) {
    throw new Error('useTraining must be used within a TrainingProvider')
  }
  return context
}
