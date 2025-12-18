// Event types
export interface Event {
  event_id: string
  event_description: string
  actor_normalized: string | null
  victim_normalized: string | null
  location_country: string
  location_city: string | null
  date_normalized: string | null
  taxonomy_l1: string
  taxonomy_l2?: string | null
  taxonomy_l3?: string | null
  severity: string | null
  deaths: number
  injuries: number
  flagged_for_review?: boolean
  created_at: string
}

export interface EventDetail extends Event {
  actor_type?: string | null
  actor_confidence?: number | null
  victim_type?: string | null
  victim_confidence?: number | null
  location_confidence?: number | null
  date_original?: string | null
  date_confidence?: number | null
  weapon_category?: string | null
  attack_method?: string | null
  severity_score?: number | null
  annotator_name?: string | null
  extraction_method?: string | null
  extraction_date?: string | null
  notes?: string | null
  review_notes?: string | null
  updated_at?: string | null
}

// Actor types
export interface Actor {
  actor_id: number
  actor_name: string
  actor_type: string | null
  actor_category: string | null
  country: string | null
  region: string | null
  aliases: string[] | null
  description: string | null
  event_count: number
  total_deaths: number
  total_injuries: number
}

// Location types
export interface Location {
  location_id: number
  country: string
  city: string | null
  region: string | null
  district: string | null
  location_type: string | null
  event_count: number
  total_deaths: number
}

// Taxonomy types
export interface Taxonomy {
  taxonomy_id: number
  level_1: string
  level_2: string | null
  level_3: string | null
  description: string | null
  event_count: number
}

// Checkpoint types
export interface Checkpoint {
  path: string
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
  num_labels: number
  available_epochs: number[]
  has_best: boolean
  size_mb: number
  modified: string
}

// Extraction types
export interface Entity {
  text: string
  label: string
  start: number
  end: number
  confidence: number
}

export interface StructuredEvent {
  who: string[]
  what: string[]
  when: string[]
  where: string[]
  how: string[]
}

export interface ExtractionResult {
  request_id: string
  text: string
  entities: Entity[]
  structured_event: StructuredEvent
  confidence_scores: Record<string, number>
  processing_time_ms: number
  model_version: string
  timestamp: string
}

// Stats types
export interface Stats {
  total_events: number
  total_actors: number
  total_locations: number
  total_taxonomies: number
  total_deaths: number
  total_injuries: number
  countries_covered: number
  date_range: {
    earliest: string | null
    latest: string | null
  }
  top_actors: Array<{ name: string; events: number; deaths: number }>
  top_locations: Array<{ country: string; events: number; deaths: number }>
  events_by_taxonomy: Array<{ taxonomy: string; count: number }>
  events_by_severity: Record<string, number>
}

// Training types
export interface TrainingConfig {
  model_name: string
  epochs: number
  batch_size: number
  learning_rate: number
  warmup_steps: number
  weight_decay: number
  max_length: number
  train_file: string
  val_file: string
}

export interface TrainingDefaults {
  model_options: string[]
  training_defaults: {
    epochs: number
    batch_size: number
    learning_rate: number
    warmup_steps: number
    weight_decay: number
    max_length: number
  }
  presets: Array<{
    name: string
    epochs: number
    batch_size: number
    learning_rate: number
  }>
}
