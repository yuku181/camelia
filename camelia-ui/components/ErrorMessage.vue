<template>
    <div v-if="message" class="error-section">
        <div class="error-message">{{ message }}</div>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    message: string;
}>();
</script>

<style scoped>
.error-section {
    background: #fee;
    border-radius: 8px;
    border-left: 4px solid #e74c3c;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.error-message {
    color: #e74c3c;
    font-weight: 500;
}
</style>
