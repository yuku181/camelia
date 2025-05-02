<template>
    <div class="container">
        <div class="mb-4">
            <h2 class="text-xl text-foam mb-2">Select Images</h2>
            <div class="flex items-center justify-between mb-2">
                <p class="text-sm text-text">Choose images to process with Camelia</p>
                <div
                    v-if="selectedFiles.length > 0"
                    class="mt-2 flex justify-end space-x-2"
                    v-auto-animate>
                    <button
                        @click.stop="emit('update:selectedFiles', [])"
                        class="px-2 text-sm text-text hover:text-love transition-colors">
                        Clear all
                    </button>
                </div>
            </div>
        </div>

        <div
            class="drop-zone border-2 border-dashed border-overlay hover:border-iris focus-within:border-iris transition-colors duration-300 rounded-lg p-6 bg-surface cursor-pointer relative"
            :class="{ 'border-foam': isDragging }"
            @dragenter.prevent="handleDragEnter"
            @dragover.prevent="() => {}"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleFileDrop"
            @click="triggerFileInput"
            ref="dropZone">
            <div
                v-if="!selectedFiles.length"
                class="flex flex-col items-center justify-center py-8">
                <div class="mb-4 text-text">
                    <Icon name="lucide:upload-cloud" size="64px" />
                </div>
                <p class="text-center text-text mb-2">
                    <span class="text-foam">Drag & drop images</span> or click to browse
                </p>
                <p class="text-xs text-subtle">Accepted formats: JPEG, PNG, WebP</p>
            </div>

            <div
                v-else
                class="custom-webkit space-y-2 max-h-64 overflow-y-auto pr-2"
                v-auto-animate>
                <div
                    v-for="(file, index) in selectedFiles"
                    :key="index"
                    class="file-item flex items-center bg-highlight-low rounded-md p-3 group hover:bg-highlight-med transition-colors duration-200">
                    <div class="w-10 h-10 mr-3 rounded overflow-hidden bg-overlay">
                        <img
                            :src="getImagePreview(file)"
                            :alt="file.name"
                            class="w-full h-full object-cover" />
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-text truncate text-sm">{{ file.name }}</p>
                        <p class="text-subtle text-xs">{{ formatFileSize(file.size) }}</p>
                    </div>
                    <button
                        class="remove-btn p-2 text-subtle opacity-0 group-hover:opacity-100 hover:text-love transition-all duration-200"
                        @click.stop="removeFile(index)">
                        <Icon name="lucide:x" size="24px" />
                    </button>
                </div>
            </div>

            <input
                type="file"
                ref="fileInput"
                @change="handleFileSelect"
                multiple
                accept="image/*"
                class="hidden" />

            <div
                v-if="isDragging"
                class="absolute inset-0 bg-base bg-opacity-50 flex items-center justify-center rounded-lg">
                <div class="flex flex-col items-center">
                    <div class="w-16 h-16 text-text">
                        <Icon name="lucide:upload-cloud" size="64px" />
                    </div>
                    <p class="text-foam text-lg">Release to upload</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
    (e: 'update:selectedFiles', files: File[]): void;
}>();

const props = defineProps<{
    selectedFiles: File[];
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const dropZone = ref<HTMLElement | null>(null);
const isDragging = ref(false);
const imagePreviews = ref<Record<string, string>>({});

let dragCounter = 0;

function triggerFileInput(): void {
    fileInput.value?.click();
}

function handleFileSelect(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target.files) {
        const files = Array.from(target.files);
        emit('update:selectedFiles', [...props.selectedFiles, ...files]);
        generatePreviews(files);
    }
}

function handleDragEnter(e: DragEvent): void {
    dragCounter++;
    isDragging.value = true;
}

function handleDragLeave(e: DragEvent): void {
    dragCounter--;

    const relatedTarget = e.relatedTarget as Node;
    if (dragCounter === 0 || (!dropZone.value?.contains(relatedTarget) && relatedTarget !== null)) {
        isDragging.value = false;
        dragCounter = 0;
    }
}

function handleFileDrop(event: DragEvent): void {
    isDragging.value = false;
    dragCounter = 0;
    if (event.dataTransfer?.files) {
        const files = Array.from(event.dataTransfer.files).filter((file) =>
            file.type.startsWith('image/')
        );
        emit('update:selectedFiles', [...props.selectedFiles, ...files]);
        generatePreviews(files);
    }
}

function removeFile(index: number): void {
    const updatedFiles = [...props.selectedFiles];
    updatedFiles.splice(index, 1);
    emit('update:selectedFiles', updatedFiles);
}

function generatePreviews(files: File[]): void {
    files.forEach((file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            if (e.target?.result) {
                imagePreviews.value[file.name] = e.target.result as string;
            }
        };
        reader.readAsDataURL(file);
    });
}

function getImagePreview(file: File): string {
    return imagePreviews.value[file.name] || '';
}

function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
</script>
