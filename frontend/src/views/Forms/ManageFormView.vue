<template>
    <BaseLayout>
        <div class="container mt-3">
            <Loading v-if="loading"></Loading>
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

                        <draggable
                            v-model="form.fields"
                            tag="div"
                            ghost-class="drag-ghost"
                            handle=".drag-handle"
                            @end="onDragEnd"
                        >
                            <template #item="{ element: field, index }">

                                <div
                                    :key="field.code"
                                    class="border rounded p-3 mb-3"
                                >
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <h6 class="drag-handle" style="cursor: move;"
                                        >Поле {{ index + 1 }}</h6>
                                        <div>
                                            <!-- Кнопки изменения порядка полей -->
                                            <button
                                                type="button"
                                                class="btn btn-secondary btn-sm"
                                                :disabled="index === 0"
                                                @click="moveFieldUp(index)"
                                            >
                                                <i class="bi bi-arrow-up"></i>
                                            </button>
                                            <button
                                                type="button"
                                                class="btn btn-secondary btn-sm ms-1"
                                                :disabled="index === form.fields.length - 1"
                                                @click="moveFieldDown(index)"
                                            >
                                                <i class="bi bi-arrow-down"></i>
                                            </button>
                                            <!-- Кнопка удаления поля (иконка) -->
                                            <button
                                                type="button"
                                                class="btn btn-outline-danger btn-sm ms-1"
                                                @click="removeField(index)"
                                            >
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
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

                                    <!-- Галочка для закрепления -->
                                    <div class="form-check form-switch mb-2">
                                        <input
                                            class="form-check-input"
                                            type="checkbox"
                                            v-model="field.showoff"
                                        />
                                        <label class="form-check-label">
                                            Закрепить на карточке
                                        </label>
                                    </div>

                                    <!-- Если select или checkboxes, даём ввод вариантов -->
                                    <div v-if="field.type === 'select' || field.type === 'checkboxes'">
                                        <label class="form-label">Варианты</label>

                                        <draggable
                                            v-model="field.options"
                                            tag="div"
                                            ghost-class="drag-ghost"
                                            handle=".option-handle"
                                            @end="onOptionsDragEnd(field)"
                                        >
                                            <template #item="{ element: option, index: optIndex }">


                                                <div
                                                    :key="optIndex"
                                                    class="input-group input-group-sm mb-2 d-flex align-items-center"
                                                >

                                                    <span class="option-handle input-group-text"
                                                          style="cursor: move;"><i
                                                        class="bi bi-grip-horizontal"></i></span>


                                                    <input
                                                        type="text"
                                                        class="form-control form-control-sm"
                                                        v-model="field.options[optIndex]"
                                                    />

                                                    <!-- Кнопка удаления варианта (подтверждение) -->
                                                    <button
                                                        type="button"
                                                        class="btn btn-danger btn-sm"
                                                        @click="removeOption(field, optIndex)"
                                                    >
                                                        <i class="bi bi-x"></i>
                                                    </button>

                                                    <!-- Кнопки изменения порядка вариантов -->
                                                    <button
                                                        type="button"
                                                        class="btn btn-outline-secondary btn-sm"
                                                        :disabled="optIndex === 0"
                                                        @click="moveOptionUp(field, optIndex)"
                                                    >
                                                        <i class="bi bi-arrow-up"></i>
                                                    </button>
                                                    <button
                                                        type="button"
                                                        class="btn btn-outline-secondary btn-sm"
                                                        :disabled="optIndex === field.options.length - 1"
                                                        @click="moveOptionDown(field, optIndex)"
                                                    >
                                                        <i class="bi bi-arrow-down"></i>
                                                    </button>
                                                </div>


                                            </template>
                                        </draggable>

                                        <div class="d-flex align-items-center mt-1">
                                            <button
                                                type="button"
                                                class="btn btn-sm btn-light"
                                                @click="addOption(field)"
                                            >
                                                <i class="bi bi-plus"></i>
                                            </button>
                                            <button
                                                type="button"
                                                class="btn btn-sm btn-light ms-2"
                                                @click="sortOptions(field)"
                                            >
                                                <i class="bi bi-sort-alpha-down"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </draggable>


                        <button
                            type="button"
                            class="btn btn-sm btn-light my-2"
                            @click="addField"
                        >
                            <i class="bi bi-plus-circle me-2"></i>Добавить
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
import draggable from 'vuedraggable';
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import useMainStore from "@/stores/mainStore.js";
import Form from "@/models/Form.js";
import Loading from "@/components/common/Loading.vue";

export default {
    name: "ManageFormView",
    components: {
        Loading,
        BaseLayout,
        draggable
    },
    props: {
        formId: {
            type: Number,
            default: null,
            required: false,
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
            return !!this.formId;
        },
    },
    async created() {
        this.loading = true;
        try {
            if (!this.store.formCategories?.length) {
                await this.store.loadObjects();
            }

            this.category = this.store.formCategories.find(
                (cat) => cat.id === parseInt(this.categoryId)
            );

            if (this.isEditMode) {
                this.form = this.category.forms.find(
                    (frm) => frm.id === parseInt(this.formId)
                );
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
        onDragEnd(evt) {
            console.log("Fields reordered:", this.form.fields);
        },
        onOptionsDragEnd(field) {
            console.log("Варианты перетащены:", field.options);
        },

        generateCode() {
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
                showoff: false,
                options: [],
            });
        },
        removeField(index) {
            const confirmed = confirm(
                "Вы уверены, что хотите удалить это поле?"
            );
            if (!confirmed) {
                return;
            }
            this.form.fields.splice(index, 1);
        },
        addOption(field) {
            field.options.push("");
        },
        removeOption(field, optionIndex) {
            const confirmed = confirm(
                "Вы уверены, что хотите удалить этот вариант?"
            );
            if (!confirmed) {
                return;
            }
            field.options.splice(optionIndex, 1);
        },
        // Метод сортировки вариантов по алфавиту
        sortOptions(field) {
            field.options = field.options.slice().sort((a, b) => {
                const valA = (a || "").trim().toLowerCase();
                const valB = (b || "").trim().toLowerCase();
                return valA.localeCompare(valB, "ru");
            });
        },
        // Перемещение поля вверх
        moveFieldUp(index) {
            if (index > 0) {
                const fields = this.form.fields;
                [fields[index - 1], fields[index]] = [fields[index], fields[index - 1]];
            }
        },
        // Перемещение поля вниз
        moveFieldDown(index) {
            if (index < this.form.fields.length - 1) {
                const fields = this.form.fields;
                [fields[index + 1], fields[index]] = [fields[index], fields[index + 1]];
            }
        },
        // Перемещение варианта вверх
        moveOptionUp(field, optIndex) {
            if (optIndex > 0) {
                [field.options[optIndex - 1], field.options[optIndex]] =
                    [field.options[optIndex], field.options[optIndex - 1]];
            }
        },
        // Перемещение варианта вниз
        moveOptionDown(field, optIndex) {
            if (optIndex < field.options.length - 1) {
                [field.options[optIndex + 1], field.options[optIndex]] =
                    [field.options[optIndex], field.options[optIndex + 1]];
            }
        },
        async handleSave() {
            try {
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
            this.form.reset();
            this.$router.push({name: "Forms"});
        },
    },
};
</script>

<style scoped>
.drag-ghost {
    background-color: #f0f0f0;
    opacity: 0.7;
    /* Дополнительные стили для “призрака” перетаскивания */
}
</style>
