// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      apiBase:
        process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1",
    },
  },

  modules: ["@pinia/nuxt"],

  nitro: {
    preset: "node-server",
  },

  css: ["~/assets/css/main.css"],

  vite: {
    optimizeDeps: {
      include: ["naive-ui", "charts.vue-ECharts"],
    },
  },
});
