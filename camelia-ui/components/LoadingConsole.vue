<template>
    <div class="container">
        <div
            v-if="isVisible"
            class="flex flex-col items-center justify-center p-8 bg-surface border border-overlay rounded-lg">
            <div class="relative mb-4" v-if="isProcessing">
                <div class="w-6 h-6 rounded-full border-2 border-muted"></div>
                <div
                    class="absolute top-0 left-0 w-6 h-6 rounded-full border-2 border-iris border-t-foam animate-spin"
                    style="
                        animation-duration: 1.2s;
                        animation-timing-function: cubic-bezier(0.5, 0, 0.5, 1);
                    "></div>
            </div>
            <span class="text-text font-medium" v-if="isProcessing">{{
                message || 'Loading...'
            }}</span>

            <!-- Console output -->
            <div v-if="logs && logs.length > 0" class="mt-6 w-full max-w-[900px] custom-webkit">
                <div class="flex items-center justify-between px-3 py-2 bg-overlay rounded-t-md">
                    <div class="flex items-center">
                        <div class="w-3 h-3 rounded-full bg-rose mx-1"></div>
                        <div class="w-3 h-3 rounded-full bg-gold mx-1"></div>
                        <div class="w-3 h-3 rounded-full bg-pine mx-1"></div>
                        <span class="text-text font-medium text-sm ml-2">Camelia Logs</span>
                    </div>
                    <div class="flex items-center">
                        <Icon
                            name="lucide:x"
                            @click="closeConsole"
                            class="ml-2 text-text hover:text-love p-1 rounded transition-colors"
                            title="Close console">
                        </Icon>
                    </div>
                </div>
                <div
                    ref="consoleBody"
                    class="p-3 rounded-b-md text-sm font-mono h-60 overflow-y-auto bg-base whitespace-pre-wrap break-words">
                    <div
                        v-for="(log, index) in logs"
                        :key="index"
                        class="leading-relaxed mb-0.5 relative pl-0.5">
                        <!-- Success messages -->
                        <span
                            v-if="
                                log.includes('Job finished') ||
                                log.includes('successfully') ||
                                log.includes('completed')
                            "
                            class="text-pine font-bold">
                            {{ log }}
                        </span>
                        <!-- Error messages -->
                        <span
                            v-else-if="
                                log.includes('Job failed') ||
                                log.includes('error') ||
                                log.includes('Error')
                            "
                            class="text-love font-bold">
                            {{ log }}
                        </span>
                        <!-- Info messages -->
                        <span
                            v-else-if="
                                log.includes('Processing') ||
                                log.includes('Starting') ||
                                log.includes('info') ||
                                log.includes('Info')
                            "
                            class="text-foam">
                            {{ log }}
                        </span>
                        <!-- Completion messages -->
                        <span v-else-if="log.includes('completed')" class="text-pine">
                            {{ log }}
                        </span>
                        <!-- Warning messages -->
                        <span
                            v-else-if="log.includes('warning') || log.includes('Warning')"
                            class="text-love">
                            {{ log }}
                        </span>
                        <!-- File operations -->
                        <span
                            v-else-if="
                                log.includes('file:') ||
                                log.includes('Saved') ||
                                log.includes('Prepared')
                            "
                            class="text-iris">
                            {{ log }}
                        </span>
                        <!-- Default message style -->
                        <span v-else class="text-text">{{ log }}</span>
                    </div>
                    <div
                        v-if="isProcessing"
                        class="inline-block w-2 h-4 bg-text align-middle ml-0.5 animate-[blink_1s_step-end_infinite]"></div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
    isVisible: boolean;
    message?: string;
    logs?: string[];
    isProcessing?: boolean;
}>();

const emit = defineEmits<{
    (e: 'closeConsole'): void;
}>();

const consoleBody = ref<HTMLElement | null>(null);

watch(
    () => props.logs?.length,
    () => {
        if (consoleBody.value) {
            setTimeout(() => {
                if (consoleBody.value) {
                    consoleBody.value.scrollTop = consoleBody.value.scrollHeight;
                }
            }, 10);
        }
    },
    { flush: 'post' }
);

function closeConsole() {
    emit('closeConsole');
}
</script>

<style scoped>
@keyframes blink {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0;
    }
}
</style>
