import { Link, Outlet, useSearchParams, useRevalidator, useLocation } from 'react-router'
import type { Route } from "./+types/history"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { historyApi } from '@/services/api'
import { History as HistoryIcon, Clock, Tag, Trash2, ChevronLeft, ChevronRight, Star, RefreshCw } from 'lucide-react'

interface HistoryItem {
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
}

const LIMIT = 20

export async function clientLoader({ request }: Route.LoaderArgs) {
  const url = new URL(request.url)
  const page = parseInt(url.searchParams.get('page') || '1')

  const history = await historyApi.list({
    limit: LIMIT,
    offset: (page - 1) * LIMIT,
  })

  return { history: history as HistoryItem[], page }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

export default function History({ loaderData }: Route.ComponentProps) {
  const { history, page } = loaderData
  const [searchParams, setSearchParams] = useSearchParams()
  const revalidator = useRevalidator()
  const location = useLocation()

  // Extract the selected ID from the pathname (e.g., /history/123 -> 123)
  const pathParts = location.pathname.split('/')
  const selectedId = pathParts.length > 2 ? parseInt(pathParts[2]) : null

  const setPage = (newPage: number) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', String(newPage))
    setSearchParams(params)
  }

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Delete this extraction from history?')) return
    try {
      await historyApi.delete(id)
      revalidator.revalidate()
    } catch (e) {
      console.error('Failed to delete:', e)
    }
  }

  const isLoading = revalidator.state === 'loading'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Extraction History</h1>
          <p className="text-muted-foreground">
            View and manage past entity extractions
          </p>
        </div>
        <Button variant="outline" onClick={() => revalidator.revalidate()} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* History List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HistoryIcon className="h-5 w-5" />
              Recent Extractions
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {history.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <HistoryIcon className="h-12 w-12 mb-4" />
                <p>No extraction history</p>
                <p className="text-sm">Extractions will appear here after using the Testing page</p>
              </div>
            ) : (
              <div className="divide-y max-h-[600px] overflow-y-auto">
                {history.map((item) => (
                  <Link
                    key={item.id}
                    to={`/history/${item.id}`}
                    className={`block p-4 hover:bg-muted/50 cursor-pointer transition-colors ${
                      selectedId === item.id ? 'bg-primary/10' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm line-clamp-2 mb-2">{item.text}</p>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Tag className="h-3 w-3" />
                            {item.entity_count} entities
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {item.processing_time_ms?.toFixed(0)}ms
                          </span>
                          {item.user_rating && (
                            <span className="flex items-center gap-1">
                              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                              {item.user_rating}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-muted-foreground">
                            {formatDate(item.created_at)}
                          </span>
                          {item.saved_to_events && (
                            <span className="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded">
                              Saved
                            </span>
                          )}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => handleDelete(item.id, e)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detail View - Outlet for nested route */}
        <Card>
          <CardHeader>
            <CardTitle>Extraction Detail</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedId ? (
              <Outlet />
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <HistoryIcon className="h-12 w-12 mb-4" />
                <p>Select an extraction to view details</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="text-sm text-muted-foreground">Page {page}</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage(page + 1)}
          disabled={history.length < LIMIT}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
