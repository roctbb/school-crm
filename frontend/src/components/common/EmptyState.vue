<template>
    <div class="empty-state">
        <i :class="`bi ${icon}`" aria-hidden="true"></i>
        <div class="empty-state-title">{{ title }}</div>
        <p v-if="description" class="mb-0">{{ description }}</p>
        <div v-if="$slots.default" class="mt-3">
            <slot />
        </div>
    </div>
</template>

<script>
export default {
    name: 'EmptyState',
    props: {
        title: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            default: '',
        },
        icon: {
            type: String,
            default: 'bi-inbox',
        },
    },
};
</script>
