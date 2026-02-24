/**
 * Documents Store
 *
 * Manages document upload, listing, and deletion state.
 */

import { defineStore } from 'pinia'
import type { DocumentListResponse, UploadResponse } from '~/composables/useApi'

export interface Document {
  id: string
  content: string
  metadata: Record<string, any>
}

export const useDocumentsStore = defineStore('documents', () => {
  // State
  const documents = ref<Document[]>([])
  const isLoading = ref(false)
  const isUploading = ref(false)
  const error = ref<string | null>(null)
  const uploadProgress = ref(0)
  const totalCount = ref(0)

  // Actions
  async function loadDocuments(options?: {
    filters?: Record<string, any>
    limit?: number
  }) {
    isLoading.value = true
    error.value = null

    try {
      const api = useRagApi()
      const response = await api.listDocuments(options)

      documents.value = response.documents
      totalCount.value = response.total
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load documents'
      throw err
    }
    finally {
      isLoading.value = false
    }
  }

  async function uploadFile(
    file: File,
    metadata?: Record<string, any>,
  ) {
    isUploading.value = true
    uploadProgress.value = 0
    error.value = null

    try {
      const api = useRagApi()
      const response = await api.uploadDocument(file, metadata)

      // Refresh the document list
      await loadDocuments()

      return response
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to upload document'
      throw err
    }
    finally {
      isUploading.value = false
      uploadProgress.value = 0
    }
  }

  async function indexText(
    text: string,
    documentId?: string,
    metadata?: Record<string, any>,
  ) {
    isUploading.value = true
    error.value = null

    try {
      const api = useRagApi()
      const response = await api.indexText(text, documentId, metadata)

      // Refresh the document list
      await loadDocuments()

      return response
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to index text'
      throw err
    }
    finally {
      isUploading.value = false
    }
  }

  async function deleteDocument(documentId: string) {
    error.value = null

    try {
      const api = useRagApi()
      await api.deleteDocument(documentId)

      // Remove from local state
      documents.value = documents.value.filter(doc => doc.id !== documentId)
      totalCount.value = Math.max(0, totalCount.value - 1)
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete document'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  // Getters
  const hasDocuments = computed(() => documents.value.length > 0)
  const isEmpty = computed(() => documents.value.length === 0)

  return {
    // State
    documents,
    isLoading,
    isUploading,
    error,
    uploadProgress,
    totalCount,

    // Actions
    loadDocuments,
    uploadFile,
    indexText,
    deleteDocument,
    clearError,

    // Getters
    hasDocuments,
    isEmpty,
  }
})
