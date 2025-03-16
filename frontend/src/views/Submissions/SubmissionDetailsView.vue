<template>
    <BaseLayout>
        <div class="container mt-4" v-if="submission && !isLoading">
            <div class="row justify-content-center">
                <div class="col-md-10 col-lg-8">
                    <!-- Карточка с деталями ответа  -->
                    <div class="card">
                        <div class="card-header d-flex align-items-center justify-content-between">
                            <div class="d-flex align-items-center">
                                <BackButton />

                                <h4 class="m-0">
                                    Ответ на форму:
                                    <span class="text-primary">{{ submission.form.name }}</span>
                                </h4>
                            </div>
                            <!-- Меню действий -->
                            <div class="dropdown" v-if="canModifySubmission(submission)">
                                <button
                                    class="btn btn-light dropdown-toggle"
                                    type="button"
                                    id="actionsMenu"
                                    data-bs-toggle="dropdown"
                                    aria-expanded="false"
                                >
                                    Действия
                                </button>
                                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="actionsMenu">
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
                                            <i class="bi bi-pencil me-1"></i> Редактировать
                                        </router-link>
                                    </li>
                                    <li v-if="!submission.is_approved && hasTeacherAccess()">
                                        <button class="dropdown-item" @click="handleApprove">
                                            <i class="bi bi-check-circle text-success me-1"></i> Утвердить
                                        </button>
                                    </li>
                                    <li>
                                        <button
                                            class="dropdown-item text-danger"
                                            @click="handleDelete"
                                        >
                                            <i class="bi bi-trash me-1"></i> Удалить
                                        </button>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="card-body">
                            <!-- Дата создания -->
                            <p v-if="submission.created_at" class="text-muted mb-4">
                                <i class="bi bi-calendar3 me-1"></i>
                                Отправлено: {{ formatDateTime(submission.created_at) }}

                                <span class="badge bg-warning ms-1"
                                      v-if="!submission.is_approved">Не подтверждено</span>
                            </p>


                            <!-- Таблица с ответами -->
                            <div class="submission-answers">
                                <h5 class="mb-3">Ответы</h5>
                                <table class="table table-sm table-bordered table-hover align-middle">
                                    <thead class="table-light">
                                    <tr>
                                        <th style="width: 30%">Название поля</th>
                                        <th>Ответ</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    <tr
                                        v-for="(field, i) in submission.fields.filter(field => field.answer)"
                                        :key="i"
                                    >
                                        <td>{{ field.name }}</td>
                                        <td>{{ formatValue(field.answer) }}</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Индикатор загрузки -->
        <div v-else class="mt-5 text-center">
            <Loading/>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import {formatDateTime, formatValue} from "@/utils/helpers.js";
import useMainStore from "@/stores/mainStore.js";
import {deleteSubmission} from "@/api/submissions_api.js";
import Loading from "@/components/common/Loading.vue";
import {canModifySubmission, hasTeacherAccess} from "@/utils/access.js";
import BackButton from "@/components/common/BackButton.vue";

export default {
    name: "SubmissionDetailsView",
    components: {BackButton, BaseLayout, Loading},
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
            if (!this.store.objectTypes.length) {
                await this.store.loadObjects();
            }
            this.object = this.store.getObject(
                this.objectTypeCode,
                this.objectId
            );
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
        hasTeacherAccess,
        canModifySubmission,
        formatValue,
        formatDateTime,
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
        async handleApprove() {
            const confirmed = confirm("Вы действительно хотите утвердить этот ответ?");
            if (confirmed) {
                await this.submission.approve(this.object.id)
            }
        }
    },
};
</script>

<style scoped>
.table th, .table td {
    vertical-align: middle !important;
}
</style>