<template>
    <BaseLayout>
        <div class="container mt-3">
            <Loading v-if="loading" />
            <div v-else-if="form">
                <h3 class="mb-4">
                    {{ isEditMode ? 'Редактирование формы' : 'Создание формы' }}
                </h3>

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
                        <h5>Поля формы</h5>
                        <FormFieldsEditor v-model="form.fields" />
                    </div>

                    <button class="btn btn-primary" type="submit">
                        {{ isEditMode ? 'Сохранить' : 'Создать' }}
                    </button>
                    <button class="btn btn-secondary ms-2" type="button" @click="cancel">
                        Отмена
                    </button>
                </form>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import Loading from '@/components/common/Loading.vue';
import FormFieldsEditor from '@/components/forms/FormFieldsEditor.vue';
import Form from '@/models/Form.js';
import useMainStore from '@/stores/mainStore.js';

export default {
    name: 'ManageFormView',
    components: {BaseLayout, FormFieldsEditor, Loading},
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
        };
    },
    computed: {
        isEditMode() {
            return Boolean(this.formId);
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
        } catch (error) {
            console.error(error);
            window.alert('Не удалось загрузить форму.');
            await this.$router.push({name: 'Forms'});
        } finally {
            this.loading = false;
        }
    },
    methods: {
        async handleSave() {
            try {
                await this.form.save();
                if (!this.isEditMode) this.category.forms.push(this.form);
                await this.$router.push({name: 'Forms'});
            } catch (error) {
                console.error('Ошибка при сохранении формы:', error);
                window.alert(error.message || 'Не удалось сохранить форму.');
            }
        },
        cancel() {
            this.form.reset();
            this.$router.push({name: 'Forms'});
        },
    },
};
</script>
