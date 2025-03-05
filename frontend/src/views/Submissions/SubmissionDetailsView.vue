<template>
    <BaseLayout>
        <div class="container mt-3" v-if="submission">
            <!-- Верхняя панель с названием и кнопками -->
            <div class="d-flex align-items-center mb-4">
                <router-link
                    :to="`/${objectTypeCode}/${objectId}`"
                    class="btn btn-sm btn-outline-secondary me-3"
                >
                    <i class="bi bi-arrow-left"></i> Назад
                </router-link>
                <h3 class="mb-0 flex-grow-1">Ответ на форму: {{ form.name }}</h3>

                <!-- Кнопки действий -->
                <div>
                    <div class="dropdown">
                        <button
                            class="btn btn-light dropdown-toggle"
                            type="button"
                            id="actionsMenu"
                            data-bs-toggle="dropdown"
                            aria-expanded="false"
                        >
                            Действия
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="actionsMenu">
                            <!-- Редактирование -->
                            <li>
                                <router-link
                                    :to="{
                                        name: 'EditSubmission',
                                        params: {
                                            objectTypeCode: objectTypeCode,
                                            objectId: objectId,
                                            submissionId: submission.id,
                                        }
                                    }"
                                    class="dropdown-item"
                                >
                                    <i class="bi bi-pencil"></i> Редактировать
                                </router-link>
                            </li>

                            <!-- Удаление -->
                            <li>
                                <button
                                    class="dropdown-item text-danger"
                                    @click="handleDelete"
                                >
                                    <i class="bi bi-trash"></i> Удалить
                                </button>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Дата создания -->
            <p v-if="submission.created_at" class="created-at-text">
                <i class="bi bi-calendar3"></i> Отправлено: {{ formatDateTime(submission.created_at) }}
            </p>

            <!-- Ответы -->
            <div class="submission-answers mt-4">
                <h5>Ответы</h5>
                <ul>
                    <li v-for="(value, key) in submission.answers" :key="key">
                        <strong>{{ getFieldName(key) }}:</strong>
                        <span>{{ formatAnswer(value) }}</span>
                    </li>
                </ul>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import { formatDateTime } from "@/utils/helpers.js";
import useMainStore from "@/stores/mainStore.js";
import { deleteSubmission } from "@/api/submissions_api.js";

export default {
    name: "SubmissionDetailsView",
    components: { BaseLayout },
    props: {
        submissionId: {
            type: Number,
            required: true,
        },
        objectId: {
            type: Number,
            required: true,
        },
        objectTypeCode: {
            type: String,
            required: true,
        },
    },
    data() {
        return {
            submission: null,
            form: null,
            object: null,
            store: useMainStore(),
            isLoading: false,
        };
    },
    async created() {
        this.isLoading = true;
        try {
            // Загружаем объект, форму и submission из хранилища
            if (!this.store.objectTypes.length) {
                await this.store.loadObjects();
            }
            this.object = this.store.getObject(this.objectTypeCode, this.objectId);
            await this.object.loadSubmissions();
            this.submission = this.object._submissions.find(
                (submission) => submission.id === parseInt(this.submissionId)
            );
            this.form = this.store.getForm(this.submission.form.id);
        } finally {
            this.isLoading = false;
        }
    },
    methods: {
        formatDateTime, // Форматируем дату через общий хелпер

        // Получить название поля из формы по коду
        getFieldName(code) {
            const field = this.form.fields.find((f) => f.code === code);
            return field ? field.name : code;
        },

        // Форматировать ответ (массивы, текст, даты)
        formatAnswer(value) {
            if (Array.isArray(value)) {
                return value.join(", "); // Если массив — объединяем через запятую
            }
            return value || "Нет данных"; // Если пусто, выводим текст
        },

        async handleDelete() {
            const confirmed = confirm("Вы действительно хотите удалить этот ответ?");
            if (confirmed) {
                try {
                    await deleteSubmission(this.objectId, this.submission.id);
                    this.object._submissions = this.object._submissions.filter(
                        (sub) => sub.id !== this.submission.id
                    );
                    this.$router.push(`/${this.objectTypeCode}/${this.objectId}`);
                } catch (error) {
                    console.error("Ошибка при удалении:", error);
                    alert("Не удалось удалить ответ.");
                }
            }
        },
    },
};
</script>

<style scoped>
.created-at-text {
    font-size: 0.95rem;
    color: #6c757d;
    margin-top: 5px;
    display: flex;
    align-items: center;
}

.created-at-text i {
    font-size: 1rem;
    margin-right: 5px;
}

.submission-answers ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.submission-answers li {
    margin-bottom: 10px;
    font-size: 1rem;
    line-height: 1.5;
}

.submission-answers strong {
    color: #343a40;
}

.submission-answers span {
    color: #495057;
}
</style>