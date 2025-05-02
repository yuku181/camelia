<template>
    <div v-if="isVisible" class="loading-section">
        <div class="spinner"></div>
        <span>{{ message }}</span>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    isVisible: boolean;
    message?: string;
}>();
</script>

<style scoped>
.loading-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    background: #f9f9f9;
    border-radius: 8px;
    margin-bottom: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(52, 152, 219, 0.3);
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}
</style>
