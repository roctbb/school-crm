<template>
    <article class="card submission-card flex-fill">
        <div class="card-body flex-grow-1">
            <div class="submission-card-heading">
                <h5 class="card-title mb-0">{{ form.name }}</h5>
                <time v-if="submission.created_at" class="created-at-text">
                    {{ formatDateTime(submission.created_at) }}
                </time>
            </div>
            <button
                v-if="!submission.is_approved && hasTeacherAccess()"
                :class="submission.deleted_at ? 'bg-danger' : 'bg-warning'"
                class="badge border-0 mt-2 submission-approve-action"
                type="button"
                title="Нажмите, чтобы утвердить"
                @click="handleApprove()"
            >Не подтверждено</button>
            <span
                v-else-if="!submission.is_approved"
                :class="submission.deleted_at ? 'bg-danger' : 'bg-warning'"
                class="badge mt-2"
            >Не подтверждено</span>

            <ShowoffPresenter
                class="submission-attributes"
                :attributes="submission.showoff_attributes"
                :hidden-attributes="hiddenAttributes"
            />
            <router-link
                :to="{
                    name: 'SubmissionDetails',
                    params: {
                        object_type: object.type,
                        object_id: object.id,
                        submissionId: submission.id
                    }
                }"
                class="stretched-link"
                :aria-label="`Открыть запись «${form.name}»`"
            >
                <span class="visually-hidden">Открыть</span>
            </router-link>
        </div>
    </article>
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
        hiddenAttributes: {
            type: Array,
            default: () => [],
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
.submission-card {
    min-height: 10rem;
    border-radius: 0.75rem;
    cursor: pointer;
    transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}

.submission-card:hover {
    border-color: #bfd2dc;
    box-shadow: var(--silaeder-shadow);
    transform: translateY(-1px);
}

.submission-card:focus-within {
    border-color: var(--silaeder-primary);
    box-shadow: 0 0 0 0.2rem rgb(57 118 152 / 18%);
}

.submission-card-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.75rem;
}

.card-title {
    min-width: 0;
    font-size: 1rem;
    line-height: 1.3;
    overflow-wrap: anywhere;
}

.created-at-text {
    flex: 0 0 auto;
    font-size: 0.75rem;
    color: var(--silaeder-muted);
    line-height: 1.3;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}

.submission-attributes {
    margin-top: 1rem;
}

.submission-approve-action {
    position: relative;
    z-index: 2;
}

@media (max-width: 575.98px) {
    .submission-card-heading {
        display: grid;
    }
}
</style>
