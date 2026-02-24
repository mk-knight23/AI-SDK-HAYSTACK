<template>
  <div class="haystack-app">
    <!-- Header -->
    <header class="header">
      <div class="container header-content">
        <div class="logo">
          <h1>Haystack RAG</h1>
          <span class="badge">Document Intelligence</span>
        </div>
        <div class="header-actions">
          <n-button text @click="showDocumentsModal = true">
            <template #icon>
              <n-icon><DocumentIcon /></n-icon>
            </template>
            Documents ({{ documentsCount }})
          </n-button>
          <n-button text @click="showStatsModal = true">
            <template #icon>
              <n-icon><StatsIcon /></n-icon>
            </template>
            Stats
          </n-button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main">
      <div class="container">
        <!-- Query Section -->
        <section class="query-section">
          <div class="card query-card">
            <h2>Ask a Question</h2>
            <p class="subtitle">Search your documents using AI-powered retrieval</p>

            <n-form ref="formRef" :model="queryForm" class="query-form">
              <n-form-item path="query">
                <n-input
                  v-model:value="queryForm.query"
                  type="textarea"
                  placeholder="Ask a question about your documents..."
                  :autosize="{ minRows: 2, maxRows: 6 }"
                  :disabled="ragStore.isLoading"
                  @keydown.enter.ctrl="handleSubmit"
                />
              </n-form-item>

              <div class="query-options">
                <n-form-item label="Documents to retrieve" path="topK">
                  <n-slider
                    v-model:value="queryForm.topK"
                    :min="1"
                    :max="20"
                    :marks="{ 1: '1', 5: '5', 10: '10', 20: '20' }"
                    :step="1"
                  />
                </n-form-item>

                <n-form-item label="Retrieval Method" path="retrievalMethod">
                  <n-radio-group v-model:value="queryForm.retrievalMethod">
                    <n-radio-button value="semantic">
                      Semantic Search
                    </n-radio-button>
                    <n-radio-button value="hybrid">
                      Hybrid Search
                    </n-radio-button>
                  </n-radio-group>
                </n-form-item>
              </div>

              <div class="query-actions">
                <n-button
                  type="primary"
                  size="large"
                  :disabled="!queryForm.query.trim()"
                  :loading="ragStore.isLoading"
                  @click="handleSubmit"
                >
                  <template #icon>
                    <n-icon><SearchIcon /></n-icon>
                  </template>
                  Search
                </n-button>
              </div>
            </n-form>
          </div>
        </section>

        <!-- Results Section -->
        <section v-if="ragStore.hasAnswer" class="results-section">
          <div class="card results-card">
            <div class="results-header">
              <h3>Answer</h3>
              <n-tag :bordered="false" type="info">
                {{ ragStore.currentAnswer?.sources.length }} sources
              </n-tag>
            </div>

            <div class="answer-content">
              {{ ragStore.currentAnswer?.answer }}
            </div>

            <div v-if="ragStore.currentAnswer?.sources.length" class="sources-section">
              <h4>Sources</h4>
              <div class="sources-list">
                <div
                  v-for="(source, index) in ragStore.currentAnswer?.sources"
                  :key="source.id"
                  class="source-item"
                >
                  <div class="source-header">
                    <span class="source-number">{{ index + 1 }}</span>
                    <n-tag v-if="source.score" size="small" type="info">
                      {{ (source.score * 100).toFixed(1) }}% match
                    </n-tag>
                  </div>
                  <p class="source-content">
                    {{ source.content }}
                  </p>
                  <div v-if="Object.keys(source.metadata).length" class="source-meta">
                    <n-text depth="3">
                      {{ formatMetadata(source.metadata) }}
                    </n-text>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- History Section -->
        <section v-if="ragStore.historyCount > 0" class="history-section">
          <h3>Recent Queries</h3>
          <div class="history-list">
            <div
              v-for="(item, index) in ragStore.queryHistory"
              :key="index"
              class="history-item"
              @click="loadFromHistory(index)"
            >
              <div class="history-question">
                {{ item.query }}
              </div>
              <n-text depth="3" class="history-time">
                {{ formatTime(item.timestamp) }}
              </n-text>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Documents Modal -->
    <DocumentsModal v-model:show="showDocumentsModal" />

    <!-- Stats Modal -->
    <StatsModal v-model:show="showStatsModal" />
  </div>
</template>

<script setup lang="ts">
import { NButton, NIcon, NForm, NFormItem, NInput, NSlider, NTag, NText } from 'naive-ui'
import { storeToRefs } from 'pinia'

const ragStore = useRagStore()
const { queryHistory } = storeToRefs(ragStore)

const showDocumentsModal = ref(false)
const showStatsModal = ref(false)

const queryForm = reactive({
  query: '',
  topK: 5,
  retrievalMethod: 'semantic' as 'semantic' | 'hybrid',
})

const documentsCount = computed(() => {
  // This would be updated from the documents store
  return 0
})

async function handleSubmit() {
  if (!queryForm.query.trim()) return

  try {
    await ragStore.askQuestion(queryForm.query, {
      topK: queryForm.topK,
      retrievalMethod: queryForm.retrievalMethod,
    })
  }
  catch (error) {
    console.error('Failed to submit query:', error)
  }
}

function loadFromHistory(index: number) {
  const historyItem = queryHistory.value[index]
  if (historyItem) {
    queryForm.query = historyItem.query
    ragStore.currentAnswer = {
      answer: historyItem.answer,
      sources: historyItem.sources,
      query: historyItem.query,
      retrievalMethod: historyItem.retrievalMethod,
    }
  }
}

function formatMetadata(metadata: Record<string, any>): string {
  const relevantKeys = ['filename', 'document_type', 'chunk_index']
  const parts = relevantKeys
    .filter(key => metadata[key])
    .map(key => `${key}: ${metadata[key]}`)
  return parts.join(' • ') || Object.values(metadata).join(' • ')
}

function formatTime(timestamp: Date): string {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

// Icons
const DocumentIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z' }),
])

const SearchIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z' }),
])

const StatsIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M3,3V21H21V19H5V3H3M9,17H13V7H9V17M15,17H19V11H15V17Z' }),
])
</script>

<style scoped>
.haystack-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid var(--color-border);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
  margin: 0;
}

.badge {
  background: var(--color-bg-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.main {
  flex: 1;
  padding: 2rem 0;
}

.query-section {
  margin-bottom: 2rem;
}

.query-card {
  max-width: 800px;
  margin: 0 auto;
}

.query-card h2 {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--color-text-secondary);
  margin-bottom: 1.5rem;
}

.query-form {
  margin-top: 1.5rem;
}

.query-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 1rem 0;
}

.query-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.results-section {
  margin-bottom: 2rem;
}

.results-card {
  max-width: 800px;
  margin: 0 auto;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.results-header h3 {
  font-size: 1.25rem;
  margin: 0;
}

.answer-content {
  font-size: 1.125rem;
  line-height: 1.8;
  color: var(--color-text);
  margin-bottom: 2rem;
}

.sources-section h4 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--color-text-secondary);
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.source-item {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius);
  padding: 1rem;
  transition: background 0.2s ease;
}

.source-item:hover {
  background: var(--color-border);
}

.source-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.source-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.source-content {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.source-meta {
  font-size: 0.75rem;
  margin-top: 0.5rem;
}

.history-section {
  max-width: 800px;
  margin: 0 auto;
}

.history-section h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--color-text-secondary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  background: #fff;
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.history-item:hover {
  background: var(--color-bg-secondary);
}

.history-question {
  font-weight: 500;
}

.history-time {
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

@media (max-width: 640px) {
  .query-options {
    grid-template-columns: 1fr;
  }
}
</style>
