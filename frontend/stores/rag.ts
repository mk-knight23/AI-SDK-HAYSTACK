/**
 * RAG Store
 *
 * Manages RAG query state and history using Pinia.
 */

import { defineStore } from 'pinia'
import type { QueryResponse, DocumentSource } from '~/composables/useApi'

export interface QueryHistory {
  query: string
  answer: string
  sources: DocumentSource[]
  timestamp: Date
  retrievalMethod: string
}

export const useRagStore = defineStore('rag', () => {
  // State
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentQuery = ref('')
  const currentAnswer = ref<QueryResponse | null>(null)
  const queryHistory = ref<QueryHistory[]>([])

  // Actions
  async function askQuestion(
    query: string,
    options?: {
      topK?: number
      filters?: Record<string, any>
      retrievalMethod?: 'semantic' | 'hybrid'
    },
  ) {
    isLoading.value = true
    error.value = null
    currentQuery.value = query

    try {
      const api = useRagApi()
      const response = await api.query(query, options)

      currentAnswer.value = response

      // Add to history
      queryHistory.value.unshift({
        query,
        answer: response.answer,
        sources: response.sources,
        timestamp: new Date(),
        retrievalMethod: response.retrieval_method || 'semantic',
      })

      // Keep only last 50 queries
      if (queryHistory.value.length > 50) {
        queryHistory.value = queryHistory.value.slice(0, 50)
      }

      return response
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get answer'
      throw err
    }
    finally {
      isLoading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearHistory() {
    queryHistory.value = []
  }

  function removeFromHistory(index: number) {
    queryHistory.value.splice(index, 1)
  }

  // Getters
  const hasAnswer = computed(() => currentAnswer.value !== null)
  const historyCount = computed(() => queryHistory.value.length)

  return {
    // State
    isLoading,
    error,
    currentQuery,
    currentAnswer,
    queryHistory,

    // Actions
    askQuestion,
    clearError,
    clearHistory,
    removeFromHistory,

    // Getters
    hasAnswer,
    historyCount,
  }
})
