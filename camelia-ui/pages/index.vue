<template>
    <main v-auto-animate>
        <FileUploader v-model:selectedFiles="selectedFiles" />

        <ProcessingOptions
            v-model:processingType="processingType"
            :canProcess="canProcess"
            :isProcessing="isProcessing"
            @process="processImages"
            @cancel="cancelProcessing" />

        <LoadingConsole
            message="Processing images, this may take some time..."
            :logs="processLogs"
            :isProcessing="isProcessing"
            :isVisible="isProcessing || showLogs"
            @closeConsole="hideConsole" />

        <ResultsDisplay :results="results" />

        <ErrorMessage :message="errorMessage" />
    </main>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import FileUploader from '@/components/FileUploader.vue';
import ProcessingOptions from '@/components/ProcessingOptions.vue';
import LoadingConsole from '~/components/LoadingConsole.vue';
import ResultsDisplay from '@/components/ResultsDisplay.vue';
import ErrorMessage from '@/components/ErrorMessage.vue';
import {
    processImages as apiProcessImages,
    checkProcessingStatus,
    streamProcessingLogs,
    transformResults,
    cancelProcessingJob
} from '@/services/api';
import type { ResultItem } from '@/services/api';

const selectedFiles = ref<File[]>([]);
const processingType = ref<'black_bars' | 'white_bars' | 'transparent_black'>('black_bars');
const isProcessing = ref<boolean>(false);
const showLogs = ref<boolean>(false);
const results = ref<ResultItem[]>([]);
const errorMessage = ref<string>('');
const processLogs = ref<string[]>([]);
const currentSessionId = ref<string | null>(null);
let logStreamCleanup: (() => void) | null = null;
let statusCheckInterval: number | null = null;

const canProcess = computed((): boolean => selectedFiles.value.length > 0);

async function processImages(): Promise<void> {
    if (!canProcess.value || isProcessing.value) return;

    isProcessing.value = true;
    showLogs.value = true;
    errorMessage.value = '';
    results.value = [];
    processLogs.value = [];

    try {
        const { sessionId } = await apiProcessImages(selectedFiles.value, processingType.value);
        currentSessionId.value = sessionId;

        logStreamCleanup = streamProcessingLogs(sessionId, (log) => {
            if (log.trim()) {
                processLogs.value.push(log);
            }
        });

        statusCheckInterval = window.setInterval(async () => {
            try {
                if (!currentSessionId.value) return;

                const status = await checkProcessingStatus(currentSessionId.value);

                if (status.status === 'completed') {
                    if (status.results) {
                        results.value = transformResults(currentSessionId.value, status.results);
                    }
                    finishProcessing();
                } else if (status.status === 'error') {
                    errorMessage.value =
                        'An error occurred during processing. Please check the logs for details.';
                    finishProcessing();
                }
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }, 3000);
    } catch (error: unknown) {
        console.error('Error processing images:', error);
        errorMessage.value =
            error instanceof Error
                ? error.message
                : 'An error occurred while processing the images';
        finishProcessing();
    }
}

function finishProcessing(): void {
    isProcessing.value = false;

    if (statusCheckInterval !== null) {
        window.clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }

    if (logStreamCleanup) {
        logStreamCleanup();
        logStreamCleanup = null;
    }

    currentSessionId.value = null;

    showLogs.value = true;
}

function hideConsole(): void {
    showLogs.value = false;
}

function cancelProcessing(): void {
    if (currentSessionId.value) {
        cancelProcessingJob(currentSessionId.value);
    }
    finishProcessing();
}

onUnmounted(() => {
    if (statusCheckInterval !== null) {
        window.clearInterval(statusCheckInterval);
    }

    if (logStreamCleanup) {
        logStreamCleanup();
    }
});
</script>
