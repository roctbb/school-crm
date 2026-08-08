<template>
    <BaseLayout>
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h2 class="mb-1">Категории форм</h2>
                    <p class="text-muted mb-0">Общие поля, доступ и отображение форм.</p>
                </div>
                <button class="btn btn-success" type="button" @click="startCreate">
                    <i class="bi bi-plus-lg me-1"></i> Новая категория
                </button>
            </div>

            <Loading v-if="loading" />
            <div v-else class="row g-3">
                <div class="col-lg-3">
                    <div class="list-group sticky-lg-top category-list">
                        <button
                            v-for="category in sortedCategories"
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
                    </div>
                </div>

                <div class="col-lg-9">
                    <div v-if="!draft" class="alert alert-light border">
                        Выберите категорию или создайте новую.
                    </div>
                    <form v-else @submit.prevent="save">
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div v-if="saved" class="alert alert-success">Изменения сохранены.</div>

                        <div v-if="usage" class="card mb-3">
                            <div class="card-body py-2 d-flex flex-wrap gap-3">
                                <span><b>{{ usage.form_count }}</b> активных форм</span>
                                <span><b>{{ usage.object_type_count }}</b> типов сущностей</span>
                                <span v-if="usage.child_category_count">
                                    <b>{{ usage.child_category_count }}</b> дочерних категорий
                                </span>
                            </div>
                        </div>

                        <div class="card mb-3">
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

                        <div class="card mb-3">
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

                        <div class="card mb-3">
                            <div class="card-header">Общие поля</div>
                            <div class="card-body">
                                <p class="text-muted small">
                                    Эти поля автоматически добавляются во все формы категории.
                                </p>
                                <FormFieldsEditor v-model="draft.common_fields" />
                            </div>
                        </div>

                        <div class="d-flex justify-content-between gap-2 mb-5">
                            <button
                                v-if="draft.id"
                                class="btn btn-outline-danger"
                                type="button"
                                :disabled="saving || hasUsage"
                                :title="deleteHint"
                                @click="removeCategory"
                            >
                                <i class="bi bi-trash me-1"></i> Удалить
                            </button>
                            <span v-else></span>
                            <button class="btn btn-primary" type="submit" :disabled="saving">
                                {{ saving ? 'Сохранение…' : (draft.id ? 'Сохранить' : 'Создать') }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import Loading from '@/components/common/Loading.vue';
import FormFieldsEditor from '@/components/forms/FormFieldsEditor.vue';
import {
    createFormCategory,
    deleteFormCategory,
    fetchFormCategoryUsage,
    updateFormCategory,
} from '@/api/forms_api.js';
import useMainStore from '@/stores/mainStore.js';

const clone = value => JSON.parse(JSON.stringify(value));

export default {
    name: 'FormCategoriesAdminView',
    components: {BaseLayout, FormFieldsEditor, Loading},
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
            this.draft = this.prepareDraft(category);
            this.groupingText = this.draft.params.show_off_grouping.join('\n');
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
    top: 1rem;
}
</style>
