// Auth types
export interface User {
  id: string
  username: string
  is_first_user: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface RegisterRequest {
  username: string
  password: string
}

// Chat record types
export interface ChatRecord {
  id: string
  user_id: string
  contact_name: string
  file_name: string | null
  message_count: number
  parse_status: string
  created_at: string
  updated_at: string
}

export interface ChatRecordList {
  records: ChatRecord[]
  total: number
}

export interface MessageDetail {
  id: string
  sender: string
  content: string | null
  message_type: string
  timestamp: string
  is_from_me: boolean
}

export interface ChatRecordDetail extends ChatRecord {
  messages: MessageDetail[]
}

// Analysis types
export interface StatsResponse {
  total_messages: number
  my_messages: number
  their_messages: number
  my_percentage: number
  their_percentage: number
  message_types: Record<string, number>
  avg_message_length: number
  max_message_length: number
  min_message_length: number
  time_distribution: Record<string, number>
  late_night_count: number
  weekend_count: number
  time_span_days: number
  // Enhanced fields
  late_night_percentage: number
  weekend_percentage: number
  my_median_response_minutes: number
  their_median_response_minutes: number
  hourly_heatmap: { hour: number; count: number }[]
  conversations: {
    total: number
    avg_per_conversation: number
    max_length: number
    length_distribution: { label: string; count: number }[]
  }
  my_top_words: string[]
  their_top_words: string[]
  my_emoji_top: [string, number][]
  their_emoji_top: [string, number][]
  my_by_day: { day: string; count: number }[]
  their_by_day: { day: string; count: number }[]
}

export interface PersonalityResponse {
  my_extroversion_score: number
  their_extroversion_score: number
  my_rational_score: number
  their_rational_score: number
  my_positive_score: number
  their_positive_score: number
  my_direct_score: number
  their_direct_score: number
  my_openness?: number
  their_openness?: number
  my_conscientiousness?: number
  their_conscientiousness?: number
  my_extraversion?: number
  their_extraversion?: number
  my_agreeableness?: number
  their_agreeableness?: number
  my_neuroticism?: number
  their_neuroticism?: number
  my_interaction_style: string
  their_interaction_style: string
  summary: string
  details: {
    my_style_traits?: string[]
    their_style_traits?: string[]
  }
}

export interface RelationResponse {
  intimacy_score: number
  my_initiative_index: number
  their_initiative_index: number
  trend: {
    direction: string
    description: string
    change_percentage: number
    weekly_counts: number[]
  }
  role_summary: string
  response_time_minutes: number
  details: {
    my_peak_hour: number
    their_peak_hour: number
    active_time_match: string
    late_night_ratio: number
    my_avg_message_length: number
    their_avg_message_length: number
  }
}

// Reply types
export interface ReplySuggestion {
  content: string
  style: string
  reason: string
}

export interface SmartContextRequest {
  draft: string
  context: string
  style: string
}

export interface SmartContextResponse {
  context_analysis: string
  suggestions: ReplySuggestion[]
  improved_reply: string
}

export interface QuickQuestionRequest {
  scenario: string
  style: string
}

export interface QuickQuestionResponse {
  scenario_analysis: string
  suggestions: ReplySuggestion[]
}

export interface ImproveDraftRequest {
  draft: string
  target_style: string
}

export interface ImproveDraftResponse {
  original: string
  improved: string
  suggestions: string[]
}