<template>
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
                            downloadImage(result.processed, 'processed-image-' + result.filename)
                        ">
                        Download
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface ResultItem {
    filename: string;
    original: string;
    processed: string;
}

defineProps<{
    results: ResultItem[];
}>();

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
        });
}
</script>

<style scoped>
/* .results-section {
    background: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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
} */
</style>
