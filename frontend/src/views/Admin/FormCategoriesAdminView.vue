<template>
    <BaseLayout>
            <PageHeader title="Категории форм" subtitle="Общие поля, доступ и отображение форм.">
                <template #actions>
                <button class="btn btn-primary" type="button" @click="startCreate">
                    <i class="bi bi-plus-lg me-1"></i> Новая категория
                </button>
                </template>
            </PageHeader>

            <Loading v-if="loading" />
            <div v-else class="row g-3">
                <div class="col-lg-3">
                    <div class="list-group sticky-lg-top category-list">
                        <div class="list-group-item p-2">
                            <div class="input-group input-group-sm">
                                <span class="input-group-text bg-white text-muted"><i class="bi bi-search"></i></span>
                                <input v-model="listSearch" class="form-control" type="search" placeholder="Найти категорию…" aria-label="Поиск категорий форм" />
                            </div>
                        </div>
                        <button
                            v-for="category in filteredCategories"
                            :key="category.id"
                            class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                            :class="{active: draft?.id === category.id}"
                            type="button"
                            @click="selectCategory(category)"
                        >
                            <span>{{ category.name }}</span>
                            <span class="badge rounded-pill" :class="draft?.id === category.id ? 'text-bg-light' : 'text-bg-secondary'">
                                {{ category.forms.length }}
                            </span>
                        </button>
                        <div v-if="!sortedCategories.length" class="list-group-item text-muted">
                            Категорий пока нет.
                        </div>
                        <div v-else-if="!filteredCategories.length" class="list-group-item text-muted small">Ничего не найдено.</div>
                    </div>
                </div>

                <div class="col-lg-9">
                    <div v-if="!draft" class="alert alert-light border">
                        Выберите категорию или создайте новую.
                    </div>
                    <form v-else @submit.prevent="save" @input="saved = false" @change="saved = false">
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div v-if="saved" class="alert alert-success">Изменения сохранены.</div>

                        <nav class="editor-section-nav d-flex flex-wrap gap-2 mb-3" aria-label="Разделы редактора">
                            <a class="btn btn-sm btn-light" href="#category-main">Основное</a>
                            <a class="btn btn-sm btn-light" href="#category-access">Доступ</a>
                            <a class="btn btn-sm btn-light" href="#category-fields">Общие поля</a>
                        </nav>

                        <div v-if="usage" class="card mb-3">
                            <div class="card-body py-2 d-flex flex-wrap gap-3">
                                <span><b>{{ usage.form_count }}</b> активных форм</span>
                                <span><b>{{ usage.object_type_count }}</b> типов сущностей</span>
                                <span v-if="usage.child_category_count">
                                    <b>{{ usage.child_category_count }}</b> дочерних категорий
                                </span>
                            </div>
                        </div>

                        <div id="category-main" class="card editor-card mb-3">
                            <div class="card-header">Основное</div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label class="form-label">Название</label>
                                    <input v-model.trim="draft.name" class="form-control" maxlength="256" required />
                                </div>

                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-check form-switch">
                                            <input v-model="draft.params.is_hidden" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">Скрытая категория</span>
                                        </label>
                                        <div class="form-text">
                                            Ученики не увидят категорию и её формы.
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-check form-switch">
                                            <input v-model="draft.params.is_private" class="form-check-input" type="checkbox" />
                                            <span class="form-check-label">Приватные ответы</span>
                                        </label>
                                        <div class="form-text">
                                            Ответы доступны только владельцам объекта и сотрудникам.
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="category-access" class="card editor-card mb-3">
                            <div class="card-header">Доступ и группировка</div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <h6>Кто может заполнять формы</h6>
                                    <label v-for="role in roles" :key="role.value" class="form-check form-check-inline">
                                        <input
                                            v-model="draft.params.can_create"
                                            :value="role.value"
                                            class="form-check-input"
                                            type="checkbox"
                                        />
                                        <span class="form-check-label">{{ role.label }}</span>
                                    </label>
                                    <div class="form-text">Учителя и администраторы имеют доступ независимо от настройки.</div>
                                </div>

                                <div>
                                    <label class="form-label">Поля группировки карточек ответов</label>
                                    <textarea
                                        v-model="groupingText"
                                        class="form-control"
                                        rows="3"
                                        placeholder="Одно название поля на строку"
                                    ></textarea>
                                    <div class="form-text">
                                        Указываются точные названия закреплённых полей из общих полей или форм категории.
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="category-fields" class="card editor-card mb-3">
                            <div class="card-header">Общие поля</div>
                            <div class="card-body">
                                <p class="text-muted small">
                                    Эти поля автоматически добавляются во все формы категории.
                                </p>
                                <FormFieldsEditor v-model="draft.common_fields" />
                            </div>
                        </div>

                        <div class="editor-save-bar">
                            <div v-if="draft.id" class="d-flex flex-column align-items-start">
                                <button
                                    class="btn btn-outline-danger"
                                    type="button"
                                    :disabled="saving || hasUsage"
                                    :title="deleteHint"
                                    @click="removeCategory"
                                >
                                    <i class="bi bi-trash me-1"></i> Удалить
                                </button>
                                <small v-if="hasUsage" class="text-muted mt-1">Категория используется и пока не может быть удалена.</small>
                            </div>
                            <span v-else class="small" :class="hasUnsavedChanges ? 'text-warning-emphasis' : 'text-muted'">
                                <i class="bi me-1" :class="hasUnsavedChanges ? 'bi-circle-fill' : 'bi-check-circle'"></i>
                                {{ hasUnsavedChanges ? 'Есть несохранённые изменения' : 'Изменений нет' }}
                            </span>
                            <div class="d-flex align-items-center gap-3">
                                <span v-if="draft.id" class="small d-none d-md-inline" :class="hasUnsavedChanges ? 'text-warning-emphasis' : 'text-muted'">
                                    {{ hasUnsavedChanges ? 'Есть несохранённые изменения' : 'Все изменения сохранены' }}
                                </span>
                                <button class="btn btn-primary" type="submit" :disabled="saving">
                                    {{ saving ? 'Сохранение…' : (draft.id ? 'Сохранить' : 'Создать') }}
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import PageHeader from '@/components/common/PageHeader.vue';
import Loading from '@/components/common/Loading.vue';
import FormFieldsEditor from '@/components/forms/FormFieldsEditor.vue';
import {
    createFormCategory,
    deleteFormCategory,
    fetchFormCategoryUsage,
    updateFormCategory,
} from '@/api/forms_api.js';
import useMainStore from '@/stores/mainStore.js';
import unsavedChangesMixin from '@/mixins/unsavedChangesMixin.js';

const clone = value => JSON.parse(JSON.stringify(value));

export default {
    name: 'FormCategoriesAdminView',
    components: {BaseLayout, FormFieldsEditor, Loading, PageHeader},
    mixins: [unsavedChangesMixin],
    data() {
        return {
            store: useMainStore(),
            draft: null,
            usage: null,
            groupingText: '',
            loading: true,
            saving: false,
            saved: false,
            error: null,
            initialSnapshot: '',
            listSearch: '',
            roles: [
                {value: 'student', label: 'Ученик'},
                {value: 'teacher', label: 'Учитель'},
                {value: 'admin', label: 'Администратор'},
            ],
        };
    },
    computed: {
        sortedCategories() {
            return [...this.store.formCategories].sort((a, b) => a.name.localeCompare(b.name, 'ru'));
        },
        filteredCategories() {
            const query = this.listSearch.trim().toLowerCase();
            if (!query) return this.sortedCategories;
            return this.sortedCategories.filter(category => category.name.toLowerCase().includes(query));
        },
        hasUsage() {
            return Boolean(
                this.usage?.form_count
                || this.usage?.object_type_count
                || this.usage?.child_category_count
            );
        },
        deleteHint() {
            if (!this.hasUsage) return 'Удалить категорию';
            return 'Сначала удалите формы и дочерние категории, затем отвяжите категорию от типов сущностей.';
        },
        hasUnsavedChanges() {
            return Boolean(this.draft && this.initialSnapshot && JSON.stringify(this.payload()) !== this.initialSnapshot);
        },
    },
    async created() {
        try {
            await this.store.fetchFormCategories();
            if (this.sortedCategories.length) await this.selectCategory(this.sortedCategories[0]);
        } catch (error) {
            this.error = error.message || 'Не удалось загрузить категории.';
        } finally {
            this.loading = false;
        }
    },
    methods: {
        prepareDraft(category) {
            const prepared = clone(category);
            prepared.params = {
                is_hidden: false,
                is_private: false,
                can_create: [],
                show_off_grouping: [],
                ...(prepared.params || {}),
            };
            prepared.common_fields = (prepared.common_fields || []).map(field => ({
                required: false,
                showoff: false,
                options: [],
                ...field,
            }));
            return prepared;
        },
        async selectCategory(category) {
            if (this.draft?.id === category.id) return;
            if (this.hasUnsavedChanges && !window.confirm('Отменить несохранённые изменения и открыть другую категорию?')) return;
            this.draft = this.prepareDraft(category);
            this.groupingText = this.draft.params.show_off_grouping.join('\n');
            this.initialSnapshot = JSON.stringify(this.payload());
            this.saved = false;
            this.error = null;
            try {
                this.usage = await fetchFormCategoryUsage(category.id);
            } catch (error) {
                this.usage = null;
                this.error = error.message || 'Не удалось проверить использование категории.';
            }
        },
        startCreate() {
            if (this.hasUnsavedChanges && !window.confirm('Отменить несохранённые изменения и создать новую категорию?')) return;
            this.draft = this.prepareDraft({
                id: null,
                name: '',
                params: {},
                common_fields: [],
                forms: [],
            });
            this.groupingText = '';
            this.usage = null;
            this.saved = false;
            this.error = null;
            this.initialSnapshot = JSON.stringify(this.payload());
        },
        payload() {
            const params = clone(this.draft.params);
            params.show_off_grouping = [...new Set(
                this.groupingText.split('\n').map(value => value.trim()).filter(Boolean)
            )];
            return {
                name: this.draft.name,
                params,
                common_fields: clone(this.draft.common_fields),
            };
        },
        async save() {
            this.saving = true;
            this.saved = false;
            this.error = null;
            try {
                const result = this.draft.id
                    ? await updateFormCategory(this.draft.id, this.payload())
                    : await createFormCategory(this.payload());
                await this.store.fetchFormCategories();
                const savedCategory = this.store.getFormCategory(result.id);
                this.initialSnapshot = JSON.stringify(this.payload());
                await this.selectCategory(savedCategory);
                this.saved = true;
            } catch (error) {
                this.error = error.message || 'Не удалось сохранить категорию.';
            } finally {
                this.saving = false;
            }
        },
        async removeCategory() {
            if (this.hasUsage || !window.confirm(`Удалить категорию «${this.draft.name}»?`)) return;

            this.saving = true;
            this.error = null;
            try {
                const removedId = this.draft.id;
                await deleteFormCategory(removedId);
                this.store.formCategories = this.store.formCategories.filter(category => category.id !== removedId);
                this.draft = null;
                this.usage = null;
                if (this.sortedCategories.length) await this.selectCategory(this.sortedCategories[0]);
            } catch (error) {
                this.error = error.message || 'Не удалось удалить категорию.';
            } finally {
                this.saving = false;
            }
        },
    },
};
</script>

<style scoped>
.category-list {
    top: 4.75rem;
}
</style>
