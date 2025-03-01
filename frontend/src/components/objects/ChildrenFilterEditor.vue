<template>
    <div>
        <h5>Связанные объекты: {{ group.name }}</h5>

        <!-- Поле поиска -->
        <input
            v-model="searchQuery"
            type="text"
            class="form-control mb-3"
            placeholder="Поиск по имени..."
        />
        <!-- Список объектов с прокруткой -->
        <div class="scroll-container" v-if="filteredChildrenOptions.length > 0">
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
            store: useMainStore()
        };
    },
    computed: {
        // Фильтр для поиска по имени
        filteredChildrenOptions() {
            return this.store.objects[this.group.code].map(obj => obj.asChild())
                .filter(child => child.type === this.group.code)
                .filter((child) =>
                    child.name.toLowerCase().includes(this.searchQuery.toLowerCase())
                );
        },

        // Сортировка уже отфильтрованных результатов
        sortedFilteredChildren() {
            return this.filteredChildrenOptions.sort((a, b) =>
                a.name.localeCompare(b.name)
            );
        },
    },

    watch: {
        // Обновление локального состояния и передачи данных наружу
        localChildren: {
            handler(newChildren) {
                this.$emit("update:children", newChildren);
            },
            deep: true,
        },
    }
};
</script>

<style scoped>
.mb-3 {
    margin-bottom: 1rem;
}

/* Контейнер с прокруткой для длинных списков */
.scroll-container {
    max-height: 300px; /* Максимальная высота контейнера */
    overflow-y: auto; /* Горизонтальная полоса прокрутки */
    border: 1px solid #ced4da; /* Граница для визуализации области */
    padding: 0.5rem; /* Внутреннее отступление */
    border-radius: 0.25rem; /* Радиус для плавных углов */
}

/* Убираем полосы прокрутки для macOS */
.scroll-container::-webkit-scrollbar {
    width: 8px;
    background-color: #f1f1f1;
}

.scroll-container::-webkit-scrollbar-thumb {
    border-radius: 4px;
    background-color: #ccc;
}
</style>
