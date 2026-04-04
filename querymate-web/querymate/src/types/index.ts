export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sql?: string | null
  rowCount?: number | null
  status?: string
  attempts?: number | null
  timestamp: Date
}

export interface ConnectResponse {
  status: string
  session_id: string | null
  db_type: string | null
  table_count: number | null
  tables: string[] | null
  error: string | null
}

export interface QueryResponse {
  status: string
  answer: string | null
  sql: string | null
  rows: Record<string, unknown>[] | null
  row_count: number | null
  truncated: boolean | null
  attempts: number | null
  error: string | null
}

export interface ConnectionState {
  connected: boolean
  sessionId: string | null
  dbType: string | null
  tables: string[]
  tableCount: number
}