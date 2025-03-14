<template>
    <BaseLayout>
        <!-- Динамические вкладки с кнопкой создания объекта -->
        <div class="d-flex align-items-center justify-content-between border-bottom mt-3">
            <ul class="nav nav-tabs flex-grow-1 border-0">
                <li
                    class="nav-item"
                    v-for="type in objectTypes"
                    :key="type.code"
                >
                    <button
                        class="nav-link"
                        :class="{ active: activeTab === type.code }"
                        @click="selectTab(type.code)"
                    >
                        {{ type.name }}

                        <span
                            v-if="objectCounts[type.code] > 0"
                            class="badge bg-secondary rounded-5 ms-1"
                        >
              {{ objectCounts[type.code] }}
            </span>
                    </button>
                </li>
            </ul>
            <button
                v-if="activeTab"
                class="btn btn-success btn-sm ms-1 d-flex align-items-center"
                @click="createObject(activeTab)"
            >
                <i class="bi bi-plus me-1"></i> Создать
            </button>
        </div>

        <!-- Поле поиска и выпадающее меню -->
        <div class="d-flex mt-3 align-items-center">
            <input
                type="text"
                class="form-control form-control-sm me-1"
                placeholder="Введите текст для поиска..."
                v-model="searchQuery"
            />

            <!-- Кнопка-иконка для группировки -->
            <div class="dropdown" :class="{ show: isMenuOpen }">
                <button
                    class="btn btn-sm btn-outline-secondary dropdown-toggle me-1"
                    type="button"
                    @click="toggleMenu"
                >
                    <i class="bi bi-filter"></i>
                </button>
                <ul class="dropdown-menu" :class="{ 'show': isMenuOpen }">
                    <li>
                        <button
                            class="dropdown-item"
                            @click="selectGrouping({})"
                        >
                            Не группировать
                            <span v-if="!selectedAttribute.code" class="me-2">
                <i class="bi bi-check2"></i>
              </span>
                        </button>
                    </li>
                    <li
                        v-for="attribute in groupingAttributes"
                        :key="attribute.code"
                    >
                        <button
                            class="dropdown-item"
                            @click="selectGrouping(attribute)"
                        >
                            {{ attribute.name }}
                            <span
                                v-if="selectedAttribute.code === attribute.code"
                                class="me-1"
                            >
                <i class="bi bi-check2"></i>
              </span>
                        </button>
                    </li>
                </ul>
            </div>

            <!-- Кнопка переключения карточного/табличного вида (с иконками) -->
            <button
                class="btn btn-outline-secondary btn-sm"
                @click="isTableView = !isTableView"
            >
                <i v-if="isTableView" class="bi bi-grid"></i>
                <i v-else class="bi bi-list"></i>
            </button>
        </div>

        <!-- Контент вкладок -->
        <div class="tab-content mt-3">
            <loading v-if="isLoading" />

            <TableView
                v-else-if="isTableView"
                :data="sortedObjects"
                :grouped-data="groupedObjects"
                :attributes="tableAttributes"
                :grouping-attribute="selectedAttribute"
                :sortKey.sync="sortKey"
                :sortDirection.sync="sortDirection"
            />

            <CardView
                v-else
                :objects="filteredObjects"
                :grouped-data="groupedObjects"
                :object-type="store.getObjectTypeByCode(activeTab)"
                :grouping-attribute="selectedAttribute"
                size="big"
            />
        </div>
    </BaseLayout>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import TableView from "@/components/objects/TableView.vue";
import CardView from "@/components/objects/CardView.vue";

export default {
    name: "ObjectsView",
    components: {
        Loading,
        BaseLayout,
        TableView,
        CardView
    },
    data() {
        return {
            activeTab: "",
            searchQuery: "",
            selectedAttribute: {},
            store: useMainStore(),
            isTableView: false,
            sortKey: "name",
            sortDirection: "asc",
            isMenuOpen: false // флаг для выпадающего меню
        };
    },
    computed: {
        objectTypes() {
            // Сортируем типы объектов по индексу
            return [...this.store.objectTypes].sort(
                (a, b) => a.params.index - b.params.index
            );
        },
        activeObjects() {
            return this.store.getObjectsByType(this.activeTab);
        },
        filteredObjects() {
            return this.activeObjects
                .filter((object) =>
                    object.name
                        .toLowerCase()
                        .includes(this.searchQuery.toLowerCase())
                )
                .sort((a, b) => a.name.localeCompare(b.name));
        },
        objectCounts() {
            const counts = {};
            this.objectTypes.forEach((type) => {
                counts[type.code] = this.store.getObjectsByType(type.code).length;
            });
            return counts;
        },
        groupingAttributes() {
            const activeType = this.store.getObjectTypeByCode(this.activeTab);
            return activeType
                ? activeType.available_attributes.filter((attr) => attr.show_off)
                : [];
        },
        groupedObjects() {
            if (!this.selectedAttribute.code) return null;

            const groups = {};
            this.filteredObjects.forEach((object) => {
                const attributeValue = object.attributes[this.selectedAttribute.code];
                if (Array.isArray(attributeValue) && attributeValue.length > 0) {
                    attributeValue.forEach((val) => {
                        if (!groups[val]) groups[val] = [];
                        groups[val].push(object);
                    });
                } else {
                    const key = attributeValue || "Без группы";
                    if (!groups[key]) groups[key] = [];
                    groups[key].push(object);
                }
            });

            Object.keys(groups).forEach((groupKey) => {
                groups[groupKey].sort((a, b) => a.name.localeCompare(b.name));
            });

            return groups;
        },
        isLoading() {
            return this.store.isLoading;
        },
        tableAttributes() {
            const activeType = this.store.getObjectTypeByCode(this.activeTab);
            if (!activeType) return [];
            return activeType.available_attributes.filter((a) => a.show_off);
        },
        sortedObjects() {
            const sorted = [...this.filteredObjects];
            sorted.sort((a, b) => {
                let aVal =
                    this.sortKey === "name"
                        ? a.name
                        : a.attributes[this.sortKey];
                let bVal =
                    this.sortKey === "name"
                        ? b.name
                        : b.attributes[this.sortKey];

                if (typeof aVal === "number" && typeof bVal === "number") {
                    return this.sortDirection === "asc"
                        ? aVal - bVal
                        : bVal - aVal;
                }

                const aStr = String(aVal ?? "");
                const bStr = String(bVal ?? "");
                return this.sortDirection === "asc"
                    ? aStr.localeCompare(bStr)
                    : bStr.localeCompare(aStr);
            });
            return sorted;
        }
    },
    async created() {
        if (!this.store.objectTypes.length) {
            await this.store.loadObjects();
        }
        this.handleRouteChange();
    },
    watch: {
        "$route"(newRoute) {
            this.handleRouteChange(newRoute);
        },
        selectedAttribute() {
            this.searchQuery = "";
        }
    },
    methods: {
        handleRouteChange(newRoute = this.$route) {
            const pathTab = newRoute.path.replace("/", "");
            if (pathTab && this.activeTab !== pathTab) {
                this.activeTab = pathTab;
            } else if (!pathTab && this.objectTypes.length) {
                this.activeTab = this.objectTypes[0].code;
                this.$router.replace(`/${this.activeTab}`);
            }
        },
        selectTab(tabCode) {
            if (this.activeTab !== tabCode) {
                this.$router.push(`/${tabCode}`);
            }
            this.selectedAttribute = {};
        },
        createObject(typeCode) {
            this.$router.push(`/${typeCode}/create`);
        },
        toggleMenu() {
            this.isMenuOpen = !this.isMenuOpen;
        },
        selectGrouping(attribute) {
            this.selectedAttribute = attribute;
            this.isMenuOpen = false;
        }
    }
};
</script>

<style scoped>
.table-grouped-row td {
    background-color: #fafafa;
}
</style>