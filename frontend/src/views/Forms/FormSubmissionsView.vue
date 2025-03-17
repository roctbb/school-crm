<template>
    <BaseLayout>
        <div class="container mt-3">
            <loading v-if="isLoading" />
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

                <!-- Сгруппированные ответы по типу объекта (группировка по ВСЕМ данным, без фильтрации) -->
                <div v-for="(submissions, objectType) in groupedSubmissions" :key="objectType" class="mb-5">
                    <div class="d-flex align-items-center mb-2">
                        <h4 class="mb-0">
                            {{ objectType === 'Без объекта' ? 'Объекты без типа' : ('Тип объекта: ' + store.getObjectTypeByCode(objectType)?.name) }}
                        </h4>
                        <button class="btn btn-sm btn-secondary ms-auto" @click="exportFilteredSubmissionsToExcel">
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
                            <!-- Столбцы для атрибутов -->
                            <th
                                v-for="attr in getAttributeColumns(submissions, objectType)"
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
                                v-for="field in formFields"
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
                                v-for="attr in getAttributeColumns(submissions, objectType)"
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
                                v-for="field in formFields"
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
                        <tr v-if="sortedSubmissions(objectType).length === 0">
                            <td :colspan="2 + getAttributeColumns(submissions, objectType).length + 1 + formFields.length" class="text-center text-muted">
                                Нет результатов для отображения.
                            </td>
                        </tr>
                        <tr
                            v-for="submission in sortedSubmissions(objectType)"
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
                            <td v-for="attr in getAttributeColumns(submissions, objectType)" :key="attr.code">
                                {{ getAttributeValue(submission, attr.code) }}
                            </td>
                            <td>{{ formatDateTime(submission.created_at) }}</td>
                            <!-- Данные полей формы -->
                            <td v-for="(field, i) in submission.fields" :key="i">
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

<script lang="js">
import { fetchFormSubmissions } from '@/api/forms_api.js';
import Loading from '@/components/common/Loading.vue';
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import useMainStore from '@/stores/mainStore.js';

// Подключаем библиотеки xlsx и file-saver
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

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
                // Фильтры для полей формы будут добавлены динамически по коду поля
            },
        };
    },
    computed: {
        /**
         * Группировка по типу объекта.
         * Группировка производится по ВСЕМ полученным данным, чтобы заголовок таблицы оставался виден.
         */
        groupedSubmissions() {
            const groups = {};
            this.submissions.forEach((submission) => {
                const key =
                    submission.object && submission.object.type
                        ? submission.object.type
                        : 'Без объекта';
                if (!groups[key]) {
                    groups[key] = [];
                }
                groups[key].push(submission);
            });
            return groups;
        },
        formFields() {
            return [...this.form._category?.common_fields, ...this.form.fields]
        }
    },
    methods: {
        async loadSubmissions() {
            await this.store.loadObjects();
            this.form = this.store.getForm(this.formId);

            if (this.form && this.form.fields) {
                this.formFields.forEach((field) => {
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
         * Функция фильтрации одной строки.
         * Логика аналогична предыдущей реализации фильтрации.
         */
        filterSubmission(submission) {
            let passes = true;
            // Глобальный фильтр по имени объекта
            if (this.searchQuery.trim()) {
                const globalObject = submission.object?.name?.toLowerCase() || '';
                if (!globalObject.includes(this.searchQuery.toLowerCase())) {
                    passes = false;
                }
            }
            // Фильтр по ID
            if (this.filters.id && !String(submission.id).includes(this.filters.id)) {
                passes = false;
            }
            // Фильтр по названию объекта
            if (
                this.filters.objectName &&
                !(submission.object?.name?.toLowerCase().includes(this.filters.objectName.toLowerCase()))
            ) {
                passes = false;
            }
            // Фильтры для атрибутов
            Object.keys(this.filters).forEach((key) => {
                if (key.startsWith('attr_') && this.filters[key].trim()) {
                    const attrCode = key.slice(5);
                    const attrValue =
                        submission.object && submission.object.attributes
                            ? submission.object.attributes[attrCode]
                            : '';
                    if (!String(attrValue).toLowerCase().includes(this.filters[key].toLowerCase())) {
                        passes = false;
                    }
                }
            });
            // Фильтр по дате
            const formattedDate = this.formatDateTime(submission.created_at);
            if (
                this.filters.createdAt &&
                !formattedDate.toLowerCase().includes(this.filters.createdAt.toLowerCase())
            ) {
                passes = false;
            }
            // Фильтры для полей формы
            if (this.form && this.formFields && Array.isArray(submission.fields)) {
                this.formFields.forEach((field, index) => {
                    const filterValue = this.filters[field.code];
                    if (filterValue) {
                        const fieldData = submission.fields[index];
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
        },
        /**
         * Применение сортировки к переданному массиву строк.
         * Копия массива сортируется согласно this.sortCriteria.
         */
        sortSubmissions(rows) {
            const result = [...rows];
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
                        // Сортировка по полям формы (код поля)
                        const fieldIndex = this.formFields.findIndex(
                            (field) => field.code === criterion.column
                        );
                        if (fieldIndex === -1) continue;
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
                    if (valA < valB) return criterion.ascending ? -1 : 1;
                    if (valA > valB) return criterion.ascending ? 1 : -1;
                    // Если равны, проверяем следующий критерий
                }
                return 0;
            });
            return result;
        },
        /**
         * Удобный метод для получения отсортированного и отфильтрованного списка строк для группы.
         * objectType – ключ группы, submissions – полный список строк группы (без фильтрации).
         */
        sortedSubmissions(objectType) {
            const groupRows = this.groupedSubmissions[objectType] || [];
            const filteredRows = groupRows.filter(this.filterSubmission);
            return this.sortSubmissions(filteredRows);
        },
        /**
         * Метод трёхкликовой сортировки (многоколоночная).
         */
        changeSort(column) {
            const existingIndex = this.sortCriteria.findIndex((c) => c.column === column);
            if (existingIndex === -1) {
                // Колонка ещё не используется – добавляем с направлением по возрастанию.
                this.sortCriteria.unshift({ column, ascending: true });
            } else {
                const existing = this.sortCriteria[existingIndex];
                if (existing.ascending) {
                    existing.ascending = false;
                    this.sortCriteria.splice(existingIndex, 1);
                    this.sortCriteria.unshift(existing);
                } else {
                    // Если уже было обратное направление – убираем критерий.
                    this.sortCriteria.splice(existingIndex, 1);
                }
            }
        },
        /**
         * Проверка, применяется ли сортировка по указанной колонке.
         */
        isColumnSorted(column) {
            return this.sortCriteria.some((c) => c.column === column);
        },
        /**
         * Получение направления сортировки для колонки.
         */
        getSortDirection(column) {
            const criterion = this.sortCriteria.find((c) => c.column === column);
            if (!criterion) return null;
            return criterion.ascending ? 'asc' : 'desc';
        },
        /**
         * Форматирование даты для отображения.
         */
        formatDateTime(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString('ru-RU');
        },
        /**
         * Возвращает атрибуты для формирования столбцов таблицы.
         * Если в группе строк нет ни одной записи, то пытаемся получить атрибуты по типу объекта из хранилища.
         */
        getAttributeColumns(submissions, objectType) {
            // Если есть хоть одна запись с объектом – используем её тип.
            let sampleSubmission = submissions.find((s) => s.object);
            if (sampleSubmission) {
                const type = this.store.getObjectTypeByCode(sampleSubmission.object.type);
                return (type?.available_attributes?.filter((attr) => attr.show_off === true)) || [];
            }
            // Если группа пуста, но это не "Без объекта" – пытаемся получить тип по коду.
            if (objectType !== 'Без объекта') {
                const type = this.store.getObjectTypeByCode(objectType);
                return (type?.available_attributes?.filter((attr) => attr.show_off === true)) || [];
            }
            return [];
        },
        /**
         * Возвращает значение атрибута для записи.
         */
        getAttributeValue(submission, attrCode) {
            return submission.object && submission.object.attributes
                ? submission.object.attributes[attrCode]
                : '';
        },
        /**
         * Экспорт отфильтрованных данных (согласно применённым фильтрам и сортировке) в Excel.
         */
        exportFilteredSubmissionsToExcel() {
            // Собираем все строки, проходящие фильтр
            let allFiltered = [];
            Object.keys(this.groupedSubmissions).forEach((objectType) => {
                const rows = this.sortedSubmissions(objectType);
                allFiltered = allFiltered.concat(rows);
            });
            // Подготавливаем данные для экспорта
            const exportData = allFiltered.map((submission) => {
                let rowData = {
                    'ID': submission.id,
                    'Объект': submission.object ? submission.object.name : 'Без объекта',
                    'Дата создания': this.formatDateTime(submission.created_at),
                };
                // Добавляем атрибуты объекта по именам
                if (submission.object) {
                    const attrs = this.getAttributeColumns([submission], submission.object.type);
                    for (const attr of attrs) {
                        const attrValue = submission.object.attributes
                            ? submission.object.attributes[attr.code]
                            : '';
                        rowData[`Атрибут: ${attr.name}`] = attrValue;
                    }
                }
                // Добавляем данные полей формы
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
            // Создаём worksheet и рабочую книгу
            const worksheet = XLSX.utils.json_to_sheet(exportData);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, 'Данные');
            const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
            const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
            saveAs(blob, 'filtered_submissions.xlsx');
        },
    },
    async mounted() {
        await this.loadSubmissions();
    },
};
</script>

<style scoped>
/* Стили можно расширить по необходимости */
</style>