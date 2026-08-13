<template>
    <div class="card flex-fill">
        <!-- Основное содержимое карточки -->
        <div class="card-body flex-grow-1 pb-0">
            <h5 class="card-title">{{ form.name }}</h5>
            <button
                v-if="!submission.is_approved && hasTeacherAccess()"
                :class="submission.deleted_at ? 'bg-danger' : 'bg-warning'"
                class="badge border-0 mt-0"
                type="button"
                title="Нажмите, чтобы утвердить"
                @click="handleApprove()"
            >Не подтверждено</button>
            <span
                v-else-if="!submission.is_approved"
                :class="submission.deleted_at ? 'bg-danger' : 'bg-warning'"
                class="badge mt-0"
            >Не подтверждено</span>
            <p v-if="submission.created_at" class="created-at-text">
                {{ formatDateTime(submission.created_at) }}
            </p>

            <ShowoffPresenter :attributes="submission.showoff_attributes"></ShowoffPresenter>
        </div>
        <!-- Кнопка Подробнее -->
        <div class="card-footer mt-auto bg-white border-0">
            <router-link
                :to="{ name: 'SubmissionDetails', params: { submissionId: submission.id, objectId: object.id }}"
                class="btn btn-sm btn-outline-primary"
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
import {hasTeacherAccess} from "@/utils/access.js";

export default {
    name: "SubmissionCard",
    components: {ShowoffPresenter},
    methods: {
        hasTeacherAccess, formatDateTime,
        async handleApprove() {
            const confirmed = confirm("Вы действительно хотите утвердить этот ответ?");
            if (confirmed) {
                await this.submission.approve(this.object.id)
            }
        }
    },
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
    font-size: 0.75rem;
    color: var(--silaeder-muted);
    margin-top: 5px;
    display: flex;
    align-items: center;
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
