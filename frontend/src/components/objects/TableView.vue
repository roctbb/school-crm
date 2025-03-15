<template>
    <div>
        <!-- Если есть сгруппированные данные -->
        <div v-if="groupedData && Object.keys(groupedData).length">
            <div
                v-for="(objects, group) in groupedData"
                :key="group"
                class="mb-4"
            >
                <h5 class="fw-bold pb-2">
                    {{ groupingAttribute?.name }}: {{ group }}
                </h5>
                <table class="table table-sm table-bordered table-hover align-middle">
                    <thead class="table-light">
                    <tr>
                        <!-- Колонка "Имя" -->
                        <th @click="onSort('name')">
                            <span class="underline">Имя</span>
                            <span v-if="sortKey === 'name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                        </th>
                        <!-- Перебираем остальные атрибуты -->
                        <th
                            v-for="attr in attributes"
                            :key="attr.code"
                            @click="onSort(attr.code)"
                        >
                            <span class="underline">{{ attr.name }}</span>
                            <span v-if="sortKey === attr.code">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </span>
                        </th>
                        <!-- Столбец для кнопки свернуть/развернуть -->
                        <th class="text-end" style="width: 40px;">
                            <button
                                class="btn btn-sm btn-outline-secondary"
                                @click="toggleCollapse"
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
                        :key="object.id"
                    >
                        <td>{{ object.name }}</td>
                        <td
                            v-for="attr in attributes"
                            :key="attr.code"
                        >
                            {{ formatValue(object.attributes[attr.code]) }}

                        </td>
                        <!-- Ячейка с иконкой-ссылкой справа -->
                        <td class="text-end">
                            <router-link :to="`/${object.type}/${object.id}`">
                                <i class="bi bi-link-45deg text-primary"></i>
                            </router-link>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Если обычный массив объектов (не сгруппировано) -->
        <div v-else-if="data.length" class="table-responsive">
            <table class="table table-sm table-bordered table-hover align-middle">
                <thead class="table-light">
                <tr>
                    <th @click="onSort('name')">
                        <span class="underline">Имя</span>
                        <span class="ms-1" v-if="sortKey === 'name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
                    </th>
                    <th
                        v-for="attr in attributes"
                        :key="attr.code"
                        @click="onSort(attr.code)"
                    >
                        <span class="underline">{{ attr.name }}</span>
                        <span class="ms-1" v-if="sortKey === attr.code">
                {{ sortDirection === 'asc' ? '▲' : '▼' }}
              </span>
                    </th>
                    <th class="text-end" style="width: 40px;">
                        <button
                            class="btn btn-sm btn-outline-secondary"
                            @click="toggleCollapse"
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
                    :key="object.id"
                >
                    <td>{{ object.name }}</td>
                    <td
                        v-for="attr in attributes"
                        :key="attr.code"
                    >
                        {{ formatValue(object.attributes[attr.code]) }}
                    </td>
                    <td class="text-end">
                        <router-link :to="`/${object.type}/${object.id}`">
                            <i class="bi bi-link-45deg text-primary"></i>
                        </router-link>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>

        <!-- Если данных нет -->
        <div v-else>
            <p class="text-center">Объекты отсутствуют для данного типа.</p>
        </div>
    </div>
</template>

<script>
import {formatValue} from "../../utils/helpers.js";

export default {
    name: "TableView",

    // Убрали sortKey/sortDirection из пропсов, так как управляем локально
    props: {
        data: {type: Array, required: true},
        groupedData: {type: Object, default: null},
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
.underline {
    text-decoration: underline;
}
</style>