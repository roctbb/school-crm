<template>
    <BaseLayout>
            <PageHeader title="Типы сущностей" subtitle="Атрибуты, права, связи и виджеты CRM.">
                <template #actions>
                <button class="btn btn-primary" type="button" @click="startCreate">
                    <i class="bi bi-plus-lg me-1"></i> Новый тип
                </button>
                </template>
            </PageHeader>

            <div class="row g-3">
                <div class="col-lg-3">
                    <div class="list-group sticky-lg-top type-list">
                        <div class="list-group-item p-2">
                            <div class="input-group input-group-sm">
                                <span class="input-group-text bg-white text-muted"><i class="bi bi-search"></i></span>
                                <input v-model="listSearch" class="form-control" type="search" placeholder="Найти тип…" aria-label="Поиск типов сущностей" />
                            </div>
                        </div>
                        <button
                            v-for="type in filteredTypes"
                            :key="type.id"
                            class="list-group-item list-group-item-action d-flex justify-content-between"
                            :class="{active: draft?.id === type.id}"
                            type="button"
                            @click="selectType(type)"
                        >
                            <span>{{ type.name }}</span>
                            <code :class="{'text-white': draft?.id === type.id}">{{ type.code }}</code>
                        </button>
                        <div v-if="!filteredTypes.length" class="list-group-item text-muted small">Ничего не найдено.</div>
                    </div>
                </div>

                <div class="col-lg-9">
                    <div v-if="!draft" class="alert alert-light border">Выберите тип сущности.</div>
                    <form v-else @submit.prevent="save" @input="saved = false" @change="saved = false">
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div v-if="saved" class="alert alert-success">Изменения сохранены.</div>

                        <nav class="editor-section-nav d-flex flex-wrap gap-2 mb-3" aria-label="Разделы редактора">
                            <a class="btn btn-sm btn-light" href="#type-main">Основное</a>
                            <a class="btn btn-sm btn-light" href="#type-attributes">Атрибуты</a>
                            <a class="btn btn-sm btn-light" href="#type-params">Параметры</a>
                            <a class="btn btn-sm btn-light" href="#type-forms">Формы</a>
                        </nav>

                        <div v-if="usage" class="card mb-3">
                            <div class="card-body py-2 d-flex flex-wrap gap-3">
                                <span><b>{{ usage.object_count }}</b> {{ pluralize(usage.object_count, ['активный объект', 'активных объекта', 'активных объектов']) }}</span>
                                <span><b>{{ usage.revision_count }}</b> {{ pluralize(usage.revision_count, ['ревизия', 'ревизии', 'ревизий']) }}</span>
                                <span v-if="orphanEntries.length" class="orphan-warning" role="status">
                                    <i class="bi bi-exclamation-triangle me-1"></i>
                                    <strong>Поля вне текущей схемы:</strong>
                                    {{ orphanEntries.map(([code, count]) => `${code} (${count})`).join(', ') }}
                                    <span class="d-block small text-muted mt-1">
                                        Данные сохранены в объектах, но эти поля больше не описаны в редакторе типа.
                                    </span>
                                    <router-link :to="`/${draft.code}`" class="btn btn-sm btn-light mt-2">
                                        Проверить объекты
                                    </router-link>
                                </span>
                            </div>
                        </div>

                        <div id="type-main" class="card editor-card mb-3">
                            <div class="card-header">Основное</div>
                            <div class="card-body row g-3">
                                <div class="col-md-7">
                                    <label class="form-label">Название</label>
                                    <input v-model.trim="draft.name" class="form-control" maxlength="100" required />
                                </div>
                                <div class="col-md-5">
                                    <label class="form-label">Код</label>
                                    <input
                                        v-model.trim="draft.code"
                                        class="form-control font-monospace"
                                        :readonly="Boolean(draft.id)"
                                        pattern="[a-z][a-z0-9_-]+"
                                        required
                                    />
                                    <div v-if="draft.id" class="form-text">Код используется в URL и не изменяется.</div>
                                </div>
                            </div>
                        </div>

                        <div id="type-attributes" class="card editor-card mb-3">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <span>Атрибуты</span>
                                <button class="btn btn-sm btn-outline-primary" type="button" @click="addAttribute">
                                    Добавить поле
                                </button>
                            </div>
                            <div class="card-body">
                                <draggable v-model="draft.available_attributes" item-key="_editorKey" handle=".drag-handle">
                                    <template #item="{element: attribute, index}">
                                        <div class="border rounded mb-3 attribute-card" :class="{ 'attribute-card--expanded': isAttributeExpanded(attribute) }">
                                            <div class="attribute-summary d-flex align-items-center gap-2">
                                                <span class="drag-handle text-muted" title="Перетащить поле">
                                                    <i class="bi bi-grip-vertical"></i>
                                                </span>
                                                <button
                                                    class="attribute-summary-button flex-grow-1"
                                                    type="button"
                                                    :aria-expanded="isAttributeExpanded(attribute)"
                                                    @click="toggleAttribute(attribute)"
                                                >
                                                    <span class="attribute-name">{{ attribute.name || `Поле ${index + 1}` }}</span>
                                                    <code v-if="attribute.code">{{ attribute.code }}</code>
                                                    <span class="badge text-bg-light">{{ attributeTypeLabel(attribute.type) }}</span>
                                                    <small v-if="attributeUsage(attribute.code)" class="text-muted">
                                                        Используется: {{ attributeUsage(attribute.code) }}
                                                    </small>
                                                </button>
                                                <button
                                                    class="btn btn-sm btn-light icon-button"
                                                    type="button"
                                                    :aria-label="isAttributeExpanded(attribute) ? `Свернуть ${attribute.name || `поле ${index + 1}`}` : `Редактировать ${attribute.name || `поле ${index + 1}`}`"
                                                    @click="toggleAttribute(attribute)"
                                                >
                                                    <i :class="isAttributeExpanded(attribute) ? 'bi bi-chevron-up' : 'bi bi-pencil'"></i>
                                                </button>
                                                <span
                                                    v-if="attributeUsage(attribute.code) > 0"
                                                    class="disabled-action-hint"
                                                    tabindex="0"
                                                    :aria-label="`Нельзя удалить поле: оно используется в ${attributeUsage(attribute.code)} ${pluralize(attributeUsage(attribute.code), ['объекте', 'объектах', 'объектах'])}`"
                                                    title="Нельзя удалить: поле используется в данных"
                                                >
                                                    <i class="bi bi-lock"></i>
                                                </span>
                                                <button
                                                    v-else
                                                    class="btn btn-sm btn-outline-danger icon-button"
                                                    type="button"
                                                    :aria-label="`Удалить ${attribute.name || `поле ${index + 1}`}`"
                                                    title="Удалить поле"
                                                    @click="removeAttribute(index)"
                                                >
                                                    <i class="bi bi-trash"></i>
                                                </button>
                                            </div>

                                            <div v-show="isAttributeExpanded(attribute)" class="attribute-editor-body">
                                            <div class="row g-2">
                                                <div class="col-md-5">
                                                    <label class="form-label form-label-sm">Название</label>
                                                    <input v-model.trim="attribute.name" class="form-control form-control-sm" required />
                                                </div>
                                                <div class="col-md-4">
                                                    <label class="form-label form-label-sm">Код</label>
                                                    <input
                                                        v-model.trim="attribute.code"
                                                        class="form-control form-control-sm font-monospace"
                                                        :readonly="attributeUsage(attribute.code) > 0"
                                                        required
                                                    />
                                                </div>
                                                <div class="col-md-3">
                                                    <label class="form-label form-label-sm">Тип</label>
                                                    <select
                                                        v-model="attribute.type"
                                                        class="form-select form-select-sm"
                                                        :disabled="attributeUsage(attribute.code) > 0"
                                                    >
                                                        <option v-for="type in attributeTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
                                                    </select>
                                                </div>
                                                <div class="col-12">
                                                    <label class="form-label form-label-sm">Описание</label>
                                                    <input v-model="attribute.description" class="form-control form-control-sm" />
                                                </div>
                                                <div v-if="['select', 'checkboxes'].includes(attribute.type)" class="col-12">
                                                    <label class="form-label form-label-sm">Варианты, по одному на строку</label>
                                                    <textarea v-model="attribute.optionsText" class="form-control form-control-sm" rows="3"></textarea>
                                                </div>
                                            </div>

                                            <div class="d-flex flex-wrap gap-3 mt-3">
                                                <label v-for="flag in attributeFlags" :key="flag.key" class="form-check">
                                                    <input
                                                        v-model="attribute[flag.key]"
                                                        class="form-check-input"
                                                        type="checkbox"
                                                        @change="flag.key === 'group' && normalizeDefaultGrouping()"
                                                    />
                                                    <span class="form-check-label">{{ flag.label }}</span>
                                                </label>
                                                <label v-if="attribute.type === 'file'" class="form-check">
                                                    <input v-model="attribute.keep_history" class="form-check-input" type="checkbox" />
                                                    <span class="form-check-label">Хранить историю</span>
                                                </label>
                                            </div>
                                            </div>
                                        </div>
                                    </template>
                                </draggable>
                                <div v-if="!draft.available_attributes.length" class="text-muted">У типа пока нет атрибутов.</div>
                            </div>
                        </div>

                        <div id="type-params" class="card editor-card mb-3">
                            <div class="card-header">Параметры типа</div>
                            <div class="card-body">
                                <div class="row g-3">
                                    <div class="col-md-3">
                                        <label class="form-label">Позиция</label>
                                        <input v-model.number="draft.params.index" class="form-control" min="0" type="number" />
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label">Группировка по умолчанию</label>
                                        <select v-model="draft.params.default_grouping" class="form-select">
                                            <option value="">Не группировать</option>
                                            <option
                                                v-for="attribute in defaultGroupingAttributes"
                                                :key="attribute.code"
                                                :value="attribute.code"
                                            >
                                                {{ attribute.name }}
                                            </option>
                                        </select>
                                        <div class="form-text">Применяется при открытии страницы без выбранной группировки.</div>
                                    </div>
                                    <div class="col-md-5">
                                        <label class="form-label">Подсказка редактора</label>
                                        <input v-model="draft.params.edit_description" class="form-control" />
                                    </div>
                                </div>

                                <div class="row g-3 mt-1">
                                    <div class="col-md-4">
                                        <h6>Права создания</h6>
                                        <label v-for="role in roles" :key="`create-${role}`" class="form-check form-check-inline">
                                            <input v-model="draft.params.can_create" :value="role" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">{{ roleLabel(role) }}</span>
                                        </label>
                                    </div>
                                    <div class="col-md-4">
                                        <h6>Права удаления владельцем</h6>
                                        <label v-for="role in roles" :key="`delete-${role}`" class="form-check form-check-inline">
                                            <input v-model="draft.params.can_delete" :value="role" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">{{ roleLabel(role) }}</span>
                                        </label>
                                    </div>
                                    <div class="col-md-4">
                                        <h6>Права заполнения</h6>
                                        <label v-for="role in roles" :key="`fill-${role}`" class="form-check form-check-inline">
                                            <input v-model="draft.params.can_fill" :value="role" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">{{ roleLabel(role) }}</span>
                                        </label>
                                    </div>
                                </div>

                                <div class="row g-3 mt-1">
                                    <div class="col-md-6">
                                        <h6>Возможные дочерние типы</h6>
                                        <label v-for="type in childTypeOptions" :key="type.code" class="form-check">
                                            <input v-model="draft.params.possible_children" :value="type.code" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">{{ type.name }} ({{ type.code }})</span>
                                        </label>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Флаги</h6>
                                        <label class="form-check">
                                            <input v-model="draft.params.is_hidden" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">Скрытый тип</span>
                                        </label>
                                        <label class="form-check">
                                            <input v-model="draft.params.comments_hidden" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">Скрывать комментарии</span>
                                        </label>
                                    </div>
                                </div>

                                <div class="row g-3 mt-1">
                                    <div class="col-md-6">
                                        <h6>Виджеты списка</h6>
                                        <label v-for="widget in widgets" :key="`list-${widget}`" class="form-check">
                                            <input v-model="draft.params.widgets" :value="widget" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">{{ widget }}</span>
                                        </label>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Виджеты страницы объекта</h6>
                                        <label v-for="widget in widgets" :key="`details-${widget}`" class="form-check">
                                            <input v-model="draft.params.details_widgets" :value="widget" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">{{ widget }}</span>
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="type-forms" class="card editor-card mb-3">
                            <div class="card-header">Категории форм</div>
                            <div class="card-body">
                                <label v-for="category in store.formCategories" :key="category.id" class="form-check">
                                    <input v-model="draft.form_category_ids" :value="category.id" class="form-check-input" type="checkbox" />
                                    <span class="form-check-label">{{ category.name }}</span>
                                </label>
                                <span v-if="!store.formCategories.length" class="text-muted">Категорий форм нет.</span>
                            </div>
                        </div>

                        <div v-if="revisions.length" class="card mb-3">
                            <div class="card-header">Последние изменения</div>
                            <ul class="list-group list-group-flush">
                                <li v-for="revision in revisions.slice(0, 5)" :key="revision.id" class="list-group-item small">
                                    {{ formatRevisionDate(revision.created_at) }} —
                                    {{ revision.editor?.name || 'неизвестный пользователь' }}
                                </li>
                            </ul>
                        </div>

                        <div class="editor-save-bar">
                            <span class="small" :class="hasUnsavedChanges ? 'text-warning-emphasis' : 'text-muted'">
                                <i class="bi me-1" :class="hasUnsavedChanges ? 'bi-circle-fill' : 'bi-check-circle'"></i>
                                {{ hasUnsavedChanges ? 'Есть несохранённые изменения' : 'Все изменения сохранены' }}
                            </span>
                            <button class="btn btn-primary" type="submit" :disabled="saving">
                                {{ saving ? 'Сохранение…' : 'Сохранить' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
    </BaseLayout>
</template>

<script>
import draggable from 'vuedraggable';
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import PageHeader from '@/components/common/PageHeader.vue';
import useMainStore from '@/stores/mainStore.js';
import unsavedChangesMixin from '@/mixins/unsavedChangesMixin.js';
import {buildGroupingOptions} from '@/utils/objectGrouping.js';
import {
    createObjectType,
    fetchObjectTypeRevisions,
    fetchObjectTypeUsage,
    updateObjectType,
} from '@/api/objects_api.js';

const clone = value => JSON.parse(JSON.stringify(value));

export default {
    name: 'ObjectTypesAdminView',
    components: {BaseLayout, PageHeader, draggable},
    mixins: [unsavedChangesMixin],
    data() {
        return {
            store: useMainStore(),
            draft: null,
            usage: null,
            revisions: [],
            saving: false,
            saved: false,
            error: null,
            initialSnapshot: '',
            listSearch: '',
            expandedAttributeKey: null,
            attributeTypes: [
                {value: 'string', label: 'Строка'},
                {value: 'text', label: 'Текст'},
                {value: 'number', label: 'Число'},
                {value: 'date', label: 'Дата'},
                {value: 'file', label: 'Файл'},
                {value: 'link', label: 'Ссылка'},
                {value: 'select', label: 'Один вариант'},
                {value: 'checkboxes', label: 'Несколько вариантов'},
            ],
            roles: ['student', 'teacher', 'admin'],
            widgets: ['active_events', 'birthdays', 'calendar', 'portfolio_progress'],
            attributeFlags: [
                {key: 'required', label: 'Обязательное'},
                {key: 'display', label: 'Показывать'},
                {key: 'show_off', label: 'В карточке'},
                {key: 'group', label: 'Группировка'},
                {key: 'is_locked', label: 'Заблокировано'},
                {key: 'is_private', label: 'Приватное'},
                {key: 'is_hidden', label: 'Скрытое'},
                {key: 'is_secret', label: 'Секретное'},
            ],
        };
    },
    computed: {
        sortedTypes() {
            return [...this.store.objectTypes].sort((a, b) => (a.params?.index || 0) - (b.params?.index || 0));
        },
        filteredTypes() {
            const query = this.listSearch.trim().toLowerCase();
            if (!query) return this.sortedTypes;
            return this.sortedTypes.filter(type => (
                type.name.toLowerCase().includes(query) || type.code.toLowerCase().includes(query)
            ));
        },
        childTypeOptions() {
            return this.store.objectTypes;
        },
        defaultGroupingAttributes() {
            return buildGroupingOptions(this.draft?.available_attributes).filter(attribute => attribute.code);
        },
        orphanEntries() {
            return Object.entries(this.usage?.orphan_attributes || {});
        },
        hasUnsavedChanges() {
            return Boolean(this.draft && this.initialSnapshot && JSON.stringify(this.payload()) !== this.initialSnapshot);
        },
    },
    async created() {
        await this.store.loadObjects();
        if (this.sortedTypes.length) await this.selectType(this.sortedTypes[0]);
    },
    methods: {
        prepareDraft(type) {
            const prepared = clone(type);
            prepared.available_attributes = (prepared.available_attributes || []).map((attribute, index) => ({
                required: false,
                display: false,
                show_off: false,
                group: false,
                is_locked: false,
                is_private: false,
                is_hidden: false,
                is_secret: false,
                keep_history: false,
                description: '',
                ...attribute,
                optionsText: (attribute.options || []).join('\n'),
                _editorKey: `${attribute.code || 'attribute'}-${index}-${Date.now()}`,
            }));
            prepared.params = {
                index: 0,
                possible_children: [],
                can_create: [],
                can_delete: [],
                can_fill: [],
                widgets: [],
                details_widgets: [],
                is_hidden: false,
                comments_hidden: false,
                edit_description: '',
                default_grouping: '',
                ...(prepared.params || {}),
            };
            prepared.form_category_ids = (prepared.form_categories || []).map(category => category.id);
            return prepared;
        },
        async selectType(type) {
            if (this.draft?.id === type.id) return;
            if (this.hasUnsavedChanges && !window.confirm('Отменить несохранённые изменения и открыть другой тип?')) return;
            this.draft = this.prepareDraft(type);
            this.initialSnapshot = JSON.stringify(this.payload());
            this.error = null;
            this.saved = false;
            this.expandedAttributeKey = null;
            [this.usage, this.revisions] = await Promise.all([
                fetchObjectTypeUsage(type.id),
                fetchObjectTypeRevisions(type.id),
            ]);
        },
        startCreate() {
            if (this.hasUnsavedChanges && !window.confirm('Отменить несохранённые изменения и создать новый тип?')) return;
            this.draft = this.prepareDraft({
                id: null,
                name: '',
                code: '',
                available_attributes: [],
                params: {index: this.store.objectTypes.length + 1},
                form_categories: [],
            });
            this.usage = null;
            this.revisions = [];
            this.error = null;
            this.saved = false;
            this.initialSnapshot = JSON.stringify(this.payload());
        },
        addAttribute() {
            const attribute = {
                name: '',
                code: '',
                type: 'string',
                description: '',
                optionsText: '',
                options: [],
                required: false,
                display: true,
                show_off: false,
                group: false,
                is_locked: false,
                is_private: false,
                is_hidden: false,
                is_secret: false,
                keep_history: false,
                _editorKey: `new-${Date.now()}-${Math.random()}`,
            };
            this.draft.available_attributes.push(attribute);
            this.expandedAttributeKey = attribute._editorKey;
        },
        removeAttribute(index) {
            this.draft.available_attributes.splice(index, 1);
            this.normalizeDefaultGrouping();
        },
        attributeUsage(code) {
            return this.usage?.attribute_usage?.[code] || 0;
        },
        isAttributeExpanded(attribute) {
            return this.expandedAttributeKey === attribute._editorKey;
        },
        toggleAttribute(attribute) {
            this.expandedAttributeKey = this.isAttributeExpanded(attribute) ? null : attribute._editorKey;
        },
        attributeTypeLabel(value) {
            return this.attributeTypes.find(type => type.value === value)?.label || value;
        },
        pluralize(value, forms) {
            const number = Math.abs(Number(value)) % 100;
            const lastDigit = number % 10;
            if (number > 10 && number < 20) return forms[2];
            if (lastDigit > 1 && lastDigit < 5) return forms[1];
            if (lastDigit === 1) return forms[0];
            return forms[2];
        },
        payload() {
            const attributes = this.draft.available_attributes.map(attribute => {
                const {_editorKey, optionsText, ...clean} = attribute;
                clean.options = optionsText.split('\n').map(option => option.trim()).filter(Boolean);
                return clean;
            });
            const params = clone(this.draft.params);
            const groupableCodes = new Set(buildGroupingOptions(attributes).map(attribute => attribute.code));
            if (!groupableCodes.has(params.default_grouping)) params.default_grouping = '';
            return {
                name: this.draft.name,
                code: this.draft.code,
                available_attributes: attributes,
                params,
                form_category_ids: [...this.draft.form_category_ids],
            };
        },
        normalizeDefaultGrouping() {
            const selectedCode = this.draft?.params?.default_grouping;
            if (selectedCode && !this.defaultGroupingAttributes.some(attribute => attribute.code === selectedCode)) {
                this.draft.params.default_grouping = '';
            }
        },
        async save() {
            this.saving = true;
            this.error = null;
            this.saved = false;
            try {
                const result = this.draft.id
                    ? await updateObjectType(this.draft.id, this.payload())
                    : await createObjectType(this.payload());
                const existingIndex = this.store.objectTypes.findIndex(type => type.id === result.id);
                if (existingIndex >= 0) this.store.objectTypes[existingIndex] = result;
                else {
                    this.store.objectTypes.push(result);
                    this.store.objects[result.code] = [];
                }
                this.initialSnapshot = JSON.stringify(this.payload());
                await this.selectType(result);
                this.saved = true;
            } catch (error) {
                this.error = error.message || 'Не удалось сохранить тип сущности.';
            } finally {
                this.saving = false;
            }
        },
        formatRevisionDate(value) {
            return new Date(value).toLocaleString('ru-RU');
        },
        roleLabel(role) {
            return {student: 'Ученик', teacher: 'Учитель', admin: 'Администратор'}[role] || role;
        },
    },
};
</script>

<style scoped>
.type-list {
    top: 4.75rem;
    overflow: hidden;
    border: 1px solid var(--silaeder-border);
    border-radius: 0.75rem;
    background: var(--silaeder-surface);
    box-shadow: var(--silaeder-shadow-sm);
}

.type-list > .list-group-item {
    border-inline: 0;
}

.type-list > .list-group-item:first-child {
    border-top: 0;
}

.type-list > .list-group-item:last-child {
    border-bottom: 0;
}

.attribute-card {
    border-color: var(--silaeder-border) !important;
    border-radius: 0.65rem !important;
    background: var(--silaeder-surface);
}

.attribute-summary {
    min-height: 3.25rem;
    padding: 0.55rem 0.65rem;
}

.attribute-summary-button {
    display: flex;
    min-width: 0;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35rem 0.75rem;
    padding: 0;
    color: inherit;
    text-align: left;
    border: 0;
    background: transparent;
}

.attribute-name {
    min-width: 8rem;
    font-weight: 600;
}

.attribute-editor-body {
    padding: 0.85rem 1rem 1rem;
    border-top: 1px solid var(--silaeder-border);
}

.disabled-action-hint {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    color: var(--silaeder-muted);
    border: 1px solid var(--silaeder-border);
    border-radius: 0.4rem;
    background: var(--silaeder-surface-subtle);
    cursor: help;
}

.orphan-warning {
    flex-basis: 100%;
    padding: 0.55rem 0.7rem;
    color: #685718;
    border: 1px solid #eadb9a;
    border-radius: 0.5rem;
    background: #fff9df;
}

.drag-handle {
    cursor: grab;
    user-select: none;
}

.form-label-sm {
    font-size: 0.85rem;
    margin-bottom: 0.2rem;
}

@media (max-width: 575.98px) {
    .attribute-summary {
        align-items: flex-start !important;
    }

    .attribute-summary-button {
        align-items: flex-start;
        flex-direction: column;
    }

    .attribute-name {
        min-width: 0;
    }
}
</style>
