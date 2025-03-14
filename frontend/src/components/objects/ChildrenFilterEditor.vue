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

        <div v-else class="text-muted">Нет доступных объектов для выбора.</div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";

// Функция нормализации строки (убираем пробелы, приводим к нижнему регистру, заменяем ё на е)
function normalizeString(str) {
    return str
        .toLowerCase()
        .replaceAll(/\s+/g, "") // удаляем все пробелы
        .replaceAll("ё", "е");  // заменяем ё на е
}

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
                .filter((child) => {
                    // сравниваем нормализованные строки
                    const childName = normalizeString(child.name);
                    const queryString = normalizeString(this.searchQuery);
                    return childName.includes(queryString);
                });
        },
        sortedFilteredChildren() {
            // просто сортируем по названию
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
            event.preventDefault();
            const pasteContent = (event.clipboardData || window.clipboardData)
                .getData("text")
                .trim();

            // Разбиваем по строкам, удаляем пустые
            const pasteLines = pasteContent
                .split(/\r?\n/)
                .map((line) => line.trim())
                .filter((line) => line.length > 0);

            // Для каждой строки ищем объекты, чьи имена содержат её (с учетом нашей нормализации)
            pasteLines.forEach((line) => {
                const normLine = normalizeString(line);
                this.filteredChildrenOptions.forEach((child) => {
                    const normName = normalizeString(child.name);
                    if (normName.includes(normLine)) {
                        // Добавляем child, если его нет в localChildren
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