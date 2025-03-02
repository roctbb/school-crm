<template>
    <BaseLayout>
        <div v-if="submission">
            <h3>Детали ответа</h3>
            <p><strong>Ответ на форму:</strong> {{ submission.form?.name }}</p>
            <p><strong>Автор:</strong> {{ submission.creator?.name }}</p>
            <p><strong>Дата создания:</strong> {{ submission.created_at }}</p>

            <hr/>
            <h4>Ответы на поля формы:</h4>
            <div
                v-for="(value, key) in submission.answers"
                :key="key"
                class="mb-2"
            >
                <strong>{{ key }}:</strong> {{ value }}
            </div>

            <div class="mt-3">
                <button class="btn btn-secondary" @click="goBack">
                    Назад
                </button>
            </div>
        </div>
        <div v-else>
            <Loading/>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";

export default {
    name: "SubmissionDetailsView",
    components: {
        BaseLayout,
        Loading
    },
    props: {
        objectId: {
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
            isLoading: false,
        };
    },

    async created() {
        try {
            this.isLoading = true;
            if (!this.store.objectTypes.length) {
                await this.store.loadObjects();
            }
            this.object = this.store.getObject(this.objectTypeCode, this.objectId);
            this.form = this.store.getForm(this.formId);
            await this.object.loadSubmissions();
            this.submission = this.object._submissions.find(
                (submission) => submission.id === parseInt(this.submissionId)
            );
        } finally {
            this.isLoading = false;
        }
    },
    methods: {
        goBack() {
            this.$router.go(-1);
        }
    }
};
</script>

<style scoped>
.mb-2 {
    margin-bottom: 0.5rem;
}
</style>