export type ServiceStatus = 'ok' | 'degraded' | 'down' | 'unknown'

export type HealthResponse = {
  api_status: string
  neo4j_status: string
  ollama_status: string
  environment: string
  document_count: number
}
