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
                            <button
                                class="absolute top-0 left-0 m-2 px-2 py-1 text-xs rounded bg-iris text-base"
                                @click="openEditor(index)">
                                Edit Mask
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <MaskEditor
            v-if="showEditor"
            :image="editorImage"
            @save="saveMask"
            @close="closeEditor" />
    </div>
</template>

<script setup lang="ts">
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { ref } from 'vue';
import MaskEditor from '@/components/MaskEditor.vue';
import { reinpaintImage, ResultItem } from '@/services/api';

interface LocalResultItem extends ResultItem {}

const props = defineProps<{
    results: LocalResultItem[];
}>();

const emit = defineEmits<{
    (e: 'update:results', results: LocalResultItem[]): void;
}>();

const downloadFormat = ref('png');
const isDownloading = ref(false);
const showEditor = ref(false);
const editingIndex = ref<number | null>(null);
const editorImage = ref('');
const editorFilename = ref('');

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

function openEditor(index: number) {
    const item = props.results[index];
    editorImage.value = item.original;
    editorFilename.value = item.filename;
    editingIndex.value = index;
    showEditor.value = true;
}

function closeEditor() {
    showEditor.value = false;
    editingIndex.value = null;
}

async function saveMask(blob: Blob) {
    if (editingIndex.value === null) return;
    const item = props.results[editingIndex.value];
    try {
        const newResult = await reinpaintImage(item.sessionId, item.filename, blob);
        const updated = [...props.results, newResult];
        emit('update:results', updated);
    } catch (error) {
        console.error('Error reinpainting image:', error);
    } finally {
        closeEditor();
    }
}
</script>
