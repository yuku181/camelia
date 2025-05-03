<template>
    <div class="container">
        <div
            v-if="results.length"
            class="bg-surface rounded-lg border border-overlay shadow-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-medium text-foam">Results</h2>
                <div class="flex items-center space-x-3">
                    <div class="relative">
                        <select
                            v-model="downloadFormat"
                            class="bg-base border border-highlight-low rounded-md py-2 px-3 pr-8 appearance-none focus:outline-none focus:border-iris text-sm">
                            <option value="png">PNG</option>
                            <option value="jpeg">JPEG</option>
                            <option value="webp">WebP</option>
                        </select>
                        <div
                            class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-text">
                            <Icon name="lucide:chevron-down" size="16" />
                        </div>
                    </div>
                    <button
                        @click="downloadAllImages"
                        :disabled="isDownloading"
                        class="bg-iris text-base rounded-md py-2 px-4 hover:bg-iris-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                        <span v-if="isDownloading">Downloading...</span>
                        <span v-else>Download All</span>
                    </button>
                </div>
            </div>

            <div
                class="grid grid-cols-1 md:grid-cols-2 gap-6 max-h-lvh overflow-y-auto custom-webkit pr-2">
                <!-- Original images column -->
                <div class="bg-base rounded-lg border border-highlight-low overflow-hidden">
                    <h3
                        class="text-sm font-medium text-iris uppercase tracking-wider p-4 border-b border-highlight-low">
                        Original Images
                    </h3>
                    <div class="p-4 space-y-6">
                        <div
                            v-for="(result, index) in results"
                            :key="`original-${index}`"
                            class="relative rounded-md overflow-hidden bg-highlight-low">
                            <img
                                :src="result.original"
                                :alt="`Original image ${index + 1}`"
                                class="w-full h-auto object-contain"
                                loading="lazy" />
                            <div
                                class="absolute bottom-0 right-0 bg-base bg-opacity-80 px-2 py-1 m-2 text-xs rounded">
                                {{ result.filename }}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Processed images column -->
                <div class="bg-base rounded-lg border border-highlight-low overflow-hidden">
                    <h3
                        class="text-sm font-medium text-pine uppercase tracking-wider p-4 border-b border-highlight-low">
                        Processed Images
                    </h3>
                    <div class="p-4 space-y-6">
                        <div
                            v-for="(result, index) in results"
                            :key="`processed-${index}`"
                            class="relative rounded-md overflow-hidden bg-highlight-low">
                            <img
                                :src="result.processed"
                                :alt="`Processed image ${index + 1}`"
                                class="w-full h-auto object-contain"
                                loading="lazy" />
                            <div
                                class="absolute bottom-0 right-0 bg-base bg-opacity-80 px-2 py-1 m-2 text-xs rounded">
                                {{ result.filename }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { ref } from 'vue';

interface ResultItem {
    filename: string;
    original: string;
    processed: string;
}

const props = defineProps<{
    results: ResultItem[];
}>();

const downloadFormat = ref('png');
const isDownloading = ref(false);

async function downloadAllImages(): Promise<void> {
    if (isDownloading.value) return;
    isDownloading.value = true;
    try {
        const zip = new JSZip();
        const fetchPromises = props.results.map(async (result) => {
            try {
                const url = `${result.processed}?format=${downloadFormat.value}`;
                const response = await fetch(url);
                const blob = await response.blob();

                const fileNameBase = result.filename.split('.')[0];
                const fileName = `${fileNameBase}.${downloadFormat.value}`;

                zip.file(fileName, blob);
                return true;
            } catch (error) {
                console.error(`Error fetching ${result.filename}:`, error);
                return false;
            }
        });

        await Promise.all(fetchPromises);

        const zipBlob = await zip.generateAsync({ type: 'blob' });
        saveAs(zipBlob, `processed-images-${downloadFormat.value}.zip`);
        isDownloading.value = false;
    } catch (error) {
        console.error('Error creating zip file:', error);
        alert('Failed to download images. Please try again.');
    }
}
</script>
