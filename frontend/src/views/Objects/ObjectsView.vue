<template>
    <BaseLayout>
        <!-- Навигация по вкладкам -->
        <div class="objects-tabs-bar d-flex flex-wrap align-items-end justify-content-between gap-2">
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
                        :objects="paginatedObjects"
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
            <div class="page-toolbar objects-toolbar mt-3">
                <div class="input-group input-group-sm toolbar-search flex-grow-1">
                    <span class="input-group-text bg-white text-muted" aria-hidden="true">
                        <i class="bi bi-search"></i>
                    </span>
                    <input
                        type="search"
                        class="form-control"
                        placeholder="Поиск по названию…"
                        aria-label="Поиск по названию"
                        v-model="searchQuery"
                    />
                    <button
                        v-if="searchQuery"
                        class="btn btn-light icon-button"
                        type="button"
                        aria-label="Очистить поиск"
                        title="Очистить поиск"
                        @click="searchQuery = ''"
                    >
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <!-- Кнопка -->
                <div class="dropdown" :class="{ show: isMenuOpen }">
                    <button
                        class="btn btn-sm btn-outline-secondary dropdown-toggle"
                        type="button"
                        @click="toggleMenu"
                        :class="{ show: isMenuOpen }"
                        aria-label="Выбрать группировку"
                        title="Группировка"
                    >
                        <i class="bi bi-collection me-sm-1"></i>
                        <span class="d-none d-sm-inline">{{ selectedAttribute.name || 'Группировка' }}</span>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end" :class="{ 'show': isMenuOpen }">
                        <li>
                            <button
                                class="dropdown-item"
                                type="button"
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
                                type="button"
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
                    class="btn btn-outline-secondary btn-sm icon-button"
                    type="button"
                    @click="toggleTableView()"
                    :aria-label="isTableView ? 'Показать карточками' : 'Показать таблицей'"
                    :title="isTableView ? 'Карточки' : 'Таблица'"
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
                    class="btn btn-sm icon-button position-relative"
                    :class="onlyUnconfirmed ? 'btn-warning' : 'btn-outline-secondary'"
                    type="button"
                    @click="toggleUnconfirmed"
                    :aria-pressed="onlyUnconfirmed"
                    :aria-label="onlyUnconfirmed ? 'Показать все записи' : 'Показать только неподтверждённые'"
                    :title="onlyUnconfirmed ? 'Показать все' : 'Только неподтверждённые'"
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

                <button
                    v-if="hasActiveFilters"
                    class="btn btn-sm btn-link text-secondary text-decoration-none ms-auto ms-sm-0"
                    type="button"
                    @click="resetFilters"
                >
                    Сбросить
                </button>

            </div>

            <!-- Содержимое вкладки -->
            <div class="objects-results">
                <loading v-if="isLoading"/>
                <div v-else>
                    <TableView
                        v-if="isTableView"
                        :data="paginatedSortedObjects"
                        :grouped-data="paginatedGroupedObjects"
                        :group-counts="groupCounts"
                        :attributes="tableAttributes"
                        :grouping-attribute="selectedAttribute"
                        :sortKey.sync="sortKey"
                        :sortDirection.sync="sortDirection"
                    />
                    <CardView
                        v-else
                        :objects="paginatedObjects"
                        :grouped-data="paginatedGroupedObjects"
                        :group-counts="groupCounts"
                        :object-type="store.getObjectTypeByCode(activeTab)"
                        :grouping-attribute="selectedAttribute"
                        size="big"
                    />
                </div>
            </div>
        </div>

        <PaginationControls
            v-if="!isLoading"
            :current-page="currentPage"
            :page-size="pageSize"
            :total-items="paginationTotalItems"
            @page-selected="selectPage"
        />
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
import PaginationControls from "@/components/common/PaginationControls.vue";

import {canCreateByType, hasTeacherAccess} from "@/utils/access.js";
import {
    buildGroupingOptions,
    compareGroupedObjects,
    compareGroupingKeys,
    groupingKey,
} from "@/utils/objectGrouping.js";

const NO_GROUPING_QUERY_VALUE = "__none__";

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
        groupingSpecified: {
            type: Boolean,
            default: false,
        },
        search: {
            type: String,
            default: "",
        },
        unconfirmed: {
            type: Boolean,
            default: false,
        },
        page: {
            type: Number,
            default: 1,
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
        PaginationControls,
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
            currentPage: 1,
            pageSize: 48,
            searchUpdateTimer: null,
            isInitializing: true,
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

            return result;
        },
        groupingAttributes() {
            const activeType = this.store.getObjectTypeByCode(this.activeTab);
            return buildGroupingOptions(activeType?.available_attributes);
        },
        groupedObjects() {
            if (!this.selectedAttribute.code) return null;
            const groups = {};
            this.filteredObjects.forEach((obj) => {
                const attributeCode = this.selectedAttribute.sourceCode || this.selectedAttribute.code;
                const attributeValue = obj.attributes[attributeCode];
                if (Array.isArray(attributeValue) && attributeValue.length > 0) {
                    attributeValue.forEach((val) => {
                        const key = groupingKey(val, this.selectedAttribute);
                        if (!groups[key]) groups[key] = [];
                        groups[key].push(obj);
                    });
                } else {
                    const key = groupingKey(attributeValue, this.selectedAttribute);
                    if (!groups[key]) groups[key] = [];
                    groups[key].push(obj);
                }
            });
            Object.keys(groups).forEach((groupKey) => {
                groups[groupKey].sort((a, b) => compareGroupedObjects(a, b, this.selectedAttribute));
            });
            return Object.fromEntries(
                Object.entries(groups).sort(([a], [b]) => compareGroupingKeys(a, b, this.selectedAttribute))
            );
        },
        groupedEntries() {
            if (!this.groupedObjects) return [];
            return Object.entries(this.groupedObjects).flatMap(([group, objects]) =>
                objects.map(object => ({group, object}))
            );
        },
        groupCounts() {
            if (!this.groupedObjects) return {};
            return Object.fromEntries(
                Object.entries(this.groupedObjects).map(([group, objects]) => [group, objects.length])
            );
        },
        paginatedGroupedObjects() {
            if (!this.groupedObjects) return null;
            const start = (this.currentPage - 1) * this.pageSize;
            return this.groupedEntries
                .slice(start, start + this.pageSize)
                .reduce((groups, {group, object}) => {
                    if (!groups[group]) groups[group] = [];
                    groups[group].push(object);
                    return groups;
                }, {});
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
        totalPages() {
            return Math.max(1, Math.ceil(this.paginationTotalItems / this.pageSize));
        },
        paginationTotalItems() {
            return this.selectedAttribute.code ? this.groupedEntries.length : this.filteredObjects.length;
        },
        paginatedObjects() {
            const start = (this.currentPage - 1) * this.pageSize;
            return this.filteredObjects.slice(start, start + this.pageSize);
        },
        paginatedSortedObjects() {
            const start = (this.currentPage - 1) * this.pageSize;
            return this.sortedObjects.slice(start, start + this.pageSize);
        },
        hasActiveFilters() {
            return Boolean(this.searchQuery || this.selectedAttribute.code || this.onlyUnconfirmed);
        },
    },

    async created() {
        if (!this.store.objectTypes.length) {
            await this.store.loadObjects();
        }

        this.isTableView = this.view === "table";
        this.searchQuery = this.search;
        this.onlyUnconfirmed = this.unconfirmed;
        this.currentPage = this.page;

        let shouldNormalizePath = false;
        if (this.objectTypeCode) {
            this.activeTab = this.objectTypeCode;
        } else if (this.objectTypesWithPortfolio.length) {
            this.activeTab = this.objectTypesWithPortfolio[0].code;
            this.currentPage = 1;
            shouldNormalizePath = true;
        }

        this.syncGrouping(this.groupingSpecified ? this.grouping : this.defaultGroupingCode());
        this.currentPage = Math.min(this.currentPage, this.totalPages);
        this.isInitializing = false;

        if (this.activeTab && (shouldNormalizePath || !this.groupingSpecified)) {
            await this.updatePath({replace: true});
        }
    },

    beforeUnmount() {
        window.clearTimeout(this.searchUpdateTimer);
        document.removeEventListener("click", this.handleOutsideMenu);
    },

    mounted() {
        document.addEventListener("click", this.handleOutsideMenu);
    },

    watch: {
        async objectTypeCode(newVal) {
            if (newVal) {
                this.activeTab = newVal;
                this.currentPage = this.page;
                this.syncGrouping(this.groupingSpecified ? this.grouping : this.defaultGroupingCode());
            } else if (!this.isInitializing) {
                await this.openDefaultTab();
            }
        },
        view(newVal) {
            this.isTableView = newVal === "table";
        },
        search(newVal) {
            if (newVal !== this.searchQuery) this.searchQuery = newVal;
        },
        unconfirmed(newVal) {
            this.onlyUnconfirmed = newVal;
        },
        grouping(newVal) {
            this.syncGrouping(this.groupingSpecified ? newVal : this.defaultGroupingCode());
        },
        groupingSpecified(newVal) {
            if (!this.isInitializing) {
                this.syncGrouping(newVal ? this.grouping : this.defaultGroupingCode());
            }
        },
        page(newVal) {
            this.currentPage = Math.max(1, newVal);
        },
        searchQuery(newVal, oldVal) {
            if (this.isInitializing || newVal === oldVal || newVal === this.search) return;
            this.currentPage = 1;
            window.clearTimeout(this.searchUpdateTimer);
            this.searchUpdateTimer = window.setTimeout(() => {
                this.updatePath({replace: true});
            }, 300);
        },
        totalPages(newVal) {
            if (this.currentPage > newVal) {
                this.currentPage = newVal;
                if (!this.isInitializing) this.updatePath({replace: true});
            }
        },
    },

    methods: {
        canCreateByType,
        hasTeacherAccess,

        async selectTab(tabCode) {
            if (this.activeTab === tabCode) return;

            this.activeTab = tabCode;
            this.syncGrouping(this.defaultGroupingCode());
            this.currentPage = 1;
            await this.updatePath();
        },
        createObject(typeCode) {
            this.$router.push(`/${typeCode}/create`);
        },
        toggleMenu() {
            this.isMenuOpen = !this.isMenuOpen;
        },
        handleOutsideMenu(event) {
            if (!this.isMenuOpen || event.target.closest(".page-toolbar .dropdown")) return;
            this.isMenuOpen = false;
        },
        selectGrouping(attribute) {
            this.selectedAttribute = attribute;
            this.isMenuOpen = false;
            this.currentPage = 1;
            this.updatePath();
        },
        hasUnconfirmed(typeCode) {
            const objects = this.store.getObjectsByType(typeCode);
            return objects.some((obj) => obj.isNotApproved());
        },
        toggleUnconfirmed() {
            this.onlyUnconfirmed = !this.onlyUnconfirmed;
            this.currentPage = 1;
            this.updatePath();
        },
        toggleTableView() {
            this.isTableView = !this.isTableView;
            this.currentPage = 1;
            this.updatePath();
        },
        resetFilters() {
            this.searchQuery = "";
            this.selectedAttribute = {};
            this.onlyUnconfirmed = false;
            this.currentPage = 1;
            window.clearTimeout(this.searchUpdateTimer);
            this.updatePath({replace: true});
        },
        routeQuery() {
            return {
                view: this.isTableView ? "table" : "cards",
                search: this.searchQuery,
                grouping: this.selectedAttribute?.code || NO_GROUPING_QUERY_VALUE,
                unconfirmed: String(this.onlyUnconfirmed),
                page: String(this.currentPage),
            };
        },
        async updatePath({replace = false} = {}) {
            if (!this.activeTab) return;

            const location = {
                name: "ObjectType",
                params: {object_type: this.activeTab},
                query: this.routeQuery(),
            };
            if (this.$router.resolve(location).fullPath === this.$route.fullPath) return;
            await this.$router[replace ? "replace" : "push"](location);
        },
        async openDefaultTab() {
            const defaultTab = this.objectTypesWithPortfolio[0]?.code;
            if (!defaultTab) return;

            this.activeTab = defaultTab;
            this.syncGrouping(this.groupingSpecified ? this.grouping : this.defaultGroupingCode());
            this.currentPage = 1;
            await this.updatePath({replace: true});
        },
        defaultGroupingCode() {
            return this.store.getObjectTypeByCode(this.activeTab)?.params?.default_grouping || "";
        },
        syncGrouping(groupingCode) {
            this.selectedAttribute = this.groupingAttributes.find(
                attribute => attribute.code === groupingCode
            ) || {};
        },
        async selectPage(pageNumber) {
            const nextPage = Math.min(Math.max(1, pageNumber), this.totalPages);
            if (nextPage === this.currentPage) return;

            this.currentPage = nextPage;
            await this.updatePath();
            window.scrollTo({top: 0, behavior: "smooth"});
        },
    },
};
</script>

<style scoped>
.objects-tabs-bar {
    margin-top: 0.25rem;
    padding: 0.4rem 0 0.7rem;
    border-bottom: 1px solid var(--silaeder-border);
}

.tab-content {
    padding-top: 0.35rem;
}

.objects-toolbar {
    padding: 0.75rem;
    margin-bottom: 1.25rem;
}

.objects-results {
    margin-top: 0;
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
@media (max-width: 575.98px) {
    .objects-tabs-bar {
        align-items: center !important;
        padding-bottom: 0.6rem;
    }

    .objects-toolbar {
        padding: 0.65rem;
    }
}
</style>
