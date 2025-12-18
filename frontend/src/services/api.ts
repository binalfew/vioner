const API_BASE = '/api'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Training Run type
export interface TrainingRun {
  id: number
  session_id: string
  model_name: string
  status: string
  epochs_total: number | null
  epochs_completed: number | null
  best_epoch: number | null
  best_val_loss: number | null
  best_val_accuracy: number | null
  checkpoint_path: string | null
  is_active: boolean
  started_at: string | null
  completed_at: string | null
  notes: string | null
}

// Training Data Upload types
export interface ValidationError {
  type: string
  column?: string
  row?: number
  message: string
}

export interface SampleEntity {
  text: string
  type: string
  start: number
  end: number
}

export interface SampleEvent {
  event_id: string
  text: string
  entities: SampleEntity[]
}

export interface ValidationResponse {
  valid: boolean
  filename: string
  file_size_kb: number
  total_rows?: number
  columns_found: string[]
  columns_missing: string[]
  columns_extra: string[]
  sample_events: SampleEvent[]
  entity_statistics: Record<string, number>
  validation_token?: string
  errors: ValidationError[]
}

export interface ProcessResponse {
  success: boolean
  message: string
  train_file?: string
  val_file?: string
  statistics?: {
    total_events: number
    train_events: number
    val_events: number
    entity_type_counts: Record<string, number>
    processing_time_ms: number
  }
}

export interface DataStatusResponse {
  has_data: boolean
  train_file: {
    path: string
    exists: boolean
    events: number
    size_mb: number
    modified: string
  } | null
  val_file: {
    path: string
    exists: boolean
    events: number
    size_mb: number
    modified: string
  } | null
  statistics: Record<string, unknown> | null
}

export interface ProcessingProgressResponse {
  is_processing: boolean
  current_row: number
  total_rows: number
  percent_complete: number
  current_event_id: string | null
  phase: 'idle' | 'processing' | 'saving' | 'complete' | 'error'
  message: string
}

// Training API
export const trainingApi = {
  getStatus: () => fetchJson<{ status: string; progress: unknown }>('/training/status'),

  start: (config: {
    model_name: string
    epochs: number
    batch_size: number
    learning_rate: number
    warmup_steps?: number
    weight_decay?: number
    max_length?: number
    train_file?: string  // Optional - backend uses defaults
    val_file?: string    // Optional - backend uses defaults
    run_epochs?: number  // Optional - run only N epochs this session
  }) => fetchJson('/training/start', {
    method: 'POST',
    body: JSON.stringify(config),
  }),

  resume: (checkpointPath: string, options?: { extendEpochs?: number; runEpochs?: number }) =>
    fetchJson('/training/resume', {
      method: 'POST',
      body: JSON.stringify({
        checkpoint_path: checkpointPath,
        extend_epochs: options?.extendEpochs || 0,
        run_epochs: options?.runEpochs || null,
      }),
    }),

  stop: () => fetchJson('/training/stop', { method: 'POST' }),

  getLogs: (limit = 100) => fetchJson<string[]>(`/training/logs?limit=${limit}`),

  getDefaults: () => fetchJson<{
    model_options: string[]
    training_defaults: Record<string, number>
    presets: Array<{ name: string; epochs: number; batch_size: number; learning_rate: number }>
  }>('/training/defaults'),

  getModels: () => fetchJson<{ models: string[] }>('/training/models'),

  // Model Management
  syncModels: () => fetchJson<{ synced: number; updated: number; message: string }>(
    '/training/sync-models',
    { method: 'POST' }
  ),

  listRuns: () => fetchJson<{
    trainings: TrainingRun[]
    recommended_id: number | null
    recommended_reason: string | null
    active_id: number | null
  }>('/training/runs'),

  activateModel: (trainingId: number) => fetchJson<{ success: boolean; message: string; status: string }>(
    '/training/activate',
    { method: 'POST', body: JSON.stringify({ training_id: trainingId }) }
  ),

  getActiveModel: () => fetchJson<{
    active_training: TrainingRun | null
    symlink_target?: string | null
    message: string
  }>('/training/active'),

  // Training Data Upload
  validateData: async (file: File): Promise<ValidationResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/training/data/validate`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Validation failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  },

  processData: (validationToken: string, trainSplit = 0.8): Promise<ProcessResponse> =>
    fetchJson('/training/data/process', {
      method: 'POST',
      body: JSON.stringify({ validation_token: validationToken, train_split: trainSplit }),
    }),

  getDataStatus: (): Promise<DataStatusResponse> =>
    fetchJson('/training/data/status'),

  getProcessingProgress: (): Promise<ProcessingProgressResponse> =>
    fetchJson('/training/data/progress'),
}

// Checkpoints API
export const checkpointsApi = {
  list: () => fetchJson<{ checkpoints: unknown[]; total: number }>('/training/checkpoints/'),

  get: (name: string) => fetchJson(`/training/checkpoints/${name}`),

  getBest: () => fetchJson('/training/checkpoints/best'),

  delete: (name: string) => fetchJson(`/training/checkpoints/${name}`, { method: 'DELETE' }),

  getEpochs: (name: string) => fetchJson<{
    checkpoint: string
    epochs: Array<{ epoch: number; path: string; name: string }>
    has_best: boolean
    best_path: string | null
  }>(`/training/checkpoints/${name}/epochs`),

  cleanupIncomplete: () => fetchJson('/training/checkpoints/cleanup/incomplete', { method: 'POST' }),
}

// Evaluation types
export interface EntityMetrics {
  entity_type: string
  precision: number
  recall: number
  f1: number
  support: number
  predicted: number
  correct: number
}

export interface ConfusionEntry {
  true_label: string
  predicted_label: string
  count: number
  examples: Array<{ text: string; entity: string }>
}

export interface ErrorExample {
  text: string
  true_entities: Array<{ text: string; type: string }>
  predicted_entities: Array<{ text: string; type: string }>
  error_type: 'false_positive' | 'false_negative' | 'wrong_type'
  entity_type: string
}

export interface EvaluationResult {
  checkpoint_name: string
  epoch: number | null
  total_samples: number
  overall_precision: number
  overall_recall: number
  overall_f1: number
  entity_metrics: EntityMetrics[]
  confusion_matrix: ConfusionEntry[]
  error_examples: ErrorExample[]
  entity_distribution: Record<string, number>
}

export interface EvaluationStatus {
  checkpoint_name: string
  status: 'running' | 'complete' | 'not_started' | 'error'
  cached?: boolean
  error?: string
}

// Evaluation API
export const evaluationApi = {
  run: (checkpointName: string, epoch?: number, maxSamples?: number): Promise<EvaluationStatus> =>
    fetchJson('/training/evaluation/run', {
      method: 'POST',
      body: JSON.stringify({
        checkpoint_name: checkpointName,
        epoch: epoch ?? null,
        max_samples: maxSamples ?? null,
      }),
    }),

  getStatus: (checkpointName: string, epoch?: number): Promise<EvaluationStatus> =>
    fetchJson(`/training/evaluation/status/${checkpointName}${epoch ? `?epoch=${epoch}` : ''}`),

  getResults: (checkpointName: string, epoch?: number): Promise<EvaluationResult> =>
    fetchJson(`/training/evaluation/results/${checkpointName}${epoch ? `?epoch=${epoch}` : ''}`),

  quickEval: (checkpointName: string, samples = 500, epoch?: number): Promise<EvaluationResult> =>
    fetchJson(`/training/evaluation/quick/${checkpointName}?samples=${samples}${epoch ? `&epoch=${epoch}` : ''}`),

  list: (): Promise<{ evaluations: Array<{ cache_key: string; checkpoint_name: string; epoch: number | null; overall_f1: number; total_samples: number }> }> =>
    fetchJson('/training/evaluation/list'),

  clearCache: (checkpointName: string, epoch?: number): Promise<{ message: string }> =>
    fetchJson(`/training/evaluation/cache/${checkpointName}${epoch ? `?epoch=${epoch}` : ''}`, { method: 'DELETE' }),
}

// Inference API
export const inferenceApi = {
  extract: (text: string, saveToDb = false) =>
    fetchJson<{
      request_id: string
      text: string
      entities: Array<{ text: string; label: string; start: number; end: number; confidence: number }>
      structured_event: { who: string[]; what: string[]; when: string[]; where: string[]; how: string[]; why: string[] }
      confidence_scores: Record<string, number>
      processing_time_ms: number
      model_version: string
      timestamp: string
    }>('/inference', {
      method: 'POST',
      body: JSON.stringify({ text, save_to_db: saveToDb }),
    }),

  extractBatch: (texts: string[]) =>
    fetchJson('/inference/batch', {
      method: 'POST',
      body: JSON.stringify({ texts }),
    }),

  getCategories: () => fetchJson<{
    categories: Record<string, string[]>
    description: Record<string, string>
  }>('/inference/categories'),

  getModelInfo: () => fetchJson<{
    model_path: string | null
    model_type: string | null
    num_labels: number
    device: string
    loaded: boolean
    loaded_at: string | null
    labels: string[]
  }>('/inference/model/info'),

  switchModel: (sessionId: string, subfolder: string = 'best') => fetchJson<{
    success: boolean
    message: string
    session_id: string
    subfolder: string
    device: string
    num_labels: number
  }>('/inference/model/switch', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, subfolder }),
  }),
}

// Events API
export const eventsApi = {
  list: (params?: {
    limit?: number
    offset?: number
    country?: string
    actor?: string
    severity?: string
    start_date?: string
    end_date?: string
    flagged?: boolean
  }) => {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, String(value))
      })
    }
    return fetchJson<{ events: unknown[]; total: number; limit: number; offset: number }>(
      `/events?${searchParams}`
    )
  },

  get: (id: string) => fetchJson(`/events/${id}`),

  create: (data: {
    event_description: string
    actor_normalized?: string
    victim_normalized?: string
    location_country: string
    location_city?: string
    date_normalized?: string
    taxonomy_l1?: string
    deaths?: number
    injuries?: number
  }) => fetchJson('/events', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: string, data: Partial<{
    event_description: string
    actor_normalized: string
    victim_normalized: string
    location_country: string
    location_city: string
    date_normalized: string
    taxonomy_l1: string
    taxonomy_l2: string
    taxonomy_l3: string
    weapon_category: string
    deaths: number
    injuries: number
  }>) => fetchJson(`/events/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: string) => fetchJson(`/events/${id}`, { method: 'DELETE' }),

  bulkDelete: (ids: string[]) => fetchJson('/events/bulk-delete', {
    method: 'POST',
    body: JSON.stringify(ids),
  }),

  flag: (id: string, notes?: string) =>
    fetchJson(`/events/${id}/flag?${notes ? `notes=${encodeURIComponent(notes)}` : ''}`, {
      method: 'POST',
    }),

  unflag: (id: string) => fetchJson(`/events/${id}/unflag`, { method: 'POST' }),
}

// Analytics API
export const analyticsApi = {
  getStats: () => fetchJson<{
    total_events: number
    total_actors: number
    total_locations: number
    total_taxonomies: number
    total_deaths: number
    total_injuries: number
    countries_covered: number
    date_range: { earliest: string | null; latest: string | null }
    top_actors: Array<{ name: string; events: number; deaths: number }>
    top_locations: Array<{ country: string; events: number; deaths: number }>
    events_by_taxonomy: Array<{ taxonomy: string; count: number }>
    events_by_severity: Record<string, number>
  }>('/analytics/stats'),

  getMonthlyTrends: (months = 12) =>
    fetchJson<Array<{ period: string; events: number; deaths: number; injuries: number }>>(
      `/analytics/trends/monthly?months=${months}`
    ),

  getByCountry: () => fetchJson<Array<{ country: string; events: number; deaths: number; injuries: number }>>(
    '/analytics/by-country'
  ),

  getByActor: (limit = 20) =>
    fetchJson<Array<{
      actor: string
      events: number
      deaths: number
      injuries: number
      countries_affected: number
    }>>(`/analytics/by-actor?limit=${limit}`),

  search: (params: {
    q?: string
    actor?: string
    country?: string
    city?: string
    taxonomy_l1?: string
    severity?: string
    min_deaths?: number
    start_date?: string
    end_date?: string
    sort_by?: string
    page?: number
    page_size?: number
  }) => {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, String(value))
    })
    return fetchJson<{
      total: number
      page: number
      page_size: number
      total_pages: number
      results: unknown[]
      filters_applied: Record<string, string | number>
    }>(`/analytics/search?${searchParams}`)
  },

  getTimeline: (period = 'month', months = 12) =>
    fetchJson<Array<{ period: string; events: number; deaths: number }>>(
      `/analytics/timeline?period=${period}&months=${months}`
    ),

  export: (format: 'csv' | 'json', filters?: Record<string, string | number>) => {
    const searchParams = new URLSearchParams({ format })
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        searchParams.append(key, String(value))
      })
    }
    return fetch(`${API_BASE}/analytics/export?${searchParams}`)
  },

  getReviewQueue: (limit = 50) => fetchJson(`/analytics/review-queue?limit=${limit}`),
}

// Knowledge Base - Actors API
export const actorsApi = {
  list: (params?: { limit?: number; offset?: number; search?: string; country?: string }) => {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, String(value))
      })
    }
    return fetchJson<unknown[]>(`/kb/actors?${searchParams}`)
  },

  get: (id: number) => fetchJson(`/kb/actors/${id}`),

  getEvents: (id: number, limit = 50) => fetchJson(`/kb/actors/${id}/events?limit=${limit}`),

  create: (data: {
    actor_name: string
    actor_type?: string
    actor_category?: string
    country?: string
    region?: string
    aliases?: string[]
    description?: string
  }) => fetchJson('/kb/actors', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: Partial<{
    actor_name: string
    actor_type: string
    actor_category: string
    country: string
    region: string
    aliases: string[]
    description: string
  }>) => fetchJson(`/kb/actors/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: number) => fetchJson(`/kb/actors/${id}`, { method: 'DELETE' }),

  merge: (sourceId: number, targetId: number) =>
    fetchJson(`/kb/actors/merge?source_id=${sourceId}&target_id=${targetId}`, { method: 'POST' }),
}

// Knowledge Base - Locations API
export const locationsApi = {
  list: (params?: { limit?: number; offset?: number; country?: string }) => {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, String(value))
      })
    }
    return fetchJson<unknown[]>(`/kb/locations?${searchParams}`)
  },

  get: (id: number) => fetchJson(`/kb/locations/${id}`),

  getEvents: (id: number, limit = 50) => fetchJson(`/kb/locations/${id}/events?limit=${limit}`),

  create: (data: {
    country: string
    city?: string
    region?: string
    district?: string
    location_type?: string
  }) => fetchJson('/kb/locations', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: Partial<{
    country: string
    city: string
    region: string
    district: string
    location_type: string
  }>) => fetchJson(`/kb/locations/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: number) => fetchJson(`/kb/locations/${id}`, { method: 'DELETE' }),

  merge: (sourceId: number, targetId: number) =>
    fetchJson(`/kb/locations/merge?source_id=${sourceId}&target_id=${targetId}`, { method: 'POST' }),

  getCountries: () => fetchJson<Array<{ country: string; event_count: number }>>('/kb/locations/countries/list'),
}

// Knowledge Base - Taxonomies API
export const taxonomiesApi = {
  list: () => fetchJson<unknown[]>('/kb/taxonomies'),

  getHierarchy: () => fetchJson('/kb/taxonomies/hierarchy'),

  getStats: () => fetchJson<{
    total_taxonomies: number
    total_events: number
    categories: Array<{
      level_1: string
      taxonomy_count: number
      event_count: number
      deaths: number
      injuries: number
    }>
  }>('/kb/taxonomies/stats/summary'),

  get: (id: number) => fetchJson(`/kb/taxonomies/${id}`),

  create: (data: {
    level_1: string
    level_2?: string
    level_3?: string
    description?: string
  }) => fetchJson('/kb/taxonomies', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: Partial<{
    level_1: string
    level_2: string
    level_3: string
    description: string
  }>) => fetchJson(`/kb/taxonomies/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: number, force = false) =>
    fetchJson(`/kb/taxonomies/${id}?force=${force}`, { method: 'DELETE' }),
}

// History API
export const historyApi = {
  list: (params?: { limit?: number; offset?: number; start_date?: string; end_date?: string }) => {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, String(value))
      })
    }
    return fetchJson<Array<{
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
    }>>(`/history?${searchParams}`)
  },

  get: (id: number) => fetchJson<{
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
    structured_event: { who: string[]; what: string[]; when: string[]; where: string[]; how: string[]; why: string[] }
    confidence_scores: Record<string, number>
  }>(`/history/${id}`, { cache: 'no-store' }),

  feedback: (id: number, data: { rating?: number; feedback?: string; corrections?: Record<string, unknown> }) =>
    fetchJson(`/history/${id}/feedback`, { method: 'POST', body: JSON.stringify(data) }),

  delete: (id: number) => fetchJson(`/history/${id}`, { method: 'DELETE' }),
}

// System API
export const systemApi = {
  getHealth: () => fetchJson<{
    status: string
    model_loaded: boolean
    model_info: unknown | null
    database_enabled: boolean
    database_connected: boolean | null
    timestamp: string
    version: string
  }>('/system/health'),

  getMetrics: () => fetchJson<{
    cpu_percent: number
    memory_percent: number
    memory_used_mb: number
    memory_available_mb: number
    disk_percent: number
    disk_used_gb: number
    disk_free_gb: number
  }>('/system/metrics'),

  getInfo: () => fetchJson('/system/info'),

  getGpuInfo: () => fetchJson<{
    available: boolean
    device: string
    name: string | null
    memory_total_mb: number | null
    memory_used_mb: number | null
    memory_free_mb: number | null
  }>('/system/gpu'),
}
