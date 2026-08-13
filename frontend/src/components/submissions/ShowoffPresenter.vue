<script>
export default {
    name: "ShowoffPresenter.vue",
    props: {
        attributes: {
            type: Object,
            default: () => ({}),
        },
        hiddenAttributes: {
            type: Array,
            default: () => [],
        }
    },
    computed: {
        visibleAttributes() {
            return Object.entries(this.attributes || {})
                .filter(([name]) => !this.hiddenAttributes.includes(name));
        },
    },
}
</script>

<template>
    <ul>
        <li v-for="([name, value]) in visibleAttributes"
            :key="name">
            <span class="attribute-name">{{ name }}</span>

            <span v-if="Array.isArray(value)">
                {{ value.join(', ') }}
            </span>
            <span v-else>
                {{ value }}
            </span>
        </li>
    </ul>
</template>

<style scoped>
ul {
    display: grid;
    gap: 0.45rem;
    list-style-type: none;
    padding: 0 !important;
    margin: 0;
}

li {
    display: grid;
    gap: 0.05rem;
    margin: 0;
    padding: 0;
    font-size: 0.9rem;
    line-height: 1.35;
    overflow-wrap: anywhere;
}

.attribute-name {
    color: var(--silaeder-muted);
    font-size: 0.75rem;
    font-weight: 500;
}
</style>
