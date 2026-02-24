<template>
  <n-modal
    :show="show"
    :mask-closable="true"
    preset="card"
    title="System Statistics"
    size="medium"
    @update:show="$emit('update:show', $event)"
  >
    <div v-if="isLoading" class="loading-state">
      <n-spin size="large" />
    </div>

    <div v-else class="stats-content">
      <n-space vertical size="large">
        <!-- Document Stats -->
        <n-statistic label="Total Documents" :value="stats.total_documents">
          <template #prefix>
            <n-icon><DocumentIcon /></n-icon>
          </template>
        </n-statistic>

        <!-- System Health -->
        <n-card title="System Health" size="small">
          <n-space vertical>
            <div class="health-item">
              <span>API Status</span>
              <n-tag :type="healthStatus.api ? 'success' : 'error'">
                {{ healthStatus.api ? 'Healthy' : 'Unhealthy' }}
              </n-tag>
            </div>
            <div class="health-item">
              <span>Vector Store</span>
              <n-tag :type="healthStatus.vectorStore ? 'success' : 'warning'">
                {{ healthStatus.vectorStore ? 'Connected' : 'Not Connected' }}
              </n-tag>
            </div>
            <div class="health-item">
              <span>Embedding Service</span>
              <n-tag type="info">
                Mistral AI
              </n-tag>
            </div>
          </n-space>
        </n-card>

        <!-- Configuration Info -->
        <n-card title="Configuration" size="small">
          <n-descriptions :column="1" bordered>
            <n-descriptions-item label="Embedding Model">
              mistral-embed (1024 dimensions)
            </n-descriptions-item>
            <n-descriptions-item label="LLM Model">
              mistral-small
            </n-descriptions-item>
            <n-descriptions-item label="Vector Store">
              Qdrant (In-Memory)
            </n-descriptions-item>
          </n-descriptions>
        </n-card>
      </n-space>
    </div>

    <template #footer>
      <n-space justify="end">
        <n-button @click="refresh">
          <template #icon>
            <n-icon><RefreshIcon /></n-icon>
          </template>
          Refresh
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { NModal, NSpin, NSpace, NStatistic, NIcon, NCard, NTag, NDescriptions, NDescriptionsItem, NButton } from 'naive-ui'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const isLoading = ref(false)
const stats = ref({
  total_documents: 0,
})

const healthStatus = ref({
  api: false,
  vectorStore: true,
})

async function fetchStats() {
  isLoading.value = true
  try {
    const api = useRagApi()
    const [statsData, healthData] = await Promise.allSettled([
      api.getStats(),
      api.healthCheck(),
    ])

    if (statsData.status === 'fulfilled') {
      stats.value = statsData.value
    }

    if (healthData.status === 'fulfilled') {
      healthStatus.value.api = healthData.value.status === 'healthy'
    }
  }
  finally {
    isLoading.value = false
  }
}

function refresh() {
  fetchStats()
}

// Watch for modal open
watch(() => props.show, (show) => {
  if (show) {
    fetchStats()
  }
})

// Icons
const DocumentIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z' }),
])

const RefreshIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z' }),
])
</script>

<style scoped>
.loading-state {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.stats-content {
  padding: 0.5rem 0;
}

.health-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
