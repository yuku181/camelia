<template>
    <div class="options-section">
        <h2>Processing Options</h2>
        <div class="option-group">
            <label>Processing Type:</label>
            <div class="radio-group">
                <label>
                    <input type="radio" v-model="localProcessingType" value="black_bars" />
                    Black Bars
                </label>
                <label>
                    <input type="radio" v-model="localProcessingType" value="white_bars" />
                    White Bars
                </label>
                <label>
                    <input type="radio" v-model="localProcessingType" value="transparent_black" />
                    Transparent Black
                </label>
            </div>
        </div>

        <button
            class="process-btn"
            @click="$emit('process')"
            :disabled="!canProcess || isProcessing">
            {{ isProcessing ? 'Processing...' : 'Process Images' }}
        </button>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const props = defineProps<{
    processingType: 'black_bars' | 'white_bars' | 'transparent_black';
    canProcess: boolean;
    isProcessing: boolean;
}>();

const emit = defineEmits<{
    (e: 'update:processingType', type: 'black_bars' | 'white_bars' | 'transparent_black'): void;
    (e: 'process'): void;
}>();

const localProcessingType = ref<'black_bars' | 'white_bars' | 'transparent_black'>(
    props.processingType
);
watch(localProcessingType, (newValue) => {
    emit('update:processingType', newValue);
});

watch(
    () => props.processingType,
    (newValue) => {
        localProcessingType.value = newValue;
    }
);
</script>

<style scoped>
.options-section {
    background: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.option-group {
    margin-bottom: 20px;
}

.option-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
}

.radio-group {
    display: flex;
    gap: 20px;
}

.radio-group label {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
}

.process-btn {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 12px 24px;
    font-size: 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.process-btn:hover:not(:disabled) {
    background-color: #2980b9;
}

.process-btn:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
}
</style>
