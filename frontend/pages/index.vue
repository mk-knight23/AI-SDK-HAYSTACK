<template>
  <div class="hello-world">
    <h1>Hello World from TrendFactory</h1>
    <p>Nuxt 3 + Django Full Stack Application</p>
    <div class="status">
      <p>Backend Status: <span :class="statusClass">{{ backendStatus }}</span></p>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const backendStatus = ref('Checking...')
const statusClass = ref('checking')

onMounted(async () => {
  try {
    const response = await fetch(`${config.public.apiBase}/health`)
    if (response.ok) {
      const data = await response.json()
      backendStatus.value = data.status || 'Healthy'
      statusClass.value = 'healthy'
    } else {
      backendStatus.value = 'Unavailable'
      statusClass.value = 'unhealthy'
    }
  } catch (error) {
    backendStatus.value = 'Offline'
    statusClass.value = 'unhealthy'
  }
})
</script>

<style scoped>
.hello-world {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  font-family: system-ui, -apple-system, sans-serif;
  text-align: center;
}

h1 {
  color: #00dc82;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

p {
  color: #333;
  font-size: 1.2rem;
}

.status {
  margin-top: 2rem;
  padding: 1rem 2rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.healthy {
  color: #00dc82;
  font-weight: bold;
}

.unhealthy {
  color: #ff6b6b;
  font-weight: bold;
}

.checking {
  color: #ffa500;
  font-weight: bold;
}
</style>
