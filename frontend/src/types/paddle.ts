// TypeScript types mirroring backend Pydantic schemas
// Source: backend/app/schemas.py and backend/app/api/chat.py, admin.py

export interface PaddleSpecs {
  swingweight?: number
  twistweight?: number
  weight_oz?: number
  grip_size?: string
  core_thickness_mm?: number
  face_material?: string
}

export interface Paddle {
  id: number
  name: string
  brand: string
  sku?: string
  image_url?: string
  specs?: PaddleSpecs
  price_min_brl?: number
  created_at: string
  // SEO / product detail fields (Phase 05-02)
  model?: string
  model_slug?: string
  description?: string
  price_brl?: number
  skill_level?: string
  rating?: number
  review_count?: number
  in_stock?: boolean
  retailer_count?: number
  latest_scraped_at?: string
}

export interface PaddleListResponse {
  items: Paddle[]
  total: number
  limit: number
  offset: number
}

export interface PriceSnapshot {
  retailer_name: string
  price_brl: number
  currency: string
  in_stock: boolean
  scraped_at: string
}

export interface LatestPriceResponse {
  paddle_id: number
  paddle_name: string
  latest_prices: PriceSnapshot[]
}

export interface ChatRequest {
  message: string
  skill_level: 'beginner' | 'intermediate' | 'advanced'
  budget_brl: number
  style?: string
}

export interface ChatRecommendation {
  paddle_id: number
  name: string
  brand: string
  price_min_brl: number
  affiliate_url: string
  similarity_score: number
}

export interface ReviewQueueItem {
  id: number
  type: 'duplicate' | 'spec_unmatched' | 'price_anomaly'
  paddle_id: number
  related_paddle_id?: number
  data: Record<string, unknown>
  status: 'pending' | 'resolved' | 'dismissed'
  created_at?: string
}

export interface UserProfile {
  level: string
  style: string
  budget_max: number
  identity?: string
  pain_points?: string[]
  frequency?: string
}

export type QuizStep = 'welcome' | 'identity' | 'style' | 'pain-points' | 'frequency' | 'budget' | 'analyzing'

export const QUIZ_STEPS: QuizStep[] = [
  'welcome', 'identity', 'style', 'pain-points', 'frequency', 'budget', 'analyzing'
]

export const QUIZ_STEP_INFO: Record<QuizStep, { title: string; subtitle: string }> = {
  'welcome': { title: '', subtitle: '' },
  'identity': { title: 'Vamos la!', subtitle: 'Como voce se descreve como jogador?' },
  'style': { title: 'Ja sei quem voce e...', subtitle: 'O que voce mais valoriza no jogo?' },
  'pain-points': { title: 'Quase la!', subtitle: 'O que te frustra na sua raquete atual?' },
  'frequency': { title: 'So mais uma...', subtitle: 'Com que frequencia voce joga?' },
  'budget': { title: 'Ultima pergunta!', subtitle: 'Quanto voce quer investir?' },
  'analyzing': { title: 'Analisando seu perfil...', subtitle: '' },
}

export const IDENTITY_OPTIONS = [
  { value: 'beginner', label: 'Estou comecando', description: 'Jogo por diversao e saude', icon: '🎯' },
  { value: 'regular', label: 'Jogo regularmente', description: 'Participo de jogos competitivos', icon: '⚡' },
  { value: 'serious', label: 'Levo o jogo a serio', description: 'Treino e participo de torneios', icon: '🏆' },
] as const

export const PAIN_POINT_OPTIONS = [
  'Nao tem potencia suficiente',
  'Erro muitos tiros na rede',
  'Braco cansa depois de jogar',
  'Nao consigo gerar spin',
  'E muito pesada',
  'Nao sei, nunca prestei atencao',
] as const

export const FREQUENCY_OPTIONS = [
  { value: 'weekly', label: 'Uma vez por semana ou menos' },
  { value: '2-3x', label: '2-3 vezes por semana' },
  { value: '4plus', label: '4+ vezes por semana' },
] as const

export const BUDGET_MIN = 200
export const BUDGET_MAX = 2000
export const BUDGET_SMART_ZONE = { min: 400, max: 800 }
