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
}
