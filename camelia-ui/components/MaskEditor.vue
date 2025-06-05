<template>
  <div class="fixed inset-0 bg-base bg-opacity-80 flex items-center justify-center z-50">
    <div class="bg-surface p-4 rounded-lg border border-overlay">
      <div class="relative">
        <img :src="image" alt="image" ref="imgRef" class="max-w-full max-h-[80vh]" @load="initCanvas" />
        <canvas
          ref="canvas"
          class="absolute top-0 left-0"
          @mousedown="start"
          @mousemove="move"
          @mouseup="end"
          @mouseleave="end" />
      </div>
      <div class="mt-4 flex justify-end space-x-2">
        <button class="px-3 py-1 rounded bg-muted" @click="$emit('close')">Cancel</button>
        <button class="px-3 py-1 rounded bg-iris" @click="emitSave">Save Mask</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{ image: string }>();
const emit = defineEmits<{ (e: 'save', blob: Blob): void; (e: 'close'): void }>();

const canvas = ref<HTMLCanvasElement | null>(null);
const imgRef = ref<HTMLImageElement | null>(null);
let drawing = false;
let ctx: CanvasRenderingContext2D | null = null;

function initCanvas() {
  if (!canvas.value || !imgRef.value) return;
  canvas.value.width = imgRef.value.naturalWidth;
  canvas.value.height = imgRef.value.naturalHeight;
  ctx = canvas.value.getContext('2d');
  if (ctx) {
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
  }
}

function start(e: MouseEvent) {
  if (!ctx) return;
  drawing = true;
  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY);
}

function move(e: MouseEvent) {
  if (!drawing || !ctx) return;
  ctx.lineTo(e.offsetX, e.offsetY);
  ctx.stroke();
}

function end() {
  drawing = false;
}

function emitSave() {
  if (!canvas.value) return;
  canvas.value.toBlob((blob) => {
    if (blob) emit('save', blob);
  });
}
</script>

<style scoped>
canvas {
  pointer-events: auto;
  cursor: crosshair;
}
</style>
