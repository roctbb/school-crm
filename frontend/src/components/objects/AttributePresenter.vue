<script>
import {external_url} from "@/utils/helpers.js";
import {hasTeacherAccess} from "@/utils/access.js";

export default {
    name: "AttributePresenter",
    methods: {external_url},
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
                const isShown = hasTeacherAccess() || !attr.is_hidden
                const isVisible = (attr.display && this.display) || (attr.show_off && this.show_off);
                const hasData = this.object.attributes[attr.code] && this.object.attributes[attr.code].length > 0;
                return isVisible && hasData && isShown;
            });
        }
    }
}
</script>

<template>
    <ul v-if="object">
        <li v-for="attribute in filteredAttributes" :key="attribute.code">
            <b>{{ attribute.name }}: </b>
            <span v-if="attribute.type === 'file'">
                <a :href="object.attributes[attribute.code]" target="_blank">Скачать</a>
            </span>
            <span v-else-if="attribute.type === 'link'">
                <a :href="object.attributes[attribute.code]" target="_blank">{{ object.attributes[attribute.code] }}</a>
            </span>
            <span v-else-if="Array.isArray(object.attributes[attribute.code])">
                {{ object.attributes[attribute.code].join(', ') }}
            </span>
            <span v-else>
                {{ object.attributes[attribute.code] }}
            </span>

            <span v-if="attribute.is_private || attribute.is_secret"><i class="ms-1 bi bi-eye-slash" :class="{'text-danger': attribute.is_secret}"></i></span>
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