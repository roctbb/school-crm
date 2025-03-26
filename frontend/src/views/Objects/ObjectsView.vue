<template>
    <BaseLayout>
        <!-- Навигация по вкладкам -->
        <div class="d-flex align-items-center justify-content-between border-bottom mt-3">
            <TabNavigation
                :tabs="objectTypesWithPortfolio"
                :active-tab="activeTab"
                :object-counts="objectCounts"
                :has-teacher-access="hasTeacherAccess()"
                :hasUnconfirmed="hasUnconfirmed"
                @tab-selected="selectTab"
            />

            <!-- Область создания объектов -->
            <CreateObjectArea
                :active-tab="activeTab"
                :store="store"
                :canCreateByType="canCreateByType"
                @createObject="createObject"
            />
        </div>

        <!-- Если выбрана вкладка "portfolio" -->
        <div v-if="activeTab === 'portfolio'" class="tab-content">
            <div class="mt-3">
                <loading v-if="isLoading"/>
                <div v-else>
                    <CardView
                        :objects="portfolioObjects"
                        size="big"
                    />
                </div>
            </div>
        </div>

        <!-- Если выбрана любая другая вкладка -->
        <div v-if="activeTab !== 'portfolio'" class="tab-content">
            <!-- Панель фильтров, если вкладка действительно выбрана -->
            <ListWidgetBar
                v-if="activeTab"
                :type="store.getObjectTypeByCode(activeTab)"
            />

            <!-- Поиск и выпадающее меню группировки -->
            <div class="d-flex mt-3 align-items-center">
                <input
                    type="text"
                    class="form-control form-control-sm me-1"
                    placeholder="Введите текст для поиска..."
                    v-model="searchQuery"
                />
                <!-- Кнопка -->
                <div class="dropdown" :class="{ show: isMenuOpen }">
                    <button
                        class="btn btn-sm btn-outline-secondary dropdown-toggle me-1"
                        type="button"
                        @click="toggleMenu"
                        :class="{ show: isMenuOpen }"
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


                <!-- Кнопка переключения вида (таблица/карточки) -->
                <button
                    class="btn btn-outline-secondary btn-sm"
                    @click="toggleTableView()"
                >
                    <i
                        v-if="isTableView"
                        class="bi bi-grid"
                    ></i>
                    <i
                        v-else
                        class="bi bi-list"
                    ></i>
                </button>

                <!-- Кнопка для преподавателей: фильтр неподтверждённых (иконки) -->
                <button
                    v-if="hasTeacherAccess()"
                    class="btn btn-outline-secondary btn-sm ms-1 position-relative"
                    @click="toggleUnconfirmed"
                >
                    <i
                        v-if="onlyUnconfirmed"
                        class="bi bi-clipboard-check"
                        title="Показать все"
                    ></i>
                    <i
                        v-else
                        class="bi bi-exclamation-circle"
                        title="Только неподтверждённые"
                    ></i>

                    <!-- Сам кружочек -->
                    <span
                        v-if="nonConfirmedObjects.length"
                        class="position-absolute top-0 start-100 translate-middle p-1 bg-warning border border-light rounded-circle"
                        style="width: 0.8rem; height: 0.8rem"
                    ></span>
                </button>

            </div>

            <!-- Содержимое вкладки -->
            <div class="mt-3">
                <loading v-if="isLoading"/>
                <div v-else>
                    <TableView
                        v-if="isTableView"
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
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import TableView from "@/components/objects/TableView.vue";
import CardView from "@/components/objects/CardView.vue";
import ListWidgetBar from "@/components/objects/ListWidgetBar.vue";

// Новые компоненты
import TabNavigation from "@/components/objects/TabNavigation.vue";
import CreateObjectArea from "@/components/objects/CreateObjectArea.vue";

import {canCreateByType, hasTeacherAccess} from "@/utils/access.js";

export default {
    name: "ObjectsView",

    props: {
        objectTypeCode: {
            type: String,
            default: "",
        },
        view: {
            type: String,
            default: "cards",
        },
        grouping: {
            type: String,
            default: "",
        },
        search: {
            type: String,
            default: "",
        },
        unconfirmed: {
            type: Boolean,
            default: false,
        },
    },

    components: {
        BaseLayout,
        Loading,
        TableView,
        CardView,
        ListWidgetBar,
        TabNavigation,
        CreateObjectArea,
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
            isMenuOpen: false,
            onlyUnconfirmed: false,
        };
    },

    computed: {
        portfolioObjects() {
            const userId = this.store.profile?.id;
            if (!userId || hasTeacherAccess()) return [];
            return this.store.allObjects().filter((obj) =>
                obj.owners.some((owner) => owner.id === userId)
            );
        },
        objectTypesWithPortfolio() {
            const sortedTypes = [...this.store.objectTypes].sort(
                (a, b) => a.params.index - b.params.index
            );
            if (this.portfolioObjects.length > 0) {
                return [{code: "portfolio", name: "Мое портфолио"}, ...sortedTypes];
            }
            return sortedTypes;
        },
        objectCounts() {
            const counts = {};
            this.store.objectTypes.forEach((type) => {
                counts[type.code] = this.store.getObjectsByType(type.code).length;
            });
            if (this.portfolioObjects.length > 0) {
                counts["portfolio"] = this.portfolioObjects.length;
            }
            return counts;
        },
        activeObjects() {
            if (this.activeTab === "portfolio") {
                return this.portfolioObjects;
            }
            return this.store.getObjectsByType(this.activeTab).filter(
                (obj) => !this.onlyUnconfirmed || obj.isNotApproved()
            );
        },
        nonConfirmedObjects() {
            return this.store
                .getObjectsByType(this.activeTab)
                .filter((obj) => obj.isNotApproved());
        },
        filteredObjects() {
            let result = this.activeObjects
                .filter((obj) =>
                    obj.name.toLowerCase().includes(this.searchQuery.toLowerCase())
                )
                .sort((a, b) => a.name.localeCompare(b.name));

            if (this.onlyUnconfirmed) {
                result = result.filter((obj) => !obj.isConfirmed);
            }
            return result;
        },
        groupingAttributes() {
            const activeType = this.store.getObjectTypeByCode(this.activeTab);
            return activeType
                ? activeType.available_attributes.filter((attr) => attr.group)
                : [];
        },
        groupedObjects() {
            if (!this.selectedAttribute.code) return null;
            const groups = {};
            this.filteredObjects.forEach((obj) => {
                const attributeValue = obj.attributes[this.selectedAttribute.code];
                if (Array.isArray(attributeValue) && attributeValue.length > 0) {
                    attributeValue.forEach((val) => {
                        if (!groups[val]) groups[val] = [];
                        groups[val].push(obj);
                    });
                } else {
                    const key = attributeValue || "Без группы";
                    if (!groups[key]) groups[key] = [];
                    groups[key].push(obj);
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
                let aVal = this.sortKey === "name" ? a.name : a.attributes[this.sortKey];
                let bVal = this.sortKey === "name" ? b.name : b.attributes[this.sortKey];

                if (typeof aVal === "number" && typeof bVal === "number") {
                    return this.sortDirection === "asc" ? aVal - bVal : bVal - aVal;
                }
                const aStr = String(aVal ?? "");
                const bStr = String(bVal ?? "");
                return this.sortDirection === "asc"
                    ? aStr.localeCompare(bStr)
                    : bStr.localeCompare(aStr);
            });
            return sorted;
        },
    },

    async created() {
        if (!this.store.objectTypes.length) {
            await this.store.loadObjects();
        }

        if (this.objectTypeCode) {
            this.activeTab = this.objectTypeCode;
        } else if (this.objectTypesWithPortfolio.length) {
            this.activeTab = this.objectTypesWithPortfolio[0].code;
            this.$router.replace(`/${this.activeTab}`);
        }

        this.isTableView = this.view === "table";
        this.searchQuery = this.search;
        this.onlyUnconfirmed = this.unconfirmed;
    },

    watch: {
        objectTypeCode(newVal) {
            if (newVal && newVal !== this.activeTab) {
                this.activeTab = newVal;
            }
        },
        view(newVal) {
            this.isTableView = newVal === "table";
        },
        search(newVal) {
            this.searchQuery = newVal;
        },
        unconfirmed(newVal) {
            this.onlyUnconfirmed = newVal;
        },
        selectedAttribute() {
            // При смене группировки сбрасываем поиск
            this.searchQuery = "";
        },
    },

    methods: {
        canCreateByType,
        hasTeacherAccess,

        selectTab(tabCode) {
            if (this.activeTab !== tabCode) {
                this.$router.push({
                    path: `/${tabCode}`,
                    query: {
                        view: this.isTableView ? "table" : "cards",
                        search: this.searchQuery,
                        grouping: this.selectedAttribute?.code || "",
                        unconfirmed: String(this.onlyUnconfirmed),
                    },
                });
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
            this.updatePath();
        },
        hasUnconfirmed(typeCode) {
            const objects = this.store.getObjectsByType(typeCode);
            return objects.some((obj) => obj.isNotApproved());
        },
        toggleUnconfirmed() {
            this.onlyUnconfirmed = !this.onlyUnconfirmed;
            this.updatePath();
        },
        toggleTableView() {
            this.isTableView = !this.isTableView;
            this.updatePath();
        },
        updatePath() {
            this.$router.push({
                path: `/${this.activeTab}`,
                query: {
                    view: this.isTableView ? "table" : "cards",
                    search: this.searchQuery,
                    grouping: this.selectedAttribute?.code || "",
                    unconfirmed: String(this.onlyUnconfirmed),
                },
            });
        },
    },
};
</script>

<style scoped>
.tab-content {
    padding: 1rem;
    border: 1px solid #dee2e6;
    border-top: none;
}

/* Анимация плавного появления и исчезновения контента */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
}

/* Анимация выезда меню сверху вниз */
.menu-slide-enter-active,
.menu-slide-leave-active {
    transition: all 0.3s ease;
}

.menu-slide-enter {
    opacity: 0;
    transform: translateY(-10px);
}

.menu-slide-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}
</style>