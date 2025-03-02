<template>
    <BaseLayout>
        <div class="container mt-3">
            <Loading v-if="!form"></Loading>
            <div v-else>
                <h3 class="mb-4">
                    {{ isEditMode ? "Редактирование формы" : "Создание формы" }}
                </h3>

                <form @submit.prevent="handleSave">
                    <!-- Название формы -->
                    <div class="mb-3">
                        <label class="form-label">Название формы</label>
                        <input
                            class="form-control"
                            type="text"
                            v-model="form.name"
                            placeholder="Введите название"
                            required
                        />
                    </div>

                    <!-- Редактор полей -->
                    <div class="mb-3">
                        <h5>Поля формы</h5>


                        <div
                            v-for="(field, index) in this.form.fields"
                            :key="field.code"
                            class="border rounded p-3 mb-3"
                        >
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6>Поле {{ index + 1 }}</h6>
                                <button
                                    type="button"
                                    class="btn btn-outline-danger btn-sm"
                                    @click="removeField(index)"
                                >
                                    Удалить
                                </button>
                            </div>

                            <div class="row g-3 mb-2">
                                <!-- Название поля -->
                                <div class="col-8">
                                    <label class="form-label">Название</label>
                                    <input
                                        type="text"
                                        class="form-control"
                                        v-model="field.name"
                                        required
                                    />
                                </div>
                                <!-- Тип поля -->
                                <div class="col-4">
                                    <label class="form-label">Тип</label>
                                    <select
                                        class="form-select"
                                        v-model="field.type"
                                        required
                                    >
                                        <option value="number">number</option>
                                        <option value="string">string</option>
                                        <option value="text">text</option>
                                        <option value="date">date</option>
                                        <option value="datetime">datetime</option>
                                        <option value="select">select</option>
                                        <option value="checkboxes">checkboxes</option>
                                        <option value="checkbox">checkbox</option>
                                    </select>
                                </div>
                            </div>

                            <!-- Признак обязательности -->
                            <div class="form-check form-switch mb-2">
                                <input
                                    class="form-check-input"
                                    type="checkbox"
                                    v-model="field.required"
                                />
                                <label class="form-check-label">
                                    Обязательное поле
                                </label>
                            </div>

                            <!-- Если select или checkboxes, даём ввод options -->
                            <div v-if="field.type === 'select' || field.type === 'checkboxes'">
                                <label class="form-label">Варианты</label>
                                <div
                                    v-for="(option, optIndex) in field.localOptions"
                                    :key="optIndex"
                                    class="input-group mb-2"
                                >
                                    <input
                                        type="text"
                                        class="form-control"
                                        v-model="field.localOptions[optIndex]"
                                    />
                                    <button
                                        type="button"
                                        class="btn btn-danger"
                                        @click="removeOption(field, optIndex)"
                                    >
                                        Удалить
                                    </button>
                                </div>

                                <button
                                    type="button"
                                    class="btn btn-sm btn-light"
                                    @click="addOption(field)"
                                >
                                    <i class="bi bi-plus me-1"></i>
                                    Добавить вариант
                                </button>
                            </div>

                        </div>

                        <button
                            type="button"
                            class="btn btn-sm btn-light my-2"
                            @click="addField"
                        >
                            <i class="bi bi-plus me-1"></i> Добавить поле
                        </button>
                    </div>

                    <!-- Кнопки -->
                    <button class="btn btn-primary" type="submit">
                        {{ isEditMode ? "Сохранить" : "Создать" }}
                    </button>
                    <button
                        class="btn btn-secondary ms-2"
                        type="button"
                        @click="cancel"
                    >
                        Отмена
                    </button>
                </form>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import useMainStore from "@/stores/mainStore.js";
import Form from "@/models/Form.js";
import Loading from "@/components/common/Loading.vue";

export default {
    name: "ManageFormView",
    components: {
        Loading,
        BaseLayout,
    },
    props: {
        // ID существующей формы (если редактирование). Если null — создаём новую.
        formId: {
            type: Number,
            default: null,
            required: false
        },
        // При необходимости можем прокинуть categoryId
        categoryId: {
            type: Number,
            default: null,
        },
    },
    data() {
        return {
            loading: false,
            form: null,        // Экземпляр модели Form
            category: null,
            store: useMainStore()
        };
    },
    computed: {
        isEditMode() {
            return !!this.formId;
        },
    },
    async created() {
        this.loading = true;

        try {
            // Убедимся, что данные форм загружены
            if (!this.store.formCategories?.length) {
                await this.store.loadObjects();
            }

            this.category = this.store.formCategories.find(
                (cat) => cat.id === parseInt(this.categoryId)
            );

            // Режим редактирования
            if (this.isEditMode) {
                // Ищем форму среди загруженных категорий и форм
                // Предположим, что есть удобный метод или вручную ищем:

                this.form = this.category.forms.find(
                    (form) => form.id === parseInt(this.formId)
                )
                if (!this.form) {
                    throw new Error("Форма с указанным ID не найдена.");
                }
            } else {
                this.form = new Form({}, this.store, this.categoryId);
            }

        } catch (err) {
            console.error(err);
            alert("Не удалось загрузить форму");
        } finally {
            this.loading = false;
        }
    },
    methods: {
        generateCode() {
            // Простейший генератор для кода поля
            return (
                Math.random().toString(36).substring(2, 15) +
                Math.random().toString(36).substring(2, 15)
            );
        },
        addField() {
            this.form.fields.push({
                name: "",
                code: this.generateCode(),
                type: "text",
                required: false,
                options: [],
            });
        },
        removeField(index) {
            this.form.fields.splice(index, 1);
        },
        addOption(field) {
            field.options.push("");
        },
        removeOption(field, optionIndex) {
            field.options.splice(optionIndex, 1);
        },
        async handleSave() {
            try {
                // Сохраняем (create или update)
                await this.form.save();

                if (!this.isEditMode) {
                    this.category.forms.push(this.form);
                }

                this.$router.push({name: "Forms"});
            } catch (error) {
                console.error("Ошибка при сохранении формы:", error);
                alert("Не удалось сохранить форму.");
            }
        },
        cancel() {
            // Возврат без сохранения
            this.form.reset();
            this.$router.push({name: "Forms"});

        },

    },
};
</script>

<style scoped>
/* При необходимости можно добавить стили */
</style>