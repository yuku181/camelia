<template>
    <div class="container">
        <div
            v-if="results.length"
            class="bg-surface rounded-lg border border-overlay shadow-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-medium text-foam">Results</h2>
                <button
                    @click="downloadAllImages"
                    class="flex items-center space-x-2 bg-iris hover:bg-opacity-80 text-base py-2 px-4 rounded-md transition-colors duration-200">
                    <Icon name="lucide:download" size="20" class="text-base" />
                    <span>Download All</span>
                </button>
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

interface ResultItem {
    filename: string;
    original: string;
    processed: string;
}

const props = defineProps<{
    results: ResultItem[];
}>();

async function downloadAllImages(): Promise<void> {
    try {
        const zip = new JSZip();
        const fetchPromises = props.results.map(async (result) => {
            try {
                const response = await fetch(result.processed);
                const blob = await response.blob();
                zip.file(`${result.filename}`, blob);
                return true;
            } catch (error) {
                console.error(`Error fetching ${result.filename}:`, error);
                return false;
            }
        });

        await Promise.all(fetchPromises);

        const zipBlob = await zip.generateAsync({ type: 'blob' });
        saveAs(zipBlob, 'processed-images.zip');
    } catch (error) {
        console.error('Error creating zip file:', error);
        alert('Failed to download images. Please try again.');
    }
}
</script>
