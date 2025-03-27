<template>
  <div>
    <div
      v-for="form_category in object_type.form_categories"
      :key="form_category.id"
      class="mb-4"
    >
      <div
        v-if="
          submissionsInCategory(form_category).length ||
          (canFillInCategory(form_category) && canModifyObject(object))
        "
      >
        <h5 class="pb-2">
          {{ form_category.name }}
          <span
            class="badge text-bg-light"
            v-if="form_category.params.is_private"
          >
            Приватный раздел <i class="ms-1 bi bi-eye-slash"></i>
          </span>
          <span
            class="badge text-bg-light"
            v-if="form_category.params.is_hidden"
          >
            Скрытый раздел <i class="ms-1 bi bi-eye-slash"></i>
          </span>
        </h5>
        <div
          v-for="(submissionsGroup, formId) in groupSubmissionsByFormId(
            submissionsInCategory(form_category)
          )"
          :key="formId"
          class="mb-1"
        >
          <div class="row">
            <div
              class="col-md-6 col-lg-4 col-xl-3 col-xl-2 mb-3 d-flex align-items-stretch"
              v-for="submission in submissionsGroup"
              :key="submission.id"
            >
              <SubmissionCard :submission="submission" :object="object" />
            </div>
          </div>
        </div>
        <div
          class="btn-group"
          v-if="canFillInCategory(form_category) && canModifyObject(object)"
        >
          <button
            class="btn btn-sm btn-light dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            Добавить
          </button>
          <ul class="dropdown-menu">
            <li
              v-for="form in store.getFormCategory(form_category.id).forms"
              :key="form.id"
            >
              <a
                class="dropdown-item"
                href="#"
                @click.prevent="goToCreateSubmission(form.id)"
              >
                {{ form.name }}
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <!-- Внешние категории -->
    <div
      v-for="(category_name, i) in externalCategories"
      :key="i"
      class="mb-2"
    >
      <h5 class="pb-2">{{ category_name }}</h5>
      <div class="row">
        <div
          class="col-md-6 col-lg-4 col-xl-3 col-xl-2 mb-4 d-flex align-items-stretch"
          v-for="submission in object._submissions.filter(
            s => s.form.category === category_name
          )"
          :key="submission.id"
        >
          <SubmissionCard :submission="submission" :object="object" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import SubmissionCard from "@/components/submissions/SubmissionCard.vue";
import {
  canFillInCategory,
  canModifyObject
} from "@/utils/access.js";

export default {
  name: "FormsSubmissions",
  components: {
    SubmissionCard
  },
  props: {
    object: {
      type: Object,
      required: true
    },
    object_type: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      store: useMainStore()
    };
  },
  computed: {
    externalCategories() {
      const categories = this.object._submissions
        .filter(submission => submission.form.is_external)
        .map(submission => submission.form.category);
      return [...new Set(categories)];
    }
  },
  methods: {
    submissionsInCategory(category) {
      return this.object._submissions.filter(
        submission => submission._form.category_id === category.id
      );
    },
    groupSubmissionsByFormId(submissions) {
      return submissions.reduce((groups, submission) => {
        const formId = submission.form.id;
        if (!groups[formId]) {
          groups[formId] = [];
        }
        groups[formId].push(submission);
        return groups;
      }, {});
    },
    canFillInCategory(category) {
      return canFillInCategory(category);
    },
    canModifyObject(object) {
      return canModifyObject(object);
    },
    goToCreateSubmission(formId) {
      this.$emit("create-submission", formId);
    }
  }
};
</script>