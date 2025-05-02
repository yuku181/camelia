<template>
    <div class="container">
        <header>
            <h1>Camelia Decensor</h1>
            <p>Upload images for processing</p>
        </header>

        <main>
            <div class="upload-section">
                <h2>Upload Images</h2>
                <div
                    class="drop-zone"
                    @dragover.prevent
                    @drop.prevent="handleFileDrop"
                    @click="triggerFileInput">
                    <span v-if="!selectedFiles.length"
                        >Drag & drop images here or click to browse</span
                    >
                    <div v-else class="file-list">
                        <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
                            {{ file.name }}
                            <button class="remove-btn" @click.stop="removeFile(index)">×</button>
                        </div>
                    </div>
                    <input
                        type="file"
                        ref="fileInput"
                        @change="handleFileSelect"
                        multiple
                        accept="image/*"
                        style="display: none" />
                </div>
            </div>

            <div class="options-section">
                <h2>Processing Options</h2>
                <div class="option-group">
                    <label>Processing Type:</label>
                    <div class="radio-group">
                        <label>
                            <input type="radio" v-model="processingType" value="black_bars" />
                            Black Bars
                        </label>
                        <label>
                            <input type="radio" v-model="processingType" value="white_bars" />
                            White Bars
                        </label>
                        <label>
                            <input
                                type="radio"
                                v-model="processingType"
                                value="transparent_black" />
                            Transparent Black
                        </label>
                    </div>
                </div>

                <button
                    class="process-btn"
                    @click="processImages"
                    :disabled="!canProcess || isProcessing">
                    {{ isProcessing ? 'Processing...' : 'Process Images' }}
                </button>
            </div>

            <div v-if="isProcessing" class="loading-section">
                <div class="spinner"></div>
                <span>Processing images, this may take some time...</span>
            </div>

            <div v-if="results.length" class="results-section">
                <h2>Results</h2>
                <div class="result-grid">
                    <div v-for="(result, index) in results" :key="index" class="result-item">
                        <div class="image-comparison">
                            <div class="image-container">
                                <h3>Original</h3>
                                <img :src="result.original" alt="Original image" />
                            </div>
                            <div class="image-container">
                                <h3>Processed</h3>
                                <img :src="result.processed" alt="Processed image" />
                            </div>
                        </div>
                        <div class="result-actions">
                            <button
                                @click="
                                    downloadImage(
                                        result.processed,
                                        'processed-image-' + result.filename
                                    )
                                ">
                                Download
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="errorMessage" class="error-section">
                <div class="error-message">{{ errorMessage }}</div>
            </div>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface ResultItem {
    filename: string;
    original: string;
    processed: string;
}

interface ApiResponse {
    success: boolean;
    session_id: string;
    results: Array<{
        filename: string;
    }>;
    error?: string;
}

const API_BASE_URL: string = 'http://localhost:5000/api';

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFiles = ref<File[]>([]);
const processingType = ref<'black_bars' | 'white_bars' | 'transparent_black'>('black_bars');
const isProcessing = ref<boolean>(false);
const results = ref<ResultItem[]>([]);
const errorMessage = ref<string>('');
const sessionId = ref<string>('');

const canProcess = computed((): boolean => selectedFiles.value.length > 0);

function triggerFileInput(): void {
    fileInput.value?.click();
}

function handleFileSelect(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target.files) {
        const files = Array.from(target.files);
        selectedFiles.value = [...selectedFiles.value, ...files];
    }
}

function handleFileDrop(event: DragEvent): void {
    if (event.dataTransfer?.files) {
        const files = Array.from(event.dataTransfer.files).filter((file) =>
            file.type.startsWith('image/')
        );
        selectedFiles.value = [...selectedFiles.value, ...files];
    }
}

function removeFile(index: number): void {
    selectedFiles.value.splice(index, 1);
}

async function processImages(): Promise<void> {
    if (!canProcess.value || isProcessing.value) return;

    isProcessing.value = true;
    errorMessage.value = '';
    results.value = [];

    try {
        const formData = new FormData();

        selectedFiles.value.forEach((file) => {
            formData.append('files', file);
        });

        formData.append('model_type', processingType.value);

        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            body: formData
        });

        const data = (await response.json()) as ApiResponse;

        if (!response.ok) {
            throw new Error(data.error || 'Failed to process images');
        }

        if (!data.success || !data.session_id || !data.results || !data.results.length) {
            throw new Error('Invalid response from server');
        }

        sessionId.value = data.session_id;

        results.value = data.results.map((result) => {
            return {
                filename: result.filename,
                original: `${API_BASE_URL}/original/${result.filename}`,
                processed: `${API_BASE_URL}/results/${data.session_id}/${result.filename}`
            };
        });
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

function downloadImage(url: string, filename: string): void {
    fetch(url)
        .then((response) => response.blob())
        .then((blob) => {
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);
        })
        .catch((error: unknown) => {
            console.error('Download error:', error);
            errorMessage.value = 'Failed to download the image';
        });
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

.upload-section,
.options-section,
.loading-section,
.results-section,
.error-section {
    background: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.error-section {
    background: #fee;
    border-left: 4px solid #e74c3c;
}

.error-message {
    color: #e74c3c;
    font-weight: 500;
}

.drop-zone {
    border: 2px dashed #3498db;
    border-radius: 8px;
    padding: 40px;
    text-align: center;
    cursor: pointer;
    transition: background-color 0.3s;
}

.drop-zone:hover {
    background-color: rgba(52, 152, 219, 0.05);
}

.file-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
}

.file-item {
    display: flex;
    align-items: center;
    background: #e9f7fe;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 14px;
}

.remove-btn {
    background: none;
    border: none;
    color: #e74c3c;
    font-size: 18px;
    cursor: pointer;
    margin-left: 8px;
    padding: 0 4px;
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

.loading-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
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

.result-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
}

.image-comparison {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

@media (min-width: 768px) {
    .image-comparison {
        flex-direction: row;
        gap: 30px;
    }

    .result-grid {
        grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    }
}

.image-container {
    flex: 1;
}

.image-container img {
    max-width: 100%;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.result-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 15px;
}

.result-actions button {
    background-color: #2ecc71;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.result-actions button:hover {
    background-color: #27ae60;
}

footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    color: #7f8c8d;
}
</style>
