<template>
    <div class="upload-section">
        <h2>Upload Images</h2>
        <div
            class="drop-zone"
            @dragover.prevent
            @drop.prevent="handleFileDrop"
            @click="triggerFileInput">
            <span v-if="!selectedFiles.length">Drag & drop images here or click to browse</span>
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
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue';

const emit = defineEmits<{
    (e: 'update:selectedFiles', files: File[]): void;
}>();

const props = defineProps<{
    selectedFiles: File[];
}>();

const fileInput = ref<HTMLInputElement | null>(null);

function triggerFileInput(): void {
    fileInput.value?.click();
}

function handleFileSelect(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target.files) {
        const files = Array.from(target.files);
        emit('update:selectedFiles', [...props.selectedFiles, ...files]);
    }
}

function handleFileDrop(event: DragEvent): void {
    if (event.dataTransfer?.files) {
        const files = Array.from(event.dataTransfer.files).filter((file) =>
            file.type.startsWith('image/')
        );
        emit('update:selectedFiles', [...props.selectedFiles, ...files]);
    }
}

function removeFile(index: number): void {
    const updatedFiles = [...props.selectedFiles];
    updatedFiles.splice(index, 1);
    emit('update:selectedFiles', updatedFiles);
}
</script>

<style scoped>
.upload-section {
    background: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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
</style>
