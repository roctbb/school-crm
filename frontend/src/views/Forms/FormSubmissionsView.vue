<template>
    <BaseLayout>
        <div class="container mt-3">
            <loading v-if="isLoading"/>
            <div v-else>
                <h3 class="mb-4">Ответы на форму: {{ form.name }}</h3>

                <!-- Глобальный фильтр по имени объекта -->
                <div class="mb-3">
                    <input
                        v-model="searchQuery"
                        type="text"
                        class="form-control"
                        placeholder="Глобальный фильтр по имени объекта"
                    />
                </div>

                <!-- Сгруппированные ответы по типу объекта -->
                <div
                    v-for="(submissions, objectType) in groupedSubmissions"
                    :key="objectType"
                    class="mb-5"
                >
                    <div class="d-flex align-items-center mb-2">
                        <h4 class="mb-0">
                            {{ objectType === "Без объекта"
                            ? "Объекты без типа"
                            : ("Тип объекта: " + objectType) }}
                        </h4>
                        <button
                            class="btn btn-sm btn-secondary ms-auto"
                            @click="exportFilteredSubmissionsToExcel"
                        >
                            <i class="bi bi-download me-1"></i> Выгрузить
                        </button>
                    </div>

                    <table class="table table-bordered table-striped table-hover align-middle">
                        <thead>
                        <tr>
                            <th @click="changeSort('id')" style="cursor: pointer">
                                ID
                                <span v-if="isColumnSorted('id')">
                    {{ getSortDirection('id') === 'asc' ? '↑' : '↓' }}
                  </span>
                            </th>
                            <th @click="changeSort('object_name')" style="cursor: pointer">
                                Объект
                                <span v-if="isColumnSorted('object_name')">
                    {{ getSortDirection('object_name') === 'asc' ? '↑' : '↓' }}
                  </span>
                            </th>
                            <!-- Столбцы для атрибутов (используем имена атрибутов) -->
                            <th
                                v-for="attr in getAttributeColumns(submissions)"
                                :key="attr.code"
                                @click="changeSort('attr_' + attr.code)"
                                style="cursor: pointer"
                            >
                                {{ attr.name }}
                                <span v-if="isColumnSorted('attr_' + attr.code)">
                    {{ getSortDirection('attr_' + attr.code) === 'asc' ? '↑' : '↓' }}
                  </span>
                            </th>
                            <th @click="changeSort('created_at')" style="cursor: pointer">
                                Дата создания
                                <span v-if="isColumnSorted('created_at')">
                    {{ getSortDirection('created_at') === 'asc' ? '↑' : '↓' }}
                  </span>
                            </th>
                            <!-- Заголовки для полей формы -->
                            <th
                                v-for="field in form.fields"
                                :key="field.code"
                                @click="changeSort(field.code)"
                                style="cursor: pointer"
                            >
                                {{ field.name }}
                                <span v-if="isColumnSorted(field.code)">
                    {{ getSortDirection(field.code) === 'asc' ? '↑' : '↓' }}
                  </span>
                            </th>
                        </tr>

                        <!-- Строка фильтров для каждого столбца -->
                        <tr>
                            <th>
                                <input
                                    v-model="filters.id"
                                    type="text"
                                    class="form-control"
                                    placeholder="Фильтр по ID"
                                />
                            </th>
                            <th>
                                <input
                                    v-model="filters.objectName"
                                    type="text"
                                    class="form-control"
                                    placeholder="Фильтр по объекту"
                                />
                            </th>
                            <!-- Фильтры для атрибутов -->
                            <th
                                v-for="attr in getAttributeColumns(submissions)"
                                :key="attr.code"
                            >
                                <input
                                    v-model="filters['attr_' + attr.code]"
                                    type="text"
                                    class="form-control"
                                    :placeholder="`Фильтр по ${attr.name}`"
                                />
                            </th>
                            <th>
                                <input
                                    v-model="filters.createdAt"
                                    type="text"
                                    class="form-control"
                                    placeholder="Фильтр по дате"
                                />
                            </th>
                            <!-- Фильтры для полей формы -->
                            <th
                                v-for="field in form.fields"
                                :key="field.code"
                            >
                                <input
                                    v-model="filters[field.code]"
                                    type="text"
                                    class="form-control"
                                    :placeholder="`Фильтр по ${field.name}`"
                                />
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-if="submissions.length === 0">
                            <td
                                :colspan="
                    2 + getAttributeColumns(submissions).length + 1 + form.fields.length
                  "
                                class="text-center text-muted"
                            >
                                Нет результатов для отображения.
                            </td>
                        </tr>
                        <tr
                            v-for="submission in submissions"
                            :key="submission.id"
                            :class="{ 'table-warning': submission.is_approved === false }"
                        >
                            <td>
                                <router-link
                                    :to="{
                      name: 'SubmissionDetails',
                      params: {
                        object_type: submission.object?.type,
                        object_id: submission.object?.id,
                        submissionId: submission.id
                      }
                    }"
                                >
                                    {{ submission.id }}
                                </router-link>
                            </td>
                            <td>
                  <span v-if="submission.object">
                    <router-link
                        :to="{
                        name: 'ObjectDetails',
                        params: {
                          object_type: submission.object.type,
                          object_id: submission.object.id
                        }
                      }"
                    >
                      {{ submission.object.name }}
                    </router-link>
                  </span>
                                <span v-else>Без объекта</span>
                            </td>
                            <!-- Вывод столбцов атрибутов -->
                            <td
                                v-for="attr in getAttributeColumns(submissions)"
                                :key="attr.code"
                            >
                                {{ getAttributeValue(submission, attr.code) }}
                            </td>
                            <td>{{ formatDateTime(submission.created_at) }}</td>
                            <!-- Данные полей формы -->
                            <td
                                v-for="(field, i) in submission.fields"
                                :key="i"
                            >
                  <span v-if="Array.isArray(field.answer)">
                    {{ field.answer.join(', ') }}
                  </span>
                                <span v-else>
                    {{ field.answer }}
                  </span>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import {fetchFormSubmissions} from '@/api/forms_api.js';
import Loading from '@/components/common/Loading.vue';
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import useMainStore from '@/stores/mainStore.js';

// Подключаем библиотеки xlsx и file-saver
import * as XLSX from 'xlsx';
import {saveAs} from 'file-saver';

export default {
    name: 'FormSubmissionsView',
    components: {
        Loading,
        BaseLayout,
    },
    props: {
        formId: {
            type: Number,
            required: true,
        },
    },
    data() {
        return {
            submissions: [],
            store: useMainStore(),
            form: null,
            isLoading: true,
            searchQuery: '',
            // Массив критериев сортировки (каждый объект: { column: string, ascending: boolean })
            sortCriteria: [],
            filters: {
                id: '',
                objectName: '',
                createdAt: '',
            },
        };
    },
    computed: {
        /**
         * Возвращает отсортированный и отфильтрованный список submissions.
         */
        filteredSubmissions() {
            // Сначала фильтруем
            let result = this.submissions.filter((item) => {
                let passes = true;
                // Глобальный фильтр по имени объекта
                if (this.searchQuery.trim()) {
                    const globalObject = item.object?.name?.toLowerCase() || '';
                    if (!globalObject.includes(this.searchQuery.toLowerCase())) {
                        passes = false;
                    }
                }
                // Фильтр по ID
                if (this.filters.id && !String(item.id).includes(this.filters.id)) {
                    passes = false;
                }
                // Фильтр по названию объекта
                if (
                    this.filters.objectName &&
                    !(item.object?.name?.toLowerCase().includes(this.filters.objectName.toLowerCase()))
                ) {
                    passes = false;
                }
                // Фильтры для атрибутов
                Object.keys(this.filters).forEach((key) => {
                    if (key.startsWith('attr_') && this.filters[key].trim()) {
                        const attrCode = key.slice(5);
                        const attrValue = item.object && item.object.attributes
                            ? item.object.attributes[attrCode]
                            : '';
                        if (!String(attrValue).toLowerCase().includes(this.filters[key].toLowerCase())) {
                            passes = false;
                        }
                    }
                });
                // Фильтр по дате
                const formattedDate = this.formatDateTime(item.created_at);
                if (
                    this.filters.createdAt &&
                    !formattedDate.toLowerCase().includes(this.filters.createdAt.toLowerCase())
                ) {
                    passes = false;
                }
                // Фильтры по полям формы
                if (this.form && this.form.fields && Array.isArray(item.fields)) {
                    this.form.fields.forEach((field, index) => {
                        const filterValue = this.filters[field.code];
                        if (filterValue) {
                            const fieldData = item.fields[index];
                            let answerValue = '';
                            if (fieldData) {
                                answerValue = Array.isArray(fieldData.answer)
                                    ? fieldData.answer.join(', ')
                                    : fieldData.answer;
                            }
                            if (!String(answerValue).toLowerCase().includes(filterValue.toLowerCase())) {
                                passes = false;
                            }
                        }
                    });
                }
                return passes;
            });

            // Затем сортируем по массиву sortCriteria
            result.sort((a, b) => {
                for (const criterion of this.sortCriteria) {
                    let valA, valB;

                    if (criterion.column === 'object_name') {
                        valA = a.object?.name || '';
                        valB = b.object?.name || '';
                    } else if (criterion.column === 'created_at') {
                        valA = new Date(a.created_at).getTime();
                        valB = new Date(b.created_at).getTime();
                    } else if (criterion.column === 'id') {
                        valA = a.id;
                        valB = b.id;
                    } else if (criterion.column.startsWith('attr_')) {
                        const attrCode = criterion.column.slice(5);
                        valA = a.object && a.object.attributes
                            ? (a.object.attributes[attrCode] ?? '')
                            : '';
                        valB = b.object && b.object.attributes
                            ? (b.object.attributes[attrCode] ?? '')
                            : '';
                    } else {
                        // Сортируем по коду поля формы
                        const fieldIndex = this.form.fields.findIndex(
                            (field) => field.code === criterion.column
                        );
                        if (fieldIndex === -1) continue; // неизвестное поле
                        const getAnswerValue = (submission) => {
                            let answerValue = submission.fields[fieldIndex]?.answer || '';
                            if (Array.isArray(answerValue)) {
                                answerValue = answerValue.join(', ');
                            }
                            return answerValue;
                        };
                        valA = getAnswerValue(a);
                        valB = getAnswerValue(b);
                    }

                    // Сравниваем
                    if (valA < valB) return criterion.ascending ? -1 : 1;
                    if (valA > valB) return criterion.ascending ? 1 : -1;
                    // Если равны, переходим к следующему критерию
                }
                return 0;
            });

            return result;
        },
        /**
         * Группировка по типу объекта для удобства отображения.
         */
        groupedSubmissions() {
            const groups = {};
            this.filteredSubmissions.forEach((submission) => {
                const key = submission.object && submission.object.type
                    ? submission.object.type
                    : 'Без объекта';
                if (!groups[key]) {
                    groups[key] = [];
                }
                groups[key].push(submission);
            });
            return groups;
        },
        /**
         * Возвращаем первый элемент критерия как «активную» колонку — если нужно.
         */
        activeSort() {
            return this.sortCriteria[0] || {column: '', ascending: true};
        },
    },
    methods: {
        async loadSubmissions() {
            await this.store.loadObjects();
            this.form = this.store.getForm(this.formId);

            // Инициализируем фильтры для каждого поля формы
            if (this.form && this.form.fields) {
                this.form.fields.forEach((field) => {
                    if (!(field.code in this.filters)) {
                        this.filters[field.code] = '';
                    }
                });
            }
            try {
                this.isLoading = true;
                const data = await fetchFormSubmissions(this.formId);
                this.submissions = data || [];
            } finally {
                this.isLoading = false;
            }
        },
        /**
         * Метод для 3-кликовой логики многоколоночной сортировки.
         */
        changeSort(column) {
            // Ищем существующий критерий
            const existingIndex = this.sortCriteria.findIndex((c) => c.column === column);

            if (existingIndex === -1) {
                // Колонка ещё не в списке: добавляем с ascending = true
                this.sortCriteria.unshift({column, ascending: true});
            } else {
                // Колонка уже есть; проверим направление
                const existing = this.sortCriteria[existingIndex];
                if (existing.ascending) {
                    // Был ascending -> станет descending
                    existing.ascending = false;
                    // Перенесём в начало массива
                    this.sortCriteria.splice(existingIndex, 1);
                    this.sortCriteria.unshift(existing);
                } else {
                    // Был descending -> убираем колонку
                    this.sortCriteria.splice(existingIndex, 1);
                }
            }
        },
        /**
         * Проверяем, сортируем ли сейчас по этой колонке (asc или desc).
         */
        isColumnSorted(column) {
            return this.sortCriteria.some((c) => c.column === column);
        },
        /**
         * Определяем, какая сортировка (asc/desc) у конкретной колонки.
         */
        getSortDirection(column) {
            const criterion = this.sortCriteria.find((c) => c.column === column);
            if (!criterion) return null;
            return criterion.ascending ? 'asc' : 'desc';
        },
        /**
         * Формат даты для отображения.
         */
        formatDateTime(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString('ru-RU');
        },
        /**
         * Получаем атрибуты объекта для формирования столбцов в таблице.
         */
        getAttributeColumns(submissions) {
            if (!submissions.length) return [];
            const sampleObject = submissions.find((s) => s.object)?.object;
            if (!sampleObject) return [];
            const type = this.store.getObjectTypeByCode(sampleObject.type);
            // Фильтруем только атрибуты, у которых show_off === true
            return (type?.available_attributes?.filter((attr) => attr.show_off === true)) || [];
        },
        /**
         * Возвращаем значение конкретного атрибута.
         */
        getAttributeValue(submission, attrCode) {
            return submission.object && submission.object.attributes
                ? submission.object.attributes[attrCode]
                : '';
        },

        /**
         * Экспорт отфильтрованных данных (filteredSubmissions) в Excel.
         * Используем имена атрибутов вместо кодов.
         */
        exportFilteredSubmissionsToExcel() {
            // Шаг 1. Подготовим данные в виде массива объектов
            const exportData = this.filteredSubmissions.map((submission) => {
                let rowData = {
                    'ID': submission.id,
                    'Объект': submission.object ? submission.object.name : 'Без объекта',
                    'Дата создания': this.formatDateTime(submission.created_at),
                };

                // Добавим атрибуты объекта по именам
                if (submission.object) {
                    const attrs = this.getAttributeColumns([submission]);
                    for (const attr of attrs) {
                        const attrValue = submission.object.attributes
                            ? submission.object.attributes[attr.code]
                            : '';
                        rowData[`Атрибут: ${attr.name}`] = attrValue;
                    }
                }

                // Добавим данные полей формы
                if (Array.isArray(submission.fields)) {
                    submission.fields.forEach((field) => {
                        const answerText = Array.isArray(field.answer)
                            ? field.answer.join(', ')
                            : field.answer;
                        rowData[field.name] = answerText;
                    });
                }

                return rowData;
            });

            // Шаг 2. Создаём worksheet из массива объектов
            const worksheet = XLSX.utils.json_to_sheet(exportData);

            // Шаг 3. Создаём новую рабочую книгу и добавляем worksheet
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, 'Данные');

            // Шаг 4. Генерируем файл в виде массива двоичных данных
            const excelBuffer = XLSX.write(workbook, {
                bookType: 'xlsx',
                type: 'array',
            });

            // Шаг 5. Сохраняем результат с помощью file-saver
            const blob = new Blob([excelBuffer], {type: 'application/octet-stream'});
            saveAs(blob, 'filtered_submissions.xlsx');
        },
    },
    async mounted() {
        await this.loadSubmissions();
    },
};
</script>

<style scoped>
/* При необходимости можно добавить стили для кнопок и др. элементов */
</style>