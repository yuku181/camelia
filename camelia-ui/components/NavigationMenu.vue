<script setup lang="ts">
interface NavItem {
    label: string;
    icon?: string;
    to?: string;
    target?: string;
    disabled?: boolean;
    type?: string;
}

const items: NavItem[] = [
    {
        label: 'Demo',
        icon: 'lucide:flask-conical',
        to: '/demo'
    },
    {
        label: 'Guide',
        icon: 'lucide:book-open',
        to: '/guide'
    },
    {
        label: 'FAQ',
        icon: 'lucide:message-circle-question',
        to: '/faq'
    },
    {
        label: 'GitHub',
        icon: 'simple-icons:github',
        to: 'https://github.com/windbow27/camelia',
        target: '_blank'
    }
];

const isOpen = ref(false);
const toggleMenu = () => {
    isOpen.value = !isOpen.value;
};

const activeItem = ref<number | null>(null);
const setActive = (index: number) => {
    activeItem.value = index;
};
</script>

<template>
    <nav class="bg-surface w-full">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <NuxtLink to="/" class="flex-shrink-0 flex items-center">
                    <img src="/logo.png" alt="Logo" class="h-6 w-6" />
                    <span class="ml-2 text-xl font-bold text-iris">Camelia</span>
                </NuxtLink>

                <!-- Desktop Menu -->
                <div class="hidden md:block">
                    <div class="ml-10 flex items-center space-x-6">
                        <template v-for="(item, index) in items" :key="index">
                            <!-- Regular nav item -->
                            <NuxtLink
                                v-if="!item.disabled && !item.target"
                                :to="item.to || '/'"
                                @mouseenter="setActive(index)"
                                @mouseleave="activeItem = null"
                                :class="[
                                    'flex items-center space-x-2',
                                    activeItem === index ? 'text-foam' : 'text-iris hover:text-foam'
                                ]">
                                <Icon v-if="item.icon" :name="item.icon" />
                                <span>{{ item.label }}</span>
                            </NuxtLink>

                            <!-- External link -->
                            <a
                                v-else-if="!item.disabled && item.target"
                                :href="item.to"
                                :target="item.target"
                                @mouseenter="setActive(index)"
                                @mouseleave="activeItem = null"
                                :class="[
                                    'flex items-center space-x-2',
                                    activeItem === index
                                        ? 'text-foam '
                                        : 'text-iris hover:text-foam'
                                ]">
                                <Icon v-if="item.icon" :name="item.icon" />
                                <span>{{ item.label }}</span>
                            </a>
                        </template>
                    </div>
                </div>

                <!-- Mobile menu button -->
                <div class="md:hidden flex items-center">
                    <button
                        @click="toggleMenu"
                        class="text-iris hover:text-foam focus:outline-none">
                        <Icon name="lucide:menu" size="24px" />
                    </button>
                </div>
            </div>
        </div>

        <!-- Mobile Menu -->
        <div class="md:hidden bg-surface border-t border-overlay overflow-hidden" v-auto-animate>
            <div class="px-2 pt-2 pb-3 space-y-1" v-if="isOpen">
                <template v-for="(item, index) in items" :key="index">
                    <!-- Regular nav item -->
                    <NuxtLink
                        v-if="!item.disabled && !item.target"
                        :to="item.to || '/'"
                        @mouseenter="setActive(index)"
                        @mouseleave="activeItem = null"
                        :class="[
                            'block px-3 py-2 items-center space-x-2 transition-all duration-200',
                            activeItem === index
                                ? 'text-foam translate-x-1'
                                : 'text-iris hover:text-foam'
                        ]">
                        <Icon v-if="item.icon" :name="item.icon" />
                        <span>{{ item.label }}</span>
                    </NuxtLink>

                    <!-- External link -->
                    <a
                        v-else-if="!item.disabled && item.target"
                        :href="item.to"
                        :target="item.target"
                        @mouseenter="setActive(index)"
                        @mouseleave="activeItem = null"
                        :class="[
                            'block px-3 py-2 items-center space-x-2 transition-all duration-200',
                            activeItem === index
                                ? 'text-foam translate-x-1'
                                : 'text-iris hover:text-foam'
                        ]">
                        <Icon v-if="item.icon" :name="item.icon" />
                        <span>{{ item.label }}</span>
                    </a>
                </template>
            </div>
        </div>
    </nav>
</template>

<style scoped></style>
