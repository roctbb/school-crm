<template>
    <div>
        <h5>Связанные объекты: {{ group.name }}</h5>

        <!-- Кнопка-иконка для группировки -->
        <div class="d-flex align-items-center mb-3">
            <div class="dropdown me-2" :class="{ show: isMenuOpen }">
                <button
                    class="btn btn-sm btn-outline-secondary dropdown-toggle"
                    type="button"
                    @click="toggleMenu"
                >
                    <i class="bi bi-filter"></i>
                </button>
                <ul class="dropdown-menu" :class="{ show: isMenuOpen }">
                    <li>
                        <a
                            class="dropdown-item"
                            @click="selectGrouping({})"
                        >
                            Не группировать
                            <span v-if="!selectedAttribute.code" class="ms-2">
                                <i class="bi bi-check2"></i>
                            </span>
                        </a>
                    </li>
                    <li
                        v-for="attribute in groupingAttributes"
                        :key="attribute.code"
                    >
                        <a
                            class="dropdown-item"
                            @click="selectGrouping(attribute)"
                        >
                            {{ attribute.name }}
                            <span v-if="selectedAttribute.code === attribute.code" class="ms-2">
                                <i class="bi bi-check2"></i>
                            </span>
                        </a>
                    </li>
                </ul>
            </div>

            <!-- Поле поиска -->
            <input
                v-model="searchQuery"
                type="text"
                class="form-control form-control-sm"
                placeholder="Поиск по имени..."
                @paste="handlePaste"
                style="flex: 1;"
            />
        </div>

        <!-- Если не выбрана группировка, выводим обычный список -->
        <div v-if="!selectedAttribute.code">
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
            <div v-else class="text-muted">
                Нет доступных объектов для выбора.
            </div>
        </div>

        <!-- Если выбрана группировка, выводим по группам -->
        <div v-else>
            <div v-if="groupedChildren" class="scroll-container">
                <div
                    v-for="(groupItems, groupValue) in groupedChildren"
                    :key="groupValue"
                    class="mb-3"
                >
                    <!-- Заголовок группы с общим чекбоксом -->
                    <div class="form-check mb-1">
                        <input
                            class="form-check-input"
                            type="checkbox"
                            :id="'group-' + groupValue"
                            :checked="isGroupFullySelected(groupItems)"
                            @change="toggleGroupSelection(groupItems, $event.target.checked)"
                        />
                        <label
                            class="form-check-label fw-bold"
                            :for="'group-' + groupValue"
                        >
                            Группа: {{ groupValue || "Без значения" }} ({{ groupItems.length }})
                        </label>
                    </div>

                    <!-- Список объектов в группе -->
                    <div style="margin-left: 20px;">
                        <div
                            v-for="child in groupItems"
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
                </div>
            </div>
            <div v-else class="text-muted">Нет доступных объектов для выбора.</div>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";

// Функция нормализации строки (убираем пробелы, приводим к нижнему регистру, заменяем ё на е)
function normalizeString(str) {
    return str
        .toLowerCase()
        .replaceAll(/\s+/g, "")
        .replaceAll("ё", "е");
}

export default {
    name: "ChildrenFilterEditor",
    props: {
        // Массив всех детей объекта, общий для всего родительского компонента
        children: {
            type: Array,
            required: true,
        },
        // Информация о группе
        group: {
            type: Object,
            required: true,
        },
    },
    emits: ["update-children"],

    data() {
        return {
            store: useMainStore(),
            searchQuery: "",
            // Локальный список детей, относящихся к этой группе
            localChildren: [],

            // Для меню
            isMenuOpen: false,

            // Текущий выбранный атрибут: { code, name } или пустой объект
            selectedAttribute: {},
        };
    },
    computed: {
        // Сначала получаем все объекты нужного типа/группы, доступные в системе
        filteredChildrenOptions() {
            return (this.store.objects[this.group.code] || [])
                .map((obj) => obj.asChild())
                .filter((child) => child.type === this.group.code)
                .filter((child) => {
                    const childName = normalizeString(child.name);
                    const query = normalizeString(this.searchQuery);
                    return childName.includes(query);
                });
        },
        // Сортируем их по имени
        sortedFilteredChildren() {
            return [...this.filteredChildrenOptions].sort((a, b) =>
                a.name.localeCompare(b.name)
            );
        },
        // Список атрибутов, доступных для группировки
        groupingAttributes() {
            return (this.group.available_attributes || []).filter(
                (attr) => attr.group
            );
        },
        // Группируем по выбранному атрибуту (если он задан)
        groupedChildren() {
            if (!this.selectedAttribute.code) {
                return null;
            }
            const grouped = {};
            for (const child of this.sortedFilteredChildren) {
                // Ищем объект в store, чтобы получить его атрибуты
                const fullObject = this.store.getObject(child.id);
                const groupValue =
                    fullObject.attributes[this.selectedAttribute.code] || "";
                if (!grouped[groupValue]) {
                    grouped[groupValue] = [];
                }
                grouped[groupValue].push(child);
            }
            return grouped;
        },
    },
    created() {
        // При инициализации компонента отбираем из children только тех,
        // у кого тип совпадает с текущей группой (group.code),
        // чтобы не перезаписывать детей других групп
        this.localChildren = this.children.filter(
            (child) => child.type === this.group.code
        );
    },
    watch: {
        // При любом изменении списка местных детей эмитим событие, чтобы родитель понял,
        // какие именно объекты относятся к данной группе
        localChildren: {
            handler(newChildren) {
                this.$emit("update-children", {
                    groupCode: this.group.code,
                    childrenItems: newChildren,
                });
            },
            deep: true,
        },
    },
    methods: {
        toggleMenu() {
            this.isMenuOpen = !this.isMenuOpen;
        },
        selectGrouping(attribute) {
            this.selectedAttribute = attribute;
            this.isMenuOpen = false;
        },
        handlePaste(event) {
            event.preventDefault();
            const pasteContent = (event.clipboardData || window.clipboardData)
                .getData("text")
                .trim();

            const pasteLines = pasteContent
                .split(/\r?\n/)
                .map((line) => line.trim())
                .filter((line) => line.length > 0);

            // Подбираем объекты, в именах которых есть совпадение
            pasteLines.forEach((line) => {
                const normLine = normalizeString(line);
                this.filteredChildrenOptions.forEach((child) => {
                    const normName = normalizeString(child.name);
                    if (normName.includes(normLine)) {
                        if (!this.localChildren.some((lc) => lc.id === child.id)) {
                            this.localChildren.push(child);
                        }
                    }
                });
            });
        },
        // Проверяем, что все объекты конкретной подгруппы выбраны
        isGroupFullySelected(groupItems) {
            return groupItems.every((child) =>
                this.localChildren.some((lc) => lc.id === child.id)
            );
        },
        // Добавить/убрать сразу все объекты группы
        toggleGroupSelection(groupItems, shouldSelect) {
            if (shouldSelect) {
                groupItems.forEach((child) => {
                    if (!this.localChildren.some((lc) => lc.id === child.id)) {
                        this.localChildren.push(child);
                    }
                });
            } else {
                this.localChildren = this.localChildren.filter(
                    (lc) => !groupItems.some((g) => g.id === lc.id)
                );
            }
        },
    },
};
</script>

<style scoped>
.scroll-container {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #ced4da;
    padding: 0.5rem;
    border-radius: 0.25rem;
}
</style>