<template>
    <BaseLayout>
        <div class="container mt-3">
            <Loading v-if="isLoading"></Loading>
            <div v-else>
                <h3 class="mb-4">
                    {{ isEditMode ? `Редактирование ответа на форму ${form.name} для ${this.object.name}` : `Создание ответа на форму ${form.name} для ${this.object.name}` }}
                </h3>


                <form @submit.prevent="handleSave">
                    <div v-for="(field, idx) in form.fields" :key="idx" class="mb-3">
                        <label :for="'field_'+idx" class="form-label">
                            {{ field.name }}
                            <span v-if="field.required" class="text-danger">*</span>
                        </label>

                        <!-- Поле-строка -->
                        <input
                            v-if="field.type === 'string'"
                            :id="'field_'+idx"
                            type="text"
                            class="form-control"
                            v-model="submission.answers[field.code]"
                            :required="field.required"
                            :placeholder="field.name"
                        />

                        <!-- Поле-текст (textarea) -->
                        <textarea
                            v-else-if="field.type === 'text'"
                            :id="'field_'+idx"
                            class="form-control"
                            v-model="submission.answers[field.code]"
                            :required="field.required"
                            :placeholder="field.name"
                        />

                        <!-- Числовое поле -->
                        <input
                            v-else-if="field.type === 'number'"
                            :id="'field_'+idx"
                            type="number"
                            class="form-control"
                            v-model.number="submission.answers[field.code]"
                            :required="field.required"
                        />

                        <!-- Дата -->
                        <VueDatePicker
                            v-else-if="field.type === 'date'"
                            :id="'field_'+idx"
                            v-model="submission.answers[field.code]"
                            :enable-time-picker="false"
                            :text-input="true"
                            model-type="format"
                            :auto-apply="true"
                            input-class="form-control"
                            locale="ru"
                            format="dd.MM.yyyy"
                        />

                        <!-- Дата/время -->
                        <VueDatePicker
                            v-else-if="field.type === 'datetime'"
                            :id="'field_'+idx"
                            v-model="submission.answers[field.code]"
                            :enable-time-picker="true"
                            :text-input="true"
                            model-type="format"
                            :auto-apply="true"
                            input-class="form-control"
                            locale="ru"
                            format="dd.MM.yyyy HH:mm"
                        />

                        <!-- Выпадающий список -->
                        <select
                            v-else-if="field.type === 'select'"
                            :id="'field_'+idx"
                            class="form-select"
                            v-model="submission.answers[field.code]"
                            :required="field.required"
                        >
                            <option
                                v-for="(option, index) in field.options || []"
                                :key="index"
                                :value="option"
                            >
                                {{ option }}
                            </option>
                        </select>

                        <!-- Одиночный чекбокс -->
                        <div v-else-if="field.type === 'checkbox'" class="form-check">
                            <input
                                type="checkbox"
                                class="form-check-input"
                                :id="'field_'+idx"
                                v-model="submission.answers[field.code]"
                            />
                            <label :for="'field_'+idx" class="form-check-label">
                                {{ field.name }}
                            </label>
                        </div>

                        <!-- Несколько чекбоксов -->
                        <div v-else-if="field.type === 'checkboxes'">
                            <div
                                v-for="(option, boxIndex) in field.options || []"
                                :key="boxIndex"
                                class="form-check mb-1"
                            >
                                <input
                                    class="form-check-input"
                                    type="checkbox"
                                    :id="'field_'+idx+'_'+boxIndex"
                                    :value="option"
                                    v-model="submission.answers[field.code]"
                                />
                                <label
                                    class="form-check-label"
                                    :for="'field_'+idx+'_'+boxIndex"
                                >
                                    {{ option }}
                                </label>
                            </div>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary">
                        Сохранить
                    </button>
                </form>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import Loading from "@/components/common/Loading.vue";
import Submission from "@/models/Submission.js";
import useMainStore from "@/stores/mainStore.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";

export default {
    name: "ManageSubmissionView",
    components: {BaseLayout, Loading, VueDatePicker},
    props: {
        objectId: {
            type: Number,
            required: true
        },
        formId: {
            type: Number,
            required: true
        },
        submissionId: {
            type: Number,
            default: null
        },
        objectTypeCode: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            submission: new Submission(),
            form: null,
            object: null,
            store: useMainStore(),
            isLoading: false
        };
    },
    computed: {
        isEditMode() {
            return !!this.submissionId;
        }
    },
    async created() {
        try {
            this.isLoading = true;
            if (!this.store.objectTypes.length) {
                await this.store.loadObjects();
            }
            this.object = this.store.getObject(this.objectTypeCode, this.objectId)
            this.form = this.store.getForm(this.formId)
            await this.object.loadSubmissions();
        } finally {
            this.isLoading = false;
        }
        if (this.isEditMode) {
            this.submission = this.object._submissions.find(submission => submission.id === parseInt(this.submissionId))
        } else {
            this.submission = new Submission({}, this.store);
            this.fillEmptyAnswers();
        }
    },
    methods: {


        // Заполнить submission.answers пустыми значениями, если форму только создали
        fillEmptyAnswers() {
            if (this.form && Array.isArray(this.form.fields)) {
                this.form.fields.forEach(field => {
                    if (['select', 'checkboxes'].includes(field)) {
                        this.submission.answers[field.code] = []
                    }
                });
            }
        },

        async handleSave() {
            try {
                this.isLoading = true;
                // Метод save() в модели сам определяет, создавать новую запись или обновлять
                await this.submission.save(this.objectId, this.formId);

                if (!this.isEditMode) {
                    this.object._submissions.push(this.submission);
                }
                // Дополнительные действия, например, переход на другую страницу
                this.$router.push(`/${this.objectTypeCode}/${this.objectId}`);
            } finally {
                this.isLoading = false;
            }
        }
    }
};
</script>

<style scoped>
/* При необходимости стили для элементов формы */
</style>