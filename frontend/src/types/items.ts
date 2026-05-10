/* TypeScript 接口定义 — 与后端 FeedItemResponse 和 API 响应结构精确对应 */

export interface FeedItem {
  /** processed_item.id */
  id: number;
  /** raw_item.title */
  title: string;
  /** raw_item.source_url */
  source_url: string;
  /** source_config.name */
  source_name: string;
  /** raw_item.author */
  author: string | null;
  /** raw_item.published_at — ISO 8601 datetime string */
  published_at: string;
  /** processed_item.summary */
  summary: string | null;
  /** processed_item.tags (JSONB array) */
  tags: string[] | null;
  /** processed_item.category — 模型/产品/行业/研究/工程 */
  category: string | null;
  /** processed_item.recommended_score */
  recommended_score: number | null;
  /** processed_item.recommendation_reason */
  recommendation_reason: string | null;
  /** raw_item.metadata.image_url */
  image_url: string | null;
  /** processed_item.created_at — ISO 8601 datetime string */
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type Category = string;
