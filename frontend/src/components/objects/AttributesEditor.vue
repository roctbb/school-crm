<template>
    <div>
        <h4 class="mb-3">Атрибуты объекта</h4>

        <!-- Перебор доступных атрибутов -->
        <div
            v-for="attribute in availableAttributes"
            :key="attribute.code"
            class="mb-3"
        >
            <label :for="attribute.code" class="form-label">
                {{ attribute.name }}
            </label>

            <!-- Поле для string -->
            <input
                v-if="attribute.type === 'string'"
                :id="attribute.code"
                v-model="localAttributes[attribute.code]"
                type="text"
                class="form-control"
                :placeholder="`Введите ${attribute.name}`"
            />

            <!-- Поле для number -->
            <input
                v-else-if="attribute.type === 'number'"
                :id="attribute.code"
                v-model.number="localAttributes[attribute.code]"
                type="number"
                class="form-control"
                :placeholder="`Введите ${attribute.name}`"
            />

            <div v-else class="form-text text-muted">
                Неизвестный тип: <strong>{{ attribute.type }}</strong>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "AttributesEditor",
    props: {
        // Атрибуты объекта (словарь: {code: value})
        attributes: {
            type: Object,
            default: () => ({}),
        },
        // Доступные атрибуты объекта (структура формы)
        availableAttributes: {
            type: Array,
            default: () => [],
        },
    },
    emits: ["update:attributes"], // Эмитим изменения объекта
    data() {
        return {
            // Локальная копия атрибутов объекта
            localAttributes: { ...this.attributes },
        };
    },
    watch: {
        // Синхронизируем локальные изменения с наружным объектом
        localAttributes: {
            handler(newAttributes) {
                this.$emit("update:attributes", newAttributes);
            },
            deep: true,
        },
    },
};
</script>

<style scoped>
/* Для подстройки под Bootstrap можно добавлять кастомные стили */
</style>