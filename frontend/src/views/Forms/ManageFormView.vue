<template>
    <BaseLayout>
            <Loading v-if="loading" />
            <div v-else-if="form">
                <PageHeader
                    :title="isEditMode ? 'Редактирование формы' : 'Создание формы'"
                    :subtitle="`Категория: ${category.name}`"
                />

                <div v-if="error" class="alert alert-danger">{{ error }}</div>

                <form @submit.prevent="handleSave">
                    <div class="mb-3">
                        <label class="form-label">Название формы</label>
                        <input
                            v-model.trim="form.name"
                            class="form-control"
                            type="text"
                            maxlength="100"
                            placeholder="Введите название"
                            required
                        />
                    </div>

                    <div class="mb-4">
                        <label class="form-label" for="card-format">Отображение на странице объекта</label>
                        <select id="card-format" v-model="form.card_format" class="form-select">
                            <option value="default">Обычная карточка</option>
                            <option value="session_results">Результаты сессии</option>
                        </select>
                        <div class="form-text">
                            Сессионная карточка показывает предметы как компактную ведомость и рассчитывает средний балл.
                        </div>
                    </div>

                    <div class="mb-4">
                        <h5>Поля формы</h5>
                        <FormFieldsEditor v-model="form.fields" />
                    </div>

                    <div class="editor-save-bar">
                        <button class="btn btn-light" type="button" @click="cancel">Отмена</button>
                        <div class="d-flex align-items-center gap-3">
                            <span v-if="hasUnsavedChanges" class="small text-warning-emphasis d-none d-sm-inline">
                                Есть несохранённые изменения
                            </span>
                            <button class="btn btn-primary" type="submit">
                                {{ isEditMode ? 'Сохранить' : 'Создать' }}
                            </button>
                        </div>
                    </div>
                </form>
            </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import Loading from '@/components/common/Loading.vue';
import FormFieldsEditor from '@/components/forms/FormFieldsEditor.vue';
import Form from '@/models/Form.js';
import useMainStore from '@/stores/mainStore.js';
import PageHeader from '@/components/common/PageHeader.vue';
import unsavedChangesMixin from '@/mixins/unsavedChangesMixin.js';

export default {
    name: 'ManageFormView',
    components: {BaseLayout, FormFieldsEditor, Loading, PageHeader},
    mixins: [unsavedChangesMixin],
    props: {
        formId: {
            type: Number,
            default: null,
        },
        categoryId: {
            type: Number,
            default: null,
        },
    },
    data() {
        return {
            loading: false,
            form: null,
            category: null,
            store: useMainStore(),
            error: '',
            initialSnapshot: '',
        };
    },
    computed: {
        isEditMode() {
            return Boolean(this.formId);
        },
        hasUnsavedChanges() {
            return Boolean(this.form && this.initialSnapshot && this.formSnapshot() !== this.initialSnapshot);
        },
    },
    async created() {
        this.loading = true;
        try {
            if (!this.store.formCategories?.length) await this.store.loadObjects();

            this.category = this.store.formCategories.find(category => (
                category.id === Number(this.categoryId)
            ));
            if (!this.category) throw new Error('Категория с указанным ID не найдена.');

            if (this.isEditMode) {
                this.form = this.category.forms.find(form => form.id === Number(this.formId));
                if (!this.form) throw new Error('Форма с указанным ID не найдена.');
            } else {
                this.form = new Form({}, this.store, this.categoryId);
            }
            this.initialSnapshot = this.formSnapshot();
        } catch (error) {
            console.error(error);
            window.alert('Не удалось загрузить форму.');
            await this.$router.push({name: 'Forms'});
        } finally {
            this.loading = false;
        }
    },
    methods: {
        formSnapshot() {
            return JSON.stringify({
                name: this.form?.name || '',
                card_format: this.form?.card_format || 'default',
                fields: this.form?.fields || [],
            });
        },
        async handleSave() {
            try {
                this.error = '';
                await this.form.save();
                if (!this.isEditMode) this.category.forms.push(this.form);
                this.initialSnapshot = this.formSnapshot();
                await this.$router.push({name: 'Forms'});
            } catch (error) {
                console.error('Ошибка при сохранении формы:', error);
                this.error = error.message || 'Не удалось сохранить форму.';
            }
        },
        cancel() {
            this.form.reset();
            this.initialSnapshot = this.formSnapshot();
            this.$router.push({name: 'Forms'});
        },
    },
};
</script>
