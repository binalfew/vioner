import { useState, useEffect } from 'react'
import { useRevalidator, useNavigate } from 'react-router'
import type { Route } from "./+types/models"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { trainingApi, inferenceApi, eventsApi, type TrainingRun } from '@/services/api'
import type { ExtractionResult } from '@/types'
import {
  RefreshCw,
  Download,
  Check,
  Star,
  Clock,
  AlertCircle,
  Box,
  FlaskConical,
  Loader2,
  Save,
  Pencil,
  Zap
} from 'lucide-react'

// Example texts for testing
const EXAMPLE_TEXTS = [
  "On January 15, 2024, a coalition of Al Shabaab and ISIS-affiliated militants launched a coordinated assault on Ethiopian National Defense Force positions near Beledweyne, Somalia, using improvised explosive devices and heavy machine guns, resulting in 47 soldiers killed and over 80 wounded, while 12 civilians died in the crossfire.",
  "Boko Haram insurgents and ISWAP fighters conducted simultaneous raids on three villages in Borno State, Nigeria between March 3rd and March 5th, abducting 200 women and children, executing 34 local militia members, and burning the Maiduguri-Damaturu highway checkpoint, forcing 15,000 residents to flee to Cameroon.",
  "The Rapid Support Forces artillery units bombarded the Omdurman district of Khartoum with mortars and rocket-propelled grenades on Tuesday morning, while Sudanese Armed Forces jets conducted airstrikes on RSF positions in Nyala, South Darfur, with combined casualties estimated at 120 dead including 45 children and medical staff at the Al-Nao Hospital.",
  "M23 rebels, allegedly backed by Rwandan forces, seized control of Rutshuru and Kiwanja in North Kivu province of the Democratic Republic of Congo on December 20th after intense clashes with FARDC troops and MONUSCO peacekeepers, displacing approximately 450,000 civilians toward Goma and the Ugandan border.",
  "In retaliation for last week's massacre in Plateau State, Fulani herdsmen armed with AK-47s and machetes attacked Berom farming communities in Jos South on Saturday night, killing 67 villagers including women and elderly, while survivors reported that Nigerian Army soldiers stationed nearby failed to intervene despite two hours of gunfire.",
  "Somali pirates operating from Puntland hijacked a Turkish-owned cargo vessel with 23 Filipino and Indian crew members off the coast of Mogadishu on April 8th, demanding a $5 million ransom, while Al Shabaab militants simultaneously attacked the Kenyan Defense Forces base in Lamu County, killing 3 American military contractors and 8 Kenyan soldiers.",
]

const ENTITY_COLORS: Record<string, string> = {
  PERPETRATOR: 'bg-red-500/20 text-red-700 dark:text-red-300 border-red-500',
  VICTIM: 'bg-orange-500/20 text-orange-700 dark:text-orange-300 border-orange-500',
  ACTOR: 'bg-yellow-500/20 text-yellow-700 dark:text-yellow-300 border-yellow-500',
  GROUP: 'bg-pink-500/20 text-pink-700 dark:text-pink-300 border-pink-500',
  EVENT_TYPE: 'bg-purple-500/20 text-purple-700 dark:text-purple-300 border-purple-500',
  WEAPON: 'bg-slate-500/20 text-slate-700 dark:text-slate-300 border-slate-500',
  DATE: 'bg-blue-500/20 text-blue-700 dark:text-blue-300 border-blue-500',
  COUNTRY: 'bg-green-500/20 text-green-700 dark:text-green-300 border-green-500',
  CITY: 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-500',
  LOCATION: 'bg-teal-500/20 text-teal-700 dark:text-teal-300 border-teal-500',
  CASUALTIES: 'bg-rose-500/20 text-rose-700 dark:text-rose-300 border-rose-500',
}

interface EventFormData {
  event_description: string
  actor_normalized: string
  victim_normalized: string
  location_country: string
  location_city: string
  date_normalized: string
  taxonomy_l1: string
  deaths: number
  injuries: number
}

// Helper to extract session_id from model path
function extractSessionId(path: string | null): string | null {
  if (!path) return null
  // Handle paths like /app/models/bert-base-cased_xxx/best or ./models/bert-base-cased_xxx/best
  const parts = path.split('/')
  for (const part of parts) {
    if (part.startsWith('bert-') || part.startsWith('roberta-') || part.startsWith('distilbert-')) {
      return part
    }
  }
  return null
}

// React Router 7 clientLoader - fetches data before component renders
export async function clientLoader() {
  const [runsData, modelInfo] = await Promise.all([
    trainingApi.listRuns().catch(() => ({ trainings: [], recommended_id: null, recommended_reason: null, active_id: null })),
    inferenceApi.getModelInfo().catch(() => null)
  ])
  return {
    ...runsData,
    // Extract session_id from the model path for environment-agnostic tracking
    currentSessionId: extractSessionId(modelInfo?.model_path || null)
  }
}

export default function Models({ loaderData }: Route.ComponentProps) {
  const { trainings, recommended_id, recommended_reason, active_id, currentSessionId: initialSessionId } = loaderData
  const revalidator = useRevalidator()
  const navigate = useNavigate()

  // Model management state
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [syncing, setSyncing] = useState(false)
  const [switchingModel, setSwitchingModel] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(initialSessionId)

  // Testing state
  const [text, setText] = useState('')
  const [result, setResult] = useState<ExtractionResult | null>(null)
  const [extracting, setExtracting] = useState(false)

  // Save dialog state
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [savedEventId, setSavedEventId] = useState<string | null>(null)

  // Form data for editing before save
  const [formData, setFormData] = useState<EventFormData>({
    event_description: '',
    actor_normalized: '',
    victim_normalized: '',
    location_country: '',
    location_city: '',
    date_normalized: '',
    taxonomy_l1: 'Unknown',
    deaths: 0,
    injuries: 0,
  })

  // Update form data when extraction result changes
  useEffect(() => {
    if (result) {
      const structured = result.structured_event
      let deaths = 0
      let injuries = 0

      structured.how?.forEach(h => {
        const deathMatch = h.match(/(\d+)\s*(dead|killed|deaths?)/i)
        const injuryMatch = h.match(/(\d+)\s*(injured|injuries|wounded)/i)
        if (deathMatch) deaths = parseInt(deathMatch[1])
        if (injuryMatch) injuries = parseInt(injuryMatch[1])
      })

      result.entities.forEach(e => {
        if (e.label === 'CASUALTIES') {
          const deathMatch = e.text.match(/(\d+)\s*(dead|killed|deaths?)/i)
          const injuryMatch = e.text.match(/(\d+)\s*(injured|injuries|wounded)/i)
          if (deathMatch) deaths = parseInt(deathMatch[1])
          if (injuryMatch) injuries = parseInt(injuryMatch[1])
        }
      })

      setFormData({
        event_description: result.text,
        actor_normalized: structured.who?.[0] || '',
        victim_normalized: structured.who?.[1] || '',
        location_country: structured.where?.find(w =>
          result.entities.some(e => e.label === 'COUNTRY' && e.text === w)
        ) || structured.where?.[0] || '',
        location_city: structured.where?.find(w =>
          result.entities.some(e => e.label === 'CITY' && e.text === w)
        ) || '',
        date_normalized: structured.when?.[0] || '',
        taxonomy_l1: structured.what?.[0] || 'Violence against civilians',
        deaths,
        injuries,
      })
    }
  }, [result])

  // Handlers
  const handleSync = async () => {
    setSyncing(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await trainingApi.syncModels()
      setSuccess(result.message)
      revalidator.revalidate()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to sync models')
    } finally {
      setSyncing(false)
    }
  }

  const handleSwitchModel = async (model: TrainingRun) => {
    if (!model.session_id) return
    setSwitchingModel(true)
    setError(null)
    setSuccess(null)
    try {
      // Load model into memory using session_id (path resolved at runtime by backend)
      await inferenceApi.switchModel(model.session_id, 'best')
      // Also activate it persistently in database
      await trainingApi.activateModel(model.id)
      setCurrentSessionId(model.session_id)
      setSuccess(`Model ${model.session_id} activated successfully`)
      setResult(null) // Clear previous results
      revalidator.revalidate()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to switch model')
    } finally {
      setSwitchingModel(false)
    }
  }

  const handleExtract = async () => {
    if (!text.trim()) return
    setExtracting(true)
    setError(null)
    setSaveSuccess(false)
    setSavedEventId(null)
    try {
      const data = await inferenceApi.extract(text)
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Extraction failed')
    } finally {
      setExtracting(false)
    }
  }

  const handleSaveEvent = async () => {
    setSaving(true)
    setError(null)
    try {
      const response = await eventsApi.create({
        event_description: formData.event_description,
        actor_normalized: formData.actor_normalized || undefined,
        victim_normalized: formData.victim_normalized || undefined,
        location_country: formData.location_country || 'Unknown',
        location_city: formData.location_city || undefined,
        date_normalized: formData.date_normalized || undefined,
        taxonomy_l1: formData.taxonomy_l1 || 'Unknown',
        deaths: formData.deaths,
        injuries: formData.injuries,
      })
      setSaveSuccess(true)
      setSavedEventId(response.event_id)
      setSaveDialogOpen(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save event')
    } finally {
      setSaving(false)
    }
  }

  // Helper functions
  const isModelActive = (model: TrainingRun) => {
    if (!currentSessionId) return false
    return currentSessionId === model.session_id
  }

  const bestModel = trainings.reduce((best: TrainingRun | null, current: TrainingRun) => {
    if (!best) return current
    if (!current.best_val_loss) return best
    if (!best.best_val_loss) return current
    return current.best_val_loss < best.best_val_loss ? current : best
  }, null as TrainingRun | null)

  const renderHighlightedText = () => {
    if (!result) return null

    const sortedEntities = [...result.entities].sort((a, b) => a.start - b.start)
    const parts: JSX.Element[] = []
    let lastEnd = 0

    sortedEntities.forEach((entity, idx) => {
      if (entity.start > lastEnd) {
        parts.push(
          <span key={`text-${idx}`}>{result.text.slice(lastEnd, entity.start)}</span>
        )
      }

      const colorClass = ENTITY_COLORS[entity.label] || 'bg-gray-500/20 text-gray-700 border-gray-500'
      parts.push(
        <span
          key={`entity-${idx}`}
          className={`inline rounded px-1 py-0.5 border ${colorClass}`}
          title={`${entity.label} (${(entity.confidence * 100).toFixed(1)}%)`}
        >
          <span className="font-medium">{entity.text}</span>
          <sup className="ml-0.5 text-[9px] font-semibold opacity-60">{entity.label}</sup>
        </span>
      )

      lastEnd = entity.end
    })

    if (lastEnd < result.text.length) {
      parts.push(<span key="text-end">{result.text.slice(lastEnd)}</span>)
    }

    return parts
  }

  const isLoading = revalidator.state === 'loading' || syncing || switchingModel

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Models & Testing</h1>
          <p className="text-muted-foreground">
            Manage trained models and test entity extraction
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => revalidator.revalidate()} disabled={isLoading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button onClick={handleSync} disabled={isLoading}>
            <Download className="mr-2 h-4 w-4" />
            Sync from Disk
          </Button>
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="rounded-lg bg-destructive/10 p-4 text-destructive flex items-center gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {success && (
        <div className="rounded-lg bg-green-500/10 p-4 text-green-600 flex items-center gap-2">
          <Check className="h-4 w-4 flex-shrink-0" />
          {success}
        </div>
      )}

      {/* Recommendation Banner */}
      {recommended_id && recommended_reason && !isModelActive(trainings.find((t: TrainingRun) => t.id === recommended_id)) && (
        <Card className="border-yellow-500/50 bg-yellow-500/5">
          <CardContent className="flex items-center gap-4 py-4">
            <Star className="h-8 w-8 text-yellow-500 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium">Recommended Model Available</p>
              <p className="text-sm text-muted-foreground">{recommended_reason}</p>
            </div>
            <Button
              onClick={() => {
                const training = trainings.find((t: TrainingRun) => t.id === recommended_id)
                if (training) handleSwitchModel(training)
              }}
              disabled={isLoading}
            >
              <Zap className="mr-2 h-4 w-4" />
              Activate
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Model Selection */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Box className="h-5 w-5 text-primary" />
              <CardTitle>Select Model</CardTitle>
            </div>
            {switchingModel && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted px-3 py-1 rounded-full">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Loading model...
              </div>
            )}
          </div>
          <CardDescription>
            Click on a model to activate it for entity extraction
          </CardDescription>
        </CardHeader>
        <CardContent>
          {trainings.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Clock className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p className="font-medium">No trained models found</p>
              <p className="text-sm mb-4">Train a model or sync from disk to get started</p>
              <Button onClick={handleSync} disabled={isLoading}>
                <Download className="mr-2 h-4 w-4" />
                Sync from Disk
              </Button>
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {trainings.map((model: TrainingRun) => {
                const isActive = isModelActive(model)
                const isBest = bestModel?.id === model.id
                const isRecommended = model.id === recommended_id
                return (
                  <div
                    key={model.id}
                    className={`relative rounded-lg border p-4 cursor-pointer transition-all hover:shadow-md ${
                      isActive
                        ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                        : 'hover:border-primary/50'
                    } ${switchingModel ? 'opacity-50 pointer-events-none' : ''}`}
                    onClick={() => {
                      if (!isActive && model.checkpoint_path) {
                        handleSwitchModel(model)
                      }
                    }}
                  >
                    {/* Badges */}
                    <div className="absolute -top-2 right-2 flex gap-1">
                      {isBest && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 dark:bg-yellow-900/30 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:text-yellow-400">
                          <Star className="h-3 w-3 fill-current" />
                          Best
                        </span>
                      )}
                      {isActive && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-0.5 text-xs font-medium text-green-700 dark:text-green-400">
                          <Check className="h-3 w-3" />
                          Active
                        </span>
                      )}
                    </div>

                    {/* Model Info */}
                    <div className="space-y-3 mt-2">
                      <div>
                        <p className="font-mono text-sm font-medium truncate" title={model.session_id}>
                          {model.session_id.replace('bert-base-cased_', '')}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {model.model_name}
                        </p>
                      </div>

                      {/* Metrics */}
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="rounded bg-muted/50 p-2">
                          <p className="text-muted-foreground">Val Loss</p>
                          <p className="font-mono font-semibold text-sm">
                            {model.best_val_loss?.toFixed(4) || '-'}
                          </p>
                        </div>
                        <div className="rounded bg-muted/50 p-2">
                          <p className="text-muted-foreground">Epochs</p>
                          <p className="font-mono font-semibold text-sm">
                            {model.epochs_completed || 0}/{model.epochs_total || 0}
                          </p>
                        </div>
                      </div>

                      {/* Status */}
                      <div className="flex items-center justify-between text-xs">
                        <span className={`capitalize ${
                          model.status === 'completed' ? 'text-green-600' :
                          model.status === 'stopped' ? 'text-yellow-600' : 'text-muted-foreground'
                        }`}>
                          {model.status}
                        </span>
                        {model.best_epoch && (
                          <span className="text-muted-foreground">
                            Best @ epoch {model.best_epoch}
                          </span>
                        )}
                      </div>

                      {!model.checkpoint_path && (
                        <p className="text-xs text-destructive">No checkpoint available</p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Testing Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-primary" />
            <CardTitle>Test Extraction</CardTitle>
          </div>
          <CardDescription>
            Enter text to extract entities using the active model
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            className="min-h-[150px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            placeholder="Enter text about a violent event..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Example texts:</Label>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_TEXTS.map((example, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => setText(example)}
                >
                  Example {idx + 1}
                </Button>
              ))}
            </div>
          </div>

          <Button onClick={handleExtract} disabled={extracting || !text.trim()} className="w-full">
            {extracting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Extracting...
              </>
            ) : (
              <>
                <FlaskConical className="mr-2 h-4 w-4" />
                Extract Entities
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Extraction Results</CardTitle>
              <div className="flex items-center gap-2">
                {saveSuccess && savedEventId ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/events`)}
                  >
                    <Check className="mr-2 h-4 w-4 text-green-500" />
                    Saved - View Events
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSaveDialogOpen(true)}
                  >
                    <Save className="mr-2 h-4 w-4" />
                    Save as Event
                  </Button>
                )}
              </div>
            </div>
            <CardDescription>
              {result.entities.length} entities found in {result.processing_time_ms.toFixed(0)}ms using <span className="font-mono text-foreground">{result.model_version}</span>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Highlighted Text */}
            <div className="rounded-lg bg-muted p-4 text-sm leading-loose">
              {renderHighlightedText()}
            </div>

            {/* 5W1H Structure - Grouped by specific entity types */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              {[
                {
                  key: 'who',
                  label: 'WHO',
                  types: ['PERPETRATOR', 'VICTIM', 'TARGET', 'ORGANIZATION', 'GOVERNMENT']
                },
                {
                  key: 'what',
                  label: 'WHAT',
                  types: ['EVENT_TYPE', 'ACTION', 'WEAPON', 'VIOLENCE_TYPE']
                },
                {
                  key: 'when',
                  label: 'WHEN',
                  types: ['DATE', 'TIME', 'DURATION', 'FREQUENCY']
                },
                {
                  key: 'where',
                  label: 'WHERE',
                  types: ['COUNTRY', 'REGION', 'CITY', 'DISTRICT', 'FACILITY', 'GEOGRAPHIC', 'COORDINATES']
                },
                {
                  key: 'how',
                  label: 'HOW',
                  types: ['CASUALTIES', 'INJURED', 'DISPLACEMENT', 'DAMAGE', 'MOTIVE', 'TRIGGER']
                },
              ].map(({ key, label, types }) => {
                // Group entities by their specific type within this category
                const groupedEntities: Record<string, string[]> = {}
                types.forEach(type => {
                  const entitiesOfType = result.entities
                    .filter(e => e.label === type)
                    .map(e => e.text)
                  if (entitiesOfType.length > 0) {
                    groupedEntities[type] = entitiesOfType
                  }
                })

                const hasEntities = Object.keys(groupedEntities).length > 0

                return (
                  <div key={key} className="rounded-lg border p-3">
                    <p className="text-xs font-semibold text-muted-foreground mb-2">{label}</p>
                    {hasEntities ? (
                      <div className="space-y-2">
                        {Object.entries(groupedEntities).map(([type, entities]) => (
                          <div key={type}>
                            <p className="text-[10px] font-medium text-primary/70 uppercase tracking-wide">{type}</p>
                            <ul className="space-y-0.5">
                              {entities.map((entity, idx) => (
                                <li key={idx} className="text-sm pl-2 border-l-2 border-primary/20">{entity}</li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">-</p>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Confidence Scores */}
            {Object.keys(result.confidence_scores).length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground mb-2">Confidence by Category</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(result.confidence_scores).map(([category, score]) => (
                    <span
                      key={category}
                      className="inline-flex items-center rounded-full bg-muted px-3 py-1 text-xs"
                    >
                      <span className="font-medium uppercase">{category}</span>
                      <span className="ml-2 text-muted-foreground">{(score * 100).toFixed(0)}%</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Save Event Dialog */}
      <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Pencil className="h-5 w-5" />
              Save as Event
            </DialogTitle>
            <DialogDescription>
              Review and edit the extracted information before saving
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="actor">Perpetrator (WHO)</Label>
                <Input
                  id="actor"
                  value={formData.actor_normalized}
                  onChange={(e) => setFormData(prev => ({ ...prev, actor_normalized: e.target.value }))}
                  placeholder="e.g., Al Shabaab"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="victim">Victim (WHO)</Label>
                <Input
                  id="victim"
                  value={formData.victim_normalized}
                  onChange={(e) => setFormData(prev => ({ ...prev, victim_normalized: e.target.value }))}
                  placeholder="e.g., civilians"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="country">Country (WHERE)</Label>
                <Input
                  id="country"
                  value={formData.location_country}
                  onChange={(e) => setFormData(prev => ({ ...prev, location_country: e.target.value }))}
                  placeholder="e.g., Somalia"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="city">City (WHERE)</Label>
                <Input
                  id="city"
                  value={formData.location_city}
                  onChange={(e) => setFormData(prev => ({ ...prev, location_city: e.target.value }))}
                  placeholder="e.g., Mogadishu"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date (WHEN)</Label>
                <Input
                  id="date"
                  value={formData.date_normalized}
                  onChange={(e) => setFormData(prev => ({ ...prev, date_normalized: e.target.value }))}
                  placeholder="e.g., 2024-01-15"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="deaths">Deaths</Label>
                <Input
                  id="deaths"
                  type="number"
                  value={formData.deaths}
                  onChange={(e) => setFormData(prev => ({ ...prev, deaths: parseInt(e.target.value) || 0 }))}
                  min={0}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="injuries">Injuries</Label>
                <Input
                  id="injuries"
                  type="number"
                  value={formData.injuries}
                  onChange={(e) => setFormData(prev => ({ ...prev, injuries: parseInt(e.target.value) || 0 }))}
                  min={0}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="taxonomy">Event Type (WHAT)</Label>
              <Input
                id="taxonomy"
                value={formData.taxonomy_l1}
                onChange={(e) => setFormData(prev => ({ ...prev, taxonomy_l1: e.target.value }))}
                placeholder="e.g., Armed clash"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setSaveDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveEvent} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Event
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
