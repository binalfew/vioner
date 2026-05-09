import { Link, useNavigate } from 'react-router'
import type { Route } from "./+types/history.$id"
import { Button } from '@/components/ui/button'
import { historyApi } from '@/services/api'
import { History as HistoryIcon, ExternalLink } from 'lucide-react'

interface HistoryDetail {
  id: number
  request_id: string
  text: string
  entity_count: number
  processing_time_ms: number | null
  model_version: string | null
  user_rating: number | null
  saved_to_events: boolean
  event_id: string | null
  created_at: string
  entities: Array<{ text: string; label: string; start: number; end: number; confidence: number }>
  structured_event: { who: string[]; whom: string[]; what: string[]; when: string[]; where: string[]; how: string[] }
  confidence_scores: Record<string, number>
}

export async function clientLoader({ params }: Route.LoaderArgs) {
  const detail = await historyApi.get(parseInt(params.id))
  return { detail: detail as HistoryDetail }
}

function getEntityColor(label: string): string {
  // WHO: Actors (1 type - merged)
  if (label.includes('ACTOR')) return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  // WHOM: Victims (1 type)
  if (label.includes('VICTIM')) return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
  // WHAT: Actions (1 type)
  if (label.includes('ACTION')) return 'bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200'
  // WHEN: Temporal (1 type)
  if (label.includes('DATE')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  // WHERE: Location (3 types)
  if (label.includes('REGION')) return 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200'
  if (label.includes('CITY')) return 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200'
  if (label.includes('DISTRICT')) return 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200'
  // HOW: Impact (1 type)
  if (label.includes('CASUALTIES')) return 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200'
  return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
}

export default function HistoryDetail({ loaderData }: Route.ComponentProps) {
  const { detail } = loaderData
  const navigate = useNavigate()

  const handleUseText = (text: string) => {
    navigate('/testing', { state: { text } })
  }

  if (!detail) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <HistoryIcon className="h-12 w-12 mb-4" />
        <p>Extraction not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with ID */}
      <div className="flex items-center justify-between text-xs text-muted-foreground pb-2 border-b">
        <span>ID: {detail.id}</span>
        <span>{detail.request_id.slice(0, 8)}...</span>
        <span>{new Date(detail.created_at).toLocaleString()}</span>
      </div>

      {/* Original Text */}
      <div>
        <h4 className="text-sm font-medium mb-2">Original Text</h4>
        <p className="text-sm bg-muted p-3 rounded-lg">{detail.text}</p>
        <Button
          variant="outline"
          size="sm"
          className="mt-2"
          onClick={() => handleUseText(detail.text)}
        >
          Re-extract
        </Button>
      </div>

      {/* Entities */}
      <div>
        <h4 className="text-sm font-medium mb-2">Extracted Entities ({detail.entities.length})</h4>
        <div className="flex flex-wrap gap-2">
          {detail.entities.map((entity, idx) => (
            <span
              key={idx}
              className={`px-2 py-1 rounded text-xs ${getEntityColor(entity.label)}`}
              title={`${entity.label} (${(entity.confidence * 100).toFixed(0)}%)`}
            >
              {entity.text}
              <span className="ml-1 opacity-60">{entity.label.replace('B-', '').replace('I-', '')}</span>
            </span>
          ))}
          {detail.entities.length === 0 && (
            <span className="text-sm text-muted-foreground">No entities extracted</span>
          )}
        </div>
      </div>

      {/* Structured Event */}
      <div>
        <h4 className="text-sm font-medium mb-2">Structured Event (5W1H)</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-muted p-2 rounded">
            <span className="font-medium">WHO:</span>{' '}
            {detail.structured_event.who?.join(', ') || '-'}
          </div>
          <div className="bg-muted p-2 rounded">
            <span className="font-medium">WHOM:</span>{' '}
            {detail.structured_event.whom?.join(', ') || '-'}
          </div>
          <div className="bg-muted p-2 rounded">
            <span className="font-medium">WHAT:</span>{' '}
            {detail.structured_event.what?.join(', ') || '-'}
          </div>
          <div className="bg-muted p-2 rounded">
            <span className="font-medium">WHEN:</span>{' '}
            {detail.structured_event.when?.join(', ') || '-'}
          </div>
          <div className="bg-muted p-2 rounded">
            <span className="font-medium">WHERE:</span>{' '}
            {detail.structured_event.where?.join(', ') || '-'}
          </div>
          <div className="bg-muted p-2 rounded">
            <span className="font-medium">HOW:</span>{' '}
            {detail.structured_event.how?.join(', ') || '-'}
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t">
        <span>Model: {detail.model_version || 'Unknown'}</span>
        <span>Time: {detail.processing_time_ms?.toFixed(0)}ms</span>
        {detail.saved_to_events && detail.event_id && (
          <Link
            to={`/events/${detail.event_id}`}
            className="flex items-center gap-1 text-primary hover:underline"
          >
            <ExternalLink className="h-3 w-3" />
            View Event
          </Link>
        )}
      </div>
    </div>
  )
}
