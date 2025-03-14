<template>
    <div>
        <h5>Связанные объекты: {{ group.name }}</h5>

        <!-- Поле поиска + обработчик события 'paste' -->
        <input
            v-model="searchQuery"
            type="text"
            class="form-control mb-3"
            placeholder="Поиск по имени..."
            @paste="handlePaste"
        />

        <!-- Список объектов с прокруткой -->
        <div class="scroll-container" v-if="sortedFilteredChildren.length > 0">
            <div
                v-for="child in sortedFilteredChildren"
                :key="child.id"
                class="form-check"
            >
                <input
                    class="form-check-input"
                    type="checkbox"
                    :id="'child-' + child.id"
                    :value="child"
                    v-model="localChildren"
                />
                <label class="form-check-label" :for="'child-' + child.id">
                    {{ child.name }}
                </label>
            </div>
        </div>

        <!-- Сообщение при отсутствии результатов -->
        <div v-else class="text-muted">Нет доступных объектов для выбора.</div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";

export default {
    name: "ChildrenFilterEditor",
    props: {
        children: {
            type: Array,
            required: true,
        },
        group: {
            type: Object,
            required: true,
        },
    },
    emits: ["update:children"],
    data() {
        return {
            searchQuery: "",
            localChildren: [...this.children],
            store: useMainStore(),
        };
    },
    computed: {
        filteredChildrenOptions() {
            return this.store.objects[this.group.code]
                .map((obj) => obj.asChild())
                .filter((child) => child.type === this.group.code)
                .filter((child) =>
                    child.name.toLowerCase().includes(this.searchQuery.toLowerCase())
                );
        },
        sortedFilteredChildren() {
            return [...this.filteredChildrenOptions].sort((a, b) =>
                a.name.localeCompare(b.name)
            );
        },
    },
    watch: {
        localChildren: {
            handler(newChildren) {
                this.$emit("update:children", newChildren);
            },
            deep: true,
        },
    },
    methods: {
        handlePaste(event) {
            // Останавливаем стандартную вставку, чтобы сами обработать текст
            event.preventDefault();

            // Получаем вставленный текст
            const pasteContent = (event.clipboardData || window.clipboardData)
                .getData("text")
                .trim();

            // Разбиваем по строкам и убираем пустые
            const pasteLines = pasteContent
                .split(/\r?\n/)
                .map((line) => line.trim())
                .filter((line) => line.length > 0);

            // Для каждой строки из буфера ищем объекты, чьи имена содержат эту строку
            pasteLines.forEach((line) => {
                this.filteredChildrenOptions.forEach((child) => {
                    if (child.name.toLowerCase().includes(line.toLowerCase())) {
                        // Добавляем child, если его там еще нет
                        if (!this.localChildren.includes(child)) {
                            this.localChildren.push(child);
                        }
                    }
                });
            });
        },
    },
};
</script>

<style scoped>
.mb-3 {
    margin-bottom: 1rem;
}
.scroll-container {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #ced4da;
    padding: 0.5rem;
    border-radius: 0.25rem;
}
</style>