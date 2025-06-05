// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite';

export default defineNuxtConfig({
    runtimeConfig: {
        public: {
            apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:5000/api'
        }
    },
    compatibilityDate: '2024-11-01',
    devtools: { enabled: true },
    css: ['~/assets/css/main.css'],
    vite: {
        plugins: [tailwindcss()]
    },
    modules: ['@nuxt/fonts', '@nuxt/icon', '@formkit/auto-animate/nuxt']
});
