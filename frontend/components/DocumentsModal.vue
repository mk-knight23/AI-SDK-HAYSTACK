<template>
  <n-modal
    :show="show"
    :mask-closable="true"
    preset="card"
    title="Documents"
    size="huge"
    @update:show="$emit('update:show', $event)"
  >
    <template #header-extra>
      <n-button
        type="primary"
        :disabled="documentsStore.isUploading"
        @click="showUploadModal = true"
      >
        <template #icon>
          <n-icon><UploadIcon /></n-icon>
        </template>
        Upload
      </n-button>
    </template>

    <!-- Upload Section -->
    <div v-if="showUploadModal" class="upload-section">
      <n-upload
        :custom-request="handleUpload"
        :show-file-list="true"
        :disabled="documentsStore.isUploading"
        accept=".pdf,.docx,.doc,.pptx,.ppt,.txt,.md"
        multiple
      >
        <n-upload-dragger>
          <div style="margin-bottom: 12px">
            <n-icon size="48" :depth="3">
              <ArchiveIcon />
            </n-icon>
          </div>
          <n-text style="font-size: 16px">
            Click or drag a file to this area to upload
          </n-text>
          <n-p depth="3" style="margin: 8px 0 0 0">
            Supports: PDF, DOCX, PPTX, TXT, MD
          </n-p>
        </n-upload-dragger>
      </n-upload>

      <n-divider />

      <n-collapse arrow-placement="right">
        <n-collapse-item title="Index text content" name="text">
          <n-form ref="textFormRef" :model="textForm">
            <n-form-item label="Document ID (optional)">
              <n-input v-model:value="textForm.documentId" placeholder="Auto-generated if empty" />
            </n-form-item>
            <n-form-item label="Text content">
              <n-input
                v-model:value="textForm.content"
                type="textarea"
                placeholder="Enter text to index..."
                :autosize="{ minRows: 4, maxRows: 10 }"
              />
            </n-form-item>
            <n-form-item label="Metadata (JSON, optional)">
              <n-input
                v-model:value="textForm.metadata"
                type="textarea"
                placeholder='{"key": "value"}'
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
            </n-form-item>
            <n-form-item :show-label="false">
              <n-button
                type="primary"
                :disabled="!textForm.content.trim() || documentsStore.isUploading"
                :loading="documentsStore.isUploading"
                @click="handleIndexText"
              >
                Index Text
              </n-button>
            </n-form-item>
          </n-form>
        </n-collapse-item>
      </n-collapse>

      <n-button
        quaternary
        type="error"
        style="margin-top: 1rem"
        @click="showUploadModal = false"
      >
        Cancel
      </n-button>
    </div>

    <!-- Documents List -->
    <div v-else class="documents-list">
      <template v-if="documentsStore.isLoading">
        <div class="loading-state">
          <n-spin size="large" />
        </div>
      </template>

      <template v-else-if="documentsStore.isEmpty">
        <n-empty
          description="No documents indexed yet"
          style="padding: 2rem 0"
        >
          <template #icon>
            <n-icon>
              <FileIcon />
            </n-icon>
          </template>
          <template #extra>
            <n-button size="small" @click="showUploadModal = true">
              Upload your first document
            </n-button>
          </template>
        </n-empty>
      </template>

      <template v-else>
        <n-list hoverable clickable>
          <n-list-item v-for="doc in documentsStore.documents" :key="doc.id">
            <template #prefix>
              <n-icon size="24" color="#18a058">
                <FileIcon />
              </n-icon>
            </template>

            <n-thing :title="doc.metadata.filename || doc.id">
              <template #description>
                <n-space>
                  <n-tag v-if="doc.metadata.document_type" size="small" type="info">
                    {{ doc.metadata.document_type }}
                  </n-tag>
                  <n-tag v-if="doc.metadata.file_size" size="small">
                    {{ formatFileSize(doc.metadata.file_size) }}
                  </n-tag>
                </n-space>
              </template>

              {{ doc.content }}
            </n-thing>

            <template #suffix>
              <n-dropdown
                :options="getDocumentOptions(doc.id)"
                @select="handleDocumentAction($key, doc.id)"
              >
                <n-button circle quaternary>
                  <template #icon>
                    <n-icon><MoreIcon /></n-icon>
                  </template>
                </n-button>
              </n-dropdown>
            </template>
          </n-list-item>
        </n-list>

        <n-pagination
          v-if="documentsStore.totalCount > 20"
          v-model:page="currentPage"
          :page-count="Math.ceil(documentsStore.totalCount / 20)"
          style="margin-top: 1rem; justify-content: center"
        />
      </template>
    </div>
  </n-modal>

  <!-- Text Index Modal -->
  <n-modal
    v-model:show="showTextModal"
    preset="card"
    title="Index Text"
    size="medium"
  >
    <n-form ref="textFormRef" :model="textForm">
      <n-form-item label="Document ID (optional)">
        <n-input v-model:value="textForm.documentId" placeholder="Auto-generated if empty" />
      </n-form-item>
      <n-form-item label="Text content">
        <n-input
          v-model:value="textForm.content"
          type="textarea"
          placeholder="Enter text to index..."
          :autosize="{ minRows: 4, maxRows: 10 }"
        />
      </n-form-item>
      <n-form-item label="Metadata (JSON, optional)">
        <n-input
          v-model:value="textForm.metadata"
          type="textarea"
          placeholder='{"key": "value"}'
          :autosize="{ minRows: 2, maxRows: 4 }"
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="showTextModal = false">Cancel</n-button>
        <n-button
          type="primary"
          :disabled="!textForm.content.trim() || documentsStore.isUploading"
          :loading="documentsStore.isUploading"
          @click="handleIndexText"
        >
          Index Text
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { NModal, NButton, NIcon, NUpload, NUploadDragger, NText, NP, NDivider, NCollapse, NCollapseItem, NForm, NFormItem, NInput, NSpace, NList, NListItem, NThing, NTag, NDropdown, NSpin, NEmpty, NPagination } from 'naive-ui'
import type { UploadCustomRequestOptions } from 'naive-ui'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const documentsStore = useDocumentsStore()
const message = useMessage()

const showUploadModal = ref(false)
const showTextModal = ref(false)
const currentPage = ref(1)

const textForm = reactive({
  documentId: '',
  content: '',
  metadata: '',
})

async function handleUpload({ file }: UploadCustomRequestOptions) {
  try {
    await documentsStore.uploadFile(file.file as File)
    message.success('Document uploaded successfully')
  }
  catch (error) {
    message.error(error instanceof Error ? error.message : 'Upload failed')
  }
}

async function handleIndexText() {
  try {
    let metadata = undefined
    if (textForm.metadata.trim()) {
      try {
        metadata = JSON.parse(textForm.metadata)
      }
      catch {
        message.error('Invalid JSON in metadata field')
        return
      }
    }

    await documentsStore.indexText(
      textForm.content,
      textForm.documentId || undefined,
      metadata,
    )

    message.success('Text indexed successfully')
    showTextModal.value = false
    textForm.content = ''
    textForm.documentId = ''
    textForm.metadata = ''
  }
  catch (error) {
    message.error(error instanceof Error ? error.message : 'Indexing failed')
  }
}

function getDocumentOptions(documentId: string) {
  return [
    {
      label: 'Copy ID',
      key: 'copy',
      icon: () => h('i', { class: 'i-carbon-copy' }),
    },
    {
      type: 'divider',
      key: 'd1',
    },
    {
      label: 'Delete',
      key: 'delete',
      icon: () => h('i', { class: 'i-carbon-trash-can' }),
      props: {
        style: {
          color: 'var(--color-error)',
        },
      },
    },
  ]
}

async function handleDocumentAction(key: string, documentId: string) {
  if (key === 'copy') {
    navigator.clipboard.writeText(documentId)
    message.success('Document ID copied')
  }
  else if (key === 'delete') {
    try {
      await documentsStore.deleteDocument(documentId)
      message.success('Document deleted')
    }
    catch (error) {
      message.error(error instanceof Error ? error.message : 'Deletion failed')
    }
  }
}

function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unit = 0

  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024
    unit++
  }

  return `${size.toFixed(1)} ${units[unit]}`
}

// Watch for modal open to refresh documents
watch(() => props.show, (show) => {
  if (show) {
    documentsStore.loadDocuments()
  }
})

// Icons
const UploadIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M9,16V10H5L12,3L19,10H15V16H9M5,20V18H19V20H5Z' }),
])

const ArchiveIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M20,6H16V4A2,2 0 0,0 14,2H10A2,2 0 0,0 8,4V6H4C2.89,6 2,6.89 2,8V19A2,2 0 0,0 4,21H20A2,2 0 0,0 22,19V8C22,6.89 21.1,6 20,6M10,4H14V6H10V4M20,19H4V8H20V19Z' }),
])

const FileIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z' }),
])

const MoreIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z' }),
])
</script>

<style scoped>
.upload-section {
  padding: 1rem 0;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.documents-list {
  max-height: 500px;
  overflow-y: auto;
}
</style>
