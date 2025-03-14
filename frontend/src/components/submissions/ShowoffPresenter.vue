<script>
export default {
    name: "ShowoffPresenter.vue",
    props: {
        attributes: {
            type: Object,
            default: {},
        }
    },
}
</script>

<template>
    <ul>
        <li v-for="(value, name) in attributes"
            :key="name">
            <b>{{ name }}:</b>

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
    list-style-type: none; /* Убирает стандартные маркеры */
    padding: 0 !important; /* Убирает отступы */
    margin: 0; /* Убирает внешние отступы */
}

li {
    margin: 0; /* Убирает внешние отступы у элементов списка */
    padding: 0; /* Убирает внутренние отступы у элементов списка */
    margin-bottom: 2px;
    font-size: 0.9rem;
}
</style>