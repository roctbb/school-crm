<template>
    <div class="card p-2 mb-2">
        <div class="card-body">
            <h5 class="card-title">
                {{ form.name }}
            </h5>
            <p class="card-text">
                Создан: {{ submission.created_at }}
            </p>
            <router-link
                :to="{ name: 'SubmissionDetails', params: { submissionId: submission.id, objectId: object.id }}"
                class="btn btn-primary btn-sm"
            >
                Подробнее
            </router-link>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";

export default {
    name: "SubmissionCard",
    props: {
        submission: {
            type: Object,
            required: true
        },
        object: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            form: null,
            store: useMainStore()
        };
    },
    created() {
        this.form = this.store.getForm(this.submission.form.id)
    }
};
</script>

<style scoped>
.card {
    border: 1px solid #ccc;
}
</style>