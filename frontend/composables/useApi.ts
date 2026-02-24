/**
 * API Composable
 *
 * Provides type-safe API communication with the Django backend.
 */

export interface DocumentSource {
  id: string
  content: string
  metadata: Record<string, any>
  score?: number
}

export interface QueryResponse {
  answer: string
  sources: DocumentSource[]
  query: string
  retrieval_method?: string
  meta?: Record<string, any>
}

export interface DocumentListResponse {
  documents: Array<{
    id: string
    content: string
    metadata: Record<string, any>
  }>
  total: number
}

export interface UploadResponse {
  success: boolean
  document_id: string
  chunks_added: number
  metadata: Record<string, any>
  error?: string
}

export interface StatsResponse {
  total_documents: number
}

export interface ApiResponse<T> {
  success?: boolean
  data?: T
  error?: string
  details?: Record<string, any>
}

const config = useRuntimeConfig()

/**
 * Create an API client with proper error handling
 */
export function useApi() {
  const apiBase = config.public.apiBase as string

  /**
   * Make a GET request
   */
  async function get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = new URL(`${apiBase}${endpoint}`, window.location.origin)

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(error.error || error.message || 'Request failed')
    }

    return response.json()
  }

  /**
   * Make a POST request with JSON body
   */
  async function post<T>(endpoint: string, data: Record<string, any>): Promise<T> {
    const response = await fetch(`${apiBase}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(error.error || error.message || 'Request failed')
    }

    return response.json()
  }

  /**
   * Make a POST request with multipart form data (for file uploads)
   */
  async function upload<T>(endpoint: string, formData: FormData): Promise<T> {
    const response = await fetch(`${apiBase}${endpoint}`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(error.error || error.message || 'Upload failed')
    }

    return response.json()
  }

  /**
   * Make a DELETE request
   */
  async function del<T>(endpoint: string, data?: Record<string, any>): Promise<T> {
    const response = await fetch(`${apiBase}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(error.error || error.message || 'Request failed')
    }

    return response.json()
  }

  return {
    get,
    post,
    upload,
    delete: del,
  }
}

/**
 * RAG API operations
 */
export function useRagApi() {
  const api = useApi()

  return {
    /**
     * Query the RAG system
     */
    async query(
      query: string,
      options?: {
        topK?: number
        filters?: Record<string, any>
        retrievalMethod?: 'semantic' | 'hybrid'
      },
    ): Promise<QueryResponse> {
      return api.post<QueryResponse>('/query', {
        query,
        top_k: options?.topK ?? 5,
        filters: options?.filters,
        retrieval_method: options?.retrievalMethod ?? 'semantic',
      })
    },

    /**
     * Upload a document
     */
    async uploadDocument(
      file: File,
      metadata?: Record<string, any>,
    ): Promise<UploadResponse> {
      const formData = new FormData()
      formData.append('file', file)
      if (metadata) {
        formData.append('metadata', JSON.stringify(metadata))
      }

      return api.upload<UploadResponse>('/documents/upload', formData)
    },

    /**
     * Index raw text
     */
    async indexText(
      text: string,
      documentId?: string,
      metadata?: Record<string, any>,
    ): Promise<UploadResponse> {
      return api.post<UploadResponse>('/documents/upload', {
        text,
        document_id: documentId,
        metadata,
      })
    },

    /**
     * List documents
     */
    async listDocuments(options?: {
      filters?: Record<string, any>
      limit?: number
    }): Promise<DocumentListResponse> {
      return api.get<DocumentListResponse>('/documents', {
        filters: options?.filters ? JSON.stringify(options.filters) : undefined,
        limit: options?.limit ?? 100,
      })
    },

    /**
     * Delete a document
     */
    async deleteDocument(documentId: string): Promise<{ success: boolean; chunks_deleted: number }> {
      return api.delete('/documents/delete', { document_id: documentId })
    },

    /**
     * Get statistics
     */
    async getStats(): Promise<StatsResponse> {
      return api.get<StatsResponse>('/stats')
    },

    /**
     * Health check
     */
    async healthCheck(): Promise<{ status: string; service: string; version: string }> {
      return api.get('/health')
    },
  }
}
