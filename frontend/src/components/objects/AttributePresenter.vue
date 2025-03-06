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
        show_off: { // Оставляем текущее имя для совместимости
            type: Boolean,
            default: false,
        }
    },
    computed: {
        filteredAttributes() {
            if (!this.object || !this.type) return [];
            return this.type.available_attributes.filter(attr => {
                const isVisible = (attr.display && this.display) || (attr.show_off && this.show_off);
                const hasData = this.object.attributes[attr.code] && this.object.attributes[attr.code].length > 0;
                return isVisible && hasData;
            });
        }
    }
}
</script>

<template>
    <ul v-if="object">
        <li v-for="attribute in filteredAttributes" :key="attribute.code">
            <b>{{ attribute.name }}: </b>
            <span v-if="Array.isArray(object.attributes[attribute.code])">
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
    list-style-type: none;
    padding: 0 !important;
    margin: 0;
}
li {
    margin: 0;
    padding: 0;
    margin-bottom: 2px;
    font-size: 0.9rem;
}
</style>