<template>
    <div class="bg-rosepine-base">
        <header>
            <h1>Camelia Decensor</h1>
            <p>Upload images for processing</p>
        </header>

        <main>
            <FileUploader v-model:selectedFiles="selectedFiles" />

            <ProcessingOptions
                v-model:processingType="processingType"
                :canProcess="canProcess"
                :isProcessing="isProcessing"
                @process="processImages" />

            <LoadingSpinner
                :isVisible="isProcessing"
                message="Processing images, this may take some time..." />

            <ResultsDisplay :results="results" />

            <ErrorMessage :message="errorMessage" />
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import FileUploader from '@/components/FileUploader.vue';
import ProcessingOptions from '@/components/ProcessingOptions.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import ResultsDisplay from '@/components/ResultsDisplay.vue';
import ErrorMessage from '@/components/ErrorMessage.vue';
import { processImages as apiProcessImages } from '@/services/api';
import type { ResultItem } from '@/services/api';

const selectedFiles = ref<File[]>([]);
const processingType = ref<'black_bars' | 'white_bars' | 'transparent_black'>('black_bars');
const isProcessing = ref<boolean>(false);
const results = ref<ResultItem[]>([]);
const errorMessage = ref<string>('');

const canProcess = computed((): boolean => selectedFiles.value.length > 0);

async function processImages(): Promise<void> {
    if (!canProcess.value || isProcessing.value) return;

    isProcessing.value = true;
    errorMessage.value = '';
    results.value = [];

    try {
        const processedResults = await apiProcessImages(selectedFiles.value, processingType.value);
        results.value = processedResults;
    } catch (error: unknown) {
        console.error('Error processing images:', error);
        errorMessage.value =
            error instanceof Error
                ? error.message
                : 'An error occurred while processing the images';
    } finally {
        isProcessing.value = false;
    }
}
</script>

<style>
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 40px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

h1 {
    color: #2c3e50;
    margin-bottom: 10px;
}

h2 {
    color: #3498db;
    margin-bottom: 15px;
}

footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    color: #7f8c8d;
}
</style>
