<template>
    <div class="container">
        <transition
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition duration-200 ease-in"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95">
            <div
                v-if="message"
                class="bg-base border-l-4 border-love rounded-md shadow-md mb-6 overflow-hidden">
                <div class="flex p-4 items-start">
                    <div class="flex-shrink-0 mt-3 mr-3">
                        <Icon name="lucide:alert-triangle" size="24" class="text-love" />
                    </div>
                    <div class="flex-1">
                        <h3 class="text-lg font-medium text-love">Error</h3>
                        <p class="text-text">{{ message }}</p>
                        <div v-if="hint" class="mt-2 text-sm text-subtle italic">{{ hint }}</div>
                    </div>
                </div>

                <div v-if="details" class="bg-highlight-low border-t border-overlay p-3">
                    <pre
                        class="text-xs text-subtle font-mono overflow-x-auto whitespace-pre-wrap"
                        >{{ details }}</pre
                    >
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    message: string;
    details?: string;
    hint?: string;
}>();

defineEmits<{
    (e: 'dismiss'): void;
}>();
</script>
