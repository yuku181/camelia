<template>
    <div class="container">
        <div class="mb-4">
            <h2 class="text-xl text-foam mb-2">Processing Options</h2>
            <p class="text-sm text-text">Choose how Camelia should process your images</p>
        </div>

        <div class="bg-surface rounded-lg p-6 border border-overlay">
            <div class="space-y-6" v-auto-animate>
                <!-- Processing Type Option -->
                <div class="option-group">
                    <label class="block text-foam text-sm mb-3">Processing Type</label>

                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3" v-auto-animate>
                        <!-- Radio option cards -->
                        <label
                            v-for="option in processingOptions"
                            :key="option.value"
                            class="relative cursor-pointer rounded-md border border-overlay p-4 hover:border-iris transition-colors"
                            :class="{
                                'border-iris bg-highlight-low': localProcessingType === option.value
                            }">
                            <input
                                type="radio"
                                :value="option.value"
                                v-model="localProcessingType"
                                class="absolute h-0 w-0 opacity-0" />
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div
                                        class="h-5 w-5 rounded-full border flex items-center justify-center border-subtle"
                                        :class="{
                                            'border-iris': localProcessingType === option.value
                                        }">
                                        <div
                                            v-if="localProcessingType === option.value"
                                            class="h-3 w-3 rounded-full bg-iris"></div>
                                    </div>
                                </div>
                                <div class="ml-3">
                                    <span
                                        class="block text-sm"
                                        :class="
                                            localProcessingType === option.value
                                                ? 'text-foam'
                                                : 'text-text'
                                        ">
                                        {{ option.label }}
                                    </span>
                                    <span class="mt-1 block text-xs text-subtle">
                                        {{ option.description }}
                                    </span>
                                </div>
                            </div>
                        </label>
                    </div>
                </div>

                <!-- Process Button -->
                <div class="pt-4 flex justify-end">
                    <button
                        @click="$emit('process')"
                        :disabled="!canProcess || isProcessing"
                        class="px-5 py-2.5 rounded-md text-base font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-base"
                        :class="[
                            canProcess && !isProcessing
                                ? 'bg-iris hover:bg-foam text-base shadow-sm'
                                : 'bg-muted text-subtle cursor-not-allowed'
                        ]">
                        <div class="flex items-center space-x-2">
                            <Icon
                                v-if="isProcessing"
                                name="lucide:loader"
                                class="w-4 h-4 animate-spin" />
                            <Icon v-else name="lucide:play" />
                            <span>{{ isProcessing ? 'Processing...' : 'Process Images' }}</span>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

type ProcessingType = 'black_bars' | 'white_bars' | 'transparent_black';

interface ProcessingOption {
    value: ProcessingType;
    label: string;
    description: string;
}

const processingOptions: ProcessingOption[] = [
    {
        value: 'black_bars',
        label: 'Black Bars',
        description: 'Decensor black censoring bars'
    },
    {
        value: 'white_bars',
        label: 'White Bars',
        description: 'Decensor white censoring bars'
    },
    {
        value: 'transparent_black',
        label: 'Transparent Black',
        description: 'Decensor semi-transparent censoring bars'
    }
];

const props = defineProps<{
    processingType: ProcessingType;
    canProcess: boolean;
    isProcessing: boolean;
}>();

const emit = defineEmits<{
    (e: 'update:processingType', type: ProcessingType): void;
    (e: 'process'): void;
}>();

const localProcessingType = ref<ProcessingType>(props.processingType);

watch(localProcessingType, (newValue) => {
    emit('update:processingType', newValue);
});

watch(
    () => props.processingType,
    (newValue) => {
        localProcessingType.value = newValue;
    }
);
</script>
