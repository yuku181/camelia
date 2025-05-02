<script setup lang="ts">
const censorsTypes = [
    {
        title: 'Black Bars',
        description: 'Removes commonly found black censorship bars.',
        originalImage: '/demos/black_bars_original.jpg',
        processedImage: '/demos/black_bars_processed.jpg',
        color: 'text-rose'
    },
    {
        title: 'White Bars',
        description: 'Removes occasionally appearing white censorship bars.',
        originalImage: '/demos/white_bars_original.jpg',
        processedImage: '/demos/white_bars_processed.jpg',
        color: 'text-foam'
    },
    {
        title: 'Transparent Black',
        description:
            'Handles semi-transparent black censoring overlays, found in digital releases.',
        originalImage: '/demos/transparent_black_original.jpg',
        processedImage: '/demos/transparent_black_processed.jpg',
        color: 'text-iris'
    }
];
</script>

<template>
    <div class="container">
        <div class="text-center mb-12">
            <h1 class="text-4xl font-bold text-foam mb-3">Demos</h1>
            <p class="text-text text-lg max-w-2xl mx-auto">Demonstrations for the application</p>
        </div>

        <!-- Demo comparisons -->
        <div class="space-y-24">
            <div
                v-for="(demo, index) in censorsTypes"
                :key="index"
                class="demo-section"
                v-auto-animate>
                <h2 class="text-3xl font-bold mb-3" :class="demo.color">{{ demo.title }}</h2>
                <p class="text-text text-lg mb-8 max-w-3xl">{{ demo.description }}</p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-12">
                    <!-- Original image -->
                    <div class="flex flex-col">
                        <h3 class="text-xl font-medium text-subtle mb-4 flex items-center">
                            <span class="inline-block w-3 h-3 mr-2 rounded-full bg-love"></span>
                            Original Image
                        </h3>
                        <div
                            class="relative bg-surface border border-overlay rounded-lg overflow-hidden h-96">
                            <!-- Placeholder image -->
                            <div
                                class="absolute inset-0 flex items-center justify-center bg-highlight-low">
                                <div class="text-center p-4">
                                    <Icon name="lucide:image" size="48" class="text-subtle mb-3" />
                                    <p class="text-subtle">Original {{ demo.title }} Image</p>
                                </div>
                            </div>
                            <!-- <img :src="demo.originalImage" :alt="`Original ${demo.title}`" class="w-full h-full object-contain" /> -->
                        </div>
                    </div>

                    <!-- Processed image -->
                    <div class="flex flex-col">
                        <h3 class="text-xl font-medium text-subtle mb-4 flex items-center">
                            <span class="inline-block w-3 h-3 mr-2 rounded-full bg-pine"></span>
                            Processed Image
                        </h3>
                        <div
                            class="relative bg-surface border border-overlay rounded-lg overflow-hidden h-96">
                            <!-- Placeholder image -->
                            <div
                                class="absolute inset-0 flex items-center justify-center bg-highlight-low">
                                <div class="text-center p-4">
                                    <Icon name="lucide:image" size="48" class="text-subtle mb-3" />
                                    <p class="text-subtle">Processed {{ demo.title }} Image</p>
                                </div>
                            </div>
                            <!-- <img :src="demo.processedImage" :alt="`Processed ${demo.title}`" class="w-full h-full object-contain" /> -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="my-20 text-center">
            <h2 class="text-2xl font-bold text-foam mb-4">Try it yourself!</h2>
            <p class="text-text mb-6">
                Process your own images using our web interface or command-line tool.
            </p>
            <div class="flex justify-center space-x-4">
                <NuxtLink
                    to="/"
                    class="px-6 py-3 bg-iris text-base hover:bg-opacity-90 rounded-md transition-colors">
                    Go to App
                </NuxtLink>
                <NuxtLink
                    to="/guide"
                    class="px-6 py-3 bg-surface border border-overlay text-text hover:bg-highlight-low rounded-md transition-colors">
                    Read Guide
                </NuxtLink>
            </div>
        </div>
    </div>
</template>

<style scoped>
.demo-section {
    scroll-margin-top: 80px;
}
</style>
