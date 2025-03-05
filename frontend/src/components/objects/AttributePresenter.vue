<script>
export default {
    name: "AttributePresenter",
    props: {
        object: Object,
        type: Object,
        display: {
            type: Boolean,
            default: true,
        },
        show_off: {
            type: Boolean,
            default: false,
        }
    },
}
</script>

<template>
    <ul v-if="object">
        <li v-for="attribute in type.available_attributes.filter(attr => ((attr.display === true && display === true) || (attr.show_off === true && show_off === true)) && object.attributes[attr.code])"
            :key="attribute.code">
            <b>{{ attribute.name }}:</b> <span v-if="Array.isArray(object.attributes[attribute.code])">
      {{ object.attributes[attribute.code].join(', ') }}
    </span>
            <span v-else>
      {{ object.attributes[attribute.code] }}
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