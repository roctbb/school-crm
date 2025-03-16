<template>
    <div class="card flex-fill">
        <!-- Основное содержимое карточки -->
        <div class="card-body flex-grow-1 pb-0">
            <h5 class="card-title">{{ form.name }}</h5>
            <div class="badge bg-warning mt-0" v-if="!submission.is_approved">Не подтверждено</div>
            <p v-if="submission.created_at" class="created-at-text">
                {{ formatDateTime(submission.created_at) }}
            </p>

            <ShowoffPresenter :attributes="submission.showoff_attributes"></ShowoffPresenter>
        </div>
        <!-- Кнопка Подробнее -->
        <div class="mt-auto py-3 ps-3">
            <router-link
                :to="{ name: 'SubmissionDetails', params: { submissionId: submission.id, objectId: object.id }}"
                class="btn btn-sm btn-light"
            >
                Подробнее
            </router-link>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import {formatDateTime} from "@/utils/helpers.js";
import ShowoffPresenter from "@/components/submissions/ShowoffPresenter.vue";

export default {
    name: "SubmissionCard",
    components: {ShowoffPresenter},
    methods: {formatDateTime},
    props: {
        submission: {
            type: Object,
            required: true,
        },
        object: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            form: null,
            store: useMainStore(),
        };
    },
    created() {
        this.form = this.submission.form;
    },
};
</script>

<style scoped>
/* Стили текста даты создания */
.created-at-text {
    font-size: 0.75rem; /* Маленький размер текста */
    color: #6c757d; /* Серый цвет */
    margin-top: 5px; /* Отступ сверху от названия */
    display: flex; /* Используем флекс для выравнивания иконки и текста */
    align-items: center; /* Выравнивание по центру */
}

.created-at-text i {
    font-size: 0.875rem; /* Размер иконки чуть больше текста */
    margin-right: 5px; /* Отступ справа от иконки */
}

ul {
    list-style-type: none; /* Убирает стандартные маркеры */
    padding: 0 !important; /* Убирает отступы */
    margin: 0; /* Убирает внешние отступы */
}

li {
    margin: 0; /* Убирает внешние отступы у элементов списка */
    padding: 0; /* Убирает внутренние отступы у элементов списка */
}
</style>