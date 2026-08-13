<template>
    <div>
        <!-- Если есть сгруппированные данные -->
        <div v-if="groupedData && Object.keys(groupedData).length">
            <div
                v-for="(objects, group) in groupedData"
                :key="group"
                class="group-table-section mb-4"
            >
                <h5 class="fw-bold d-flex align-items-center mb-3">
                    <span class="me-2">{{ groupingAttribute?.name }}: {{ formatGroupingLabel(group, groupingAttribute) }}</span>
                    <span class="badge bg-secondary rounded-pill py-1 px-2"
                          style="font-size: 0.75rem;">{{ groupCounts[group] || objects.length }}</span>
                </h5>


                <div class="table-responsive object-table-surface">
                <table class="table table-hover align-middle object-table">
                    <thead>
                    <tr>
                        <!-- Колонка "Имя" -->
                        <th class="table-sortable" tabindex="0" @click="onSort('name')" @keydown.enter="onSort('name')">
                            <span class="underline">Имя</span>
                            <span v-if="sortKey === 'name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                        </th>
                        <!-- Перебираем остальные атрибуты -->
                        <th
                            v-for="attr in attributes"
                            :key="attr.code"
                            class="table-sortable"
                            tabindex="0"
                            @click="onSort(attr.code)"
                            @keydown.enter="onSort(attr.code)"
                        >
                            <span class="underline">{{ attr.name }}</span>
                            <span v-if="sortKey === attr.code">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </span>
                        </th>
                        <!-- Столбец для кнопки свернуть/развернуть -->
                        <th class="text-end" style="width: 40px;">
                            <button
                                class="btn btn-sm btn-outline-secondary icon-button"
                                @click="toggleCollapse"
                                :aria-label="isCollapsed ? 'Развернуть таблицу' : 'Свернуть таблицу'"
                                :title="isCollapsed ? 'Развернуть' : 'Свернуть'"
                            >
                                <i v-if="isCollapsed" class="bi bi-chevron-down"></i>
                                <i v-else class="bi bi-chevron-up"></i>
                            </button>
                        </th>
                    </tr>
                    </thead>
                    <!-- Тело таблицы скрывается/открывается при свёртывании -->
                    <tbody v-show="!isCollapsed">
                    <tr
                        v-for="object in sortData(objects)"
                        :key="object.id" :class="{'table-warning': !object.is_approved}"
                    >
                        <td>
                            <router-link :to="`/${object.type}/${object.id}`" class="fw-medium text-decoration-none">
                                {{ object.name }}
                            </router-link>
                        </td>
                        <td
                            v-for="attr in attributes"
                            :key="attr.code"
                        >
                            {{ formatValue(object.attributes[attr.code]) }}

                        </td>
                        <!-- Ячейка с иконкой-ссылкой справа -->
                        <td class="text-end">
                            <router-link :to="`/${object.type}/${object.id}`" :aria-label="`Открыть ${object.name}`" title="Открыть запись">
                                <i class="bi bi-link-45deg text-primary"></i>
                            </router-link>
                        </td>
                    </tr>
                    </tbody>
                </table>
                </div>
            </div>
        </div>

        <!-- Если обычный массив объектов (не сгруппировано) -->
        <div v-else-if="data.length" class="table-responsive object-table-surface">
            <table class="table table-hover align-middle object-table">
                <thead>
                <tr>
                    <th class="table-sortable" tabindex="0" @click="onSort('name')" @keydown.enter="onSort('name')">
                        <span class="underline">Имя</span>
                        <span class="ms-1" v-if="sortKey === 'name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                    </th>
                    <th
                        v-for="attr in attributes"
                        :key="attr.code"
                        class="table-sortable"
                        tabindex="0"
                        @click="onSort(attr.code)"
                        @keydown.enter="onSort(attr.code)"
                    >
                        <span class="underline">{{ attr.name }}</span>
                        <span class="ms-1" v-if="sortKey === attr.code">
                {{ sortDirection === 'asc' ? '▲' : '▼' }}
              </span>
                    </th>
                    <th class="text-end" style="width: 40px;">
                        <button
                            class="btn btn-sm btn-outline-secondary icon-button"
                            @click="toggleCollapse"
                            :aria-label="isCollapsed ? 'Развернуть таблицу' : 'Свернуть таблицу'"
                            :title="isCollapsed ? 'Развернуть' : 'Свернуть'"
                        >
                            <i v-if="isCollapsed" class="bi bi-chevron-down"></i>
                            <i v-else class="bi bi-chevron-up"></i>
                        </button>
                    </th>
                </tr>
                </thead>
                <tbody v-show="!isCollapsed">
                <tr
                    v-for="object in sortData(data)"
                    :key="object.id"  :class="{'table-warning': !object.is_approved}"
                >
                    <td>
                        <router-link :to="`/${object.type}/${object.id}`" class="fw-medium text-decoration-none">
                            {{ object.name }}
                        </router-link>
                    </td>
                    <td
                        v-for="attr in attributes"
                        :key="attr.code"
                    >
                        {{ formatValue(object.attributes[attr.code]) }}
                    </td>
                    <td class="text-end">
                        <router-link :to="`/${object.type}/${object.id}`" :aria-label="`Открыть ${object.name}`" title="Открыть запись">
                            <i class="bi bi-link-45deg text-primary"></i>
                        </router-link>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <!-- Если данных нет -->
        <EmptyState
            v-else
            title="Записей пока нет"
            description="Измените фильтры или создайте первую запись этого типа."
            icon="bi-table"
        />
    </div>
</template>

<script>
import {formatValue} from "../../utils/helpers.js";
import EmptyState from "@/components/common/EmptyState.vue";
import {groupingLabel} from "@/utils/objectGrouping.js";

export default {
    name: "TableView",
    components: {EmptyState},

    // Убрали sortKey/sortDirection из пропсов, так как управляем локально
    props: {
        data: {type: Array, required: true},
        groupedData: {type: Object, default: null},
        groupCounts: {type: Object, default: () => ({})},
        attributes: {type: Array, required: true},
        groupingAttribute: {type: Object, default: null}
    },

    data() {
        return {
            isCollapsed: false,
            // Вводим локальные поля для сортировки
            sortKey: "name",
            sortDirection: "asc"
        };
    },

    // Исходные события тоже не нужны, так как не передаём наружу
    // emits: ["update:sortKey", "update:sortDirection"],

    methods: {
        formatValue,
        formatGroupingLabel: groupingLabel,
        toggleCollapse() {
            this.isCollapsed = !this.isCollapsed;
        },
        onSort(key) {
            if (this.sortKey === key) {
                // Меняем направление, если кликнули по тому же столбцу
                this.sortDirection =
                    this.sortDirection === "asc" ? "desc" : "asc";
            } else {
                // Сбрасываем сортировку на "asc" при выборе нового столбца
                this.sortKey = key;
                this.sortDirection = "asc";
            }
        },
        sortData(objects) {
            const sorted = [...objects];

            sorted.sort((a, b) => {
                // Извлекаем исходные значения
                let aVal = this.sortKey === "name" ? a.name : a.attributes[this.sortKey];
                let bVal = this.sortKey === "name" ? b.name : b.attributes[this.sortKey];

                // Пробуем преобразовать к числу
                const aNum = Number(aVal);
                const bNum = Number(bVal);

                // Если оба значения корректно преобразовались в числа (не NaN)
                if (!Number.isNaN(aNum) && !Number.isNaN(bNum)) {
                    return this.sortDirection === "asc" ? aNum - bNum : bNum - aNum;
                }

                // Иначе сравниваем как строки
                const aStr = String(aVal ?? "");
                const bStr = String(bVal ?? "");
                return this.sortDirection === "asc"
                    ? aStr.localeCompare(bStr)
                    : bStr.localeCompare(aStr);
            });

            return sorted;
        }

    }
};
</script>

<style scoped>
.group-table-section {
    min-width: 0;
}

.underline {
    text-decoration: none;
}

.object-table-surface {
    overflow-y: hidden;
    border: 1px solid var(--silaeder-border);
    border-radius: 0.75rem;
    background: var(--silaeder-surface);
    box-shadow: var(--silaeder-shadow-sm);
}

.object-table {
    --bs-table-bg: transparent;
    --bs-table-border-color: var(--silaeder-border);
    --bs-table-hover-bg: var(--silaeder-primary-soft);
    min-width: 34rem;
    margin-bottom: 0;
}

.object-table thead th {
    padding: 0.7rem 0.9rem;
    color: var(--silaeder-muted);
    font-size: 0.78rem;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: 0.015em;
    white-space: nowrap;
    border-bottom-width: 1px;
    background: #f8fafb;
}

.object-table tbody td {
    padding: 0.75rem 0.9rem;
    color: var(--silaeder-text);
    line-height: 1.35;
    vertical-align: middle;
}

.object-table tbody tr:last-child td {
    border-bottom: 0;
}

.object-table tbody tr {
    transition: background-color 140ms ease;
}

.object-table tbody tr.table-warning > * {
    --bs-table-bg-state: #fff7da;
}

.object-table a:not(.btn) {
    color: var(--silaeder-primary-dark);
}

.table-sortable {
    cursor: pointer;
    transition: color 140ms ease, background-color 140ms ease;
}

.table-sortable:hover {
    color: var(--silaeder-primary-dark);
    background: var(--silaeder-primary-soft);
}

.table-sortable:focus-visible {
    outline: 0;
    box-shadow: inset 0 0 0 2px rgb(57 118 152 / 22%);
}

@media (max-width: 575.98px) {
    .object-table {
        min-width: 30rem;
    }

    .object-table thead th,
    .object-table tbody td {
        padding-right: 0.75rem;
        padding-left: 0.75rem;
    }
}
</style>
