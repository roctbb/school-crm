<template>
    <BaseLayout>
        <div class="container mt-3">
            <Loading v-if="isLoading"></Loading>
            <div v-else>
                <h3 class="mb-4">
                    {{
                        isEditMode ? `Редактирование ответа на форму ${form.name} для ${this.object.name}` : `Создание ответа на форму ${form.name} для ${this.object.name}`
                    }}
                </h3>


                <form @submit.prevent="handleSave">
                    <div v-for="(field, idx) in submission.fields" :key="idx" class="mb-3">
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
                            v-model="field.answer"
                            :required="field.required"
                            :placeholder="field.name"
                        />

                        <!-- Поле-текст (textarea) -->
                        <textarea
                            v-else-if="field.type === 'text'"
                            :id="'field_'+idx"
                            class="form-control"
                            v-model="field.answer"
                            :required="field.required"
                            :placeholder="field.name"
                        />

                        <!-- Числовое поле -->
                        <input
                            v-else-if="field.type === 'number'"
                            :id="'field_'+idx"
                            type="number"
                            class="form-control"
                            v-model.number="field.answer"
                            :required="field.required"
                        />

                        <!-- Дата -->
                        <VueDatePicker
                            v-else-if="field.type === 'date'"
                            :id="'field_'+idx"
                            v-model="field.answer"
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
                            v-model="field.answer"
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
                            v-model="field.answer"
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
                                v-model="field.answer"
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
                                    v-model="field.answer"
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

                    <div class="accordion my-3" id="brothersAccordion">
                        <div class="accordion-item">
                            <h5 class="accordion-header" id="headingFilter">
                                <button
                                    class="accordion-button collapsed p-2 bg-light"
                                    type="button"
                                    data-bs-toggle="collapse"
                                    data-bs-target="#collapseFilter"
                                    aria-expanded="false"
                                    aria-controls="collapseFilter"
                                >
                                    Дублировать для...
                                </button>
                            </h5>
                            <div
                                id="collapseFilter"
                                class="accordion-collapse collapse"
                                aria-labelledby="headingFilter"
                                data-bs-parent="#brothersAccordion"
                            >
                                <div class="accordion-body p-2">
                                    <div v-if="!isEditMode">
                                        <ChildrenFilterEditor
                                            v-model:children="attached_brothers"
                                            :group="object_type"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>


                    <button type="submit" class="btn btn-primary me-1">
                        Сохранить
                    </button>
                    <button type="submit" class="btn btn-secondary" @click="cancel">
                        Назад
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
import ChildrenFilterEditor from "@/components/objects/ChildrenFilterEditor.vue";
import {getAcademicYear} from "@/utils/helpers.js";

export default {
    name: "ManageSubmissionView",
    components: {ChildrenFilterEditor, BaseLayout, Loading, VueDatePicker},
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
            submission: null,
            form: null,
            object: null,
            store: useMainStore(),
            isLoading: false,
            object_type: {},
            attached_brothers: [],
        };
    },
    computed: {
        isEditMode() {
            return !!this.submissionId;
        }
    },
    async created() {
        this.isLoading = true;
        if (!this.store.objectTypes.length) {
            await this.store.loadObjects();
        }
        this.object = this.store.getObject(this.objectTypeCode, this.objectId)

        if (this.isEditMode) {
            await this.object.loadSubmissions();
            this.submission = this.object._submissions.find(submission => submission.id === parseInt(this.submissionId))
            this.form = this.submission._form;
        } else {
            this.form = this.store.getForm(this.formId)
            this.submission = new Submission({}, this.store, this.form);
            this.object_type = this.store.getObjectTypeByCode(this.object.type)
            this.attached_brothers.push(this.object.asChild())
            this.fillEmptyAnswers();
        }

        this.isLoading = false;
    },
    methods: {


        // Заполнить submission.answers пустыми значениями, если форму только создали
        fillEmptyAnswers() {
            if (this.submission) {
                this.submission.fields.forEach(field => {
                    if (['select', 'checkboxes'].includes(field.type)) {
                        field.answer = []
                    }
                    if (field.default === 'current_learn_year') {
                        field.answer = getAcademicYear()
                    }
                    if (field.default === 'class' && this.object.attributes.class) {
                        field.answer = this.object.attributes.class
                    }
                });
            }
        },

        async handleSave() {
            try {
                this.isLoading = true;
                // Метод save() в модели сам определяет, создавать новую запись или обновлять
                let submission_template = this.submission.copy()
                await this.submission.save(this.objectId, this.formId);

                if (!this.isEditMode) {
                    this.object._submissions.push(this.submission);

                    for (let brother of this.attached_brothers) {
                        if (brother.id !== this.objectId) {
                            let brother_submission = submission_template.copy()
                            console.log("copy is", brother_submission.copy())
                            await brother_submission.save(brother.id, this.formId);
                            let brother_object = this.store.getObject(brother.type, brother.id)
                            await brother_object.loadSubmissions()
                            brother_object._submissions.push(brother_submission);
                        }
                    }
                }

                // Дополнительные действия, например, переход на другую страницу
                this.$router.push(`/${this.objectTypeCode}/${this.objectId}`);
            } finally {
                this.isLoading = false;
            }
        },
        cancel() {
            this.submission.reset();
            this.$router.back();
        },


    }
};
</script>

<style scoped>
/* При необходимости стили для элементов формы */
</style>