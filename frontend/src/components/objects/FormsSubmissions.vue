<template>
  <div class="forms-submissions-stack">
    <div
      v-for="form_category in object_type.form_categories"
      :key="form_category.id"
      class="form-category-section"
    >
      <div
        v-if="
          submissionsInCategory(form_category).length ||
          (canFillInCategory(form_category) && canModifyObject(object))
        "
      >
        <div class="d-flex flex-wrap align-items-center mb-3 section-heading">
          <h5 class="pb-0 mb-0 me-3">
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
          
          <!-- Tabs for show_off_grouping if present -->
          <div v-if="hasShowOffGrouping(form_category)" class="group-tabs ms-sm-auto mt-2 mt-sm-0">
            <ul class="nav nav-tabs flex-nowrap">
              <li class="nav-item" v-for="(group, index) in getGroupingValues(form_category)" :key="index">
                <button 
                  class="nav-link" 
                  :class="{ active: isActiveGroup(form_category, group) }"
                  @click="setActiveGroup(form_category.id, group)"
                >
                  {{ group }}
                  <span class="badge rounded-pill bg-secondary ms-1">
                    {{ countSubmissionsForGroup(submissionsInCategory(form_category), form_category.params.show_off_grouping, group) }}
                  </span>
                </button>
              </li>
            </ul>
          </div>
        </div>
        
        <div
          v-for="(submissionsGroup, formId) in groupSubmissionsByFormId(
            filterSubmissionsByActiveGroup(submissionsInCategory(form_category), form_category)
          )"
          :key="formId"
          class="mb-1"
        >
          <div class="row g-3">
            <div
              class="col-md-6 col-lg-4 col-xl-3 d-flex align-items-stretch"
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
            class="btn btn-sm btn-outline-primary dropdown-toggle"
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
      class="form-category-section"
    >
      <h5 class="pb-2">{{ category_name }}</h5>
      <div class="row g-3">
        <div
          class="col-md-6 col-lg-4 col-xl-3 d-flex align-items-stretch"
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
import {currentAcademicYearGroup} from "@/utils/academicYear.js";
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
      store: useMainStore(),
      activeGroups: {} // Tracks active group for each category
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
    },
    // Check if a category has show_off_grouping in its params
    hasShowOffGrouping(category) {
      return category.params && 
             category.params.show_off_grouping && 
             Array.isArray(category.params.show_off_grouping) && 
             category.params.show_off_grouping.length > 0;
    },
    // Get unique values for the grouping fields from the submissions
    getGroupingValues(category) {
      if (!this.hasShowOffGrouping(category)) {
        return [];
      }
      
      const submissions = this.submissionsInCategory(category);
      const groupingFields = category.params.show_off_grouping;
      const values = new Set();
      
      // For each submission, get the value of the first grouping field that exists in showoff_attributes
      submissions.forEach(submission => {
        for (const field of groupingFields) {
          if (submission.showoff_attributes && submission.showoff_attributes[field]) {
            values.add(submission.showoff_attributes[field]);
            break;
          }
        }
      });
      
      // If no values found, add a default "All" value
      if (values.size === 0) {
        values.add("Все");
      }
      
      return Array.from(values);
    },
    selectedGroup(category) {
      const groups = this.getGroupingValues(category);
      const manuallySelectedGroup = this.activeGroups[category.id];
      if (groups.includes(manuallySelectedGroup)) {
        return manuallySelectedGroup;
      }
      return currentAcademicYearGroup(groups);
    },
    // Check if a group is active for a category
    isActiveGroup(category, group) {
      return this.selectedGroup(category) === group;
    },
    // Set the active group for a category
    setActiveGroup(categoryId, group) {
      this.activeGroups[categoryId] = group;
    },
    // Filter submissions based on the active group
    filterSubmissionsByActiveGroup(submissions, category) {
      if (!this.hasShowOffGrouping(category)) {
        return submissions;
      }
      
      const groupingFields = category.params.show_off_grouping;
      const activeGroup = this.selectedGroup(category);
      if (!activeGroup) return submissions;
      
      // If active group is "Все" (All), return all submissions
      if (activeGroup === "Все") {
        return submissions;
      }
      
      // Filter submissions by the active group
      return this.filterSubmissionsByGroup(submissions, groupingFields, activeGroup);
    },
    // Helper method to filter submissions by a specific group value
    filterSubmissionsByGroup(submissions, groupingFields, groupValue) {
      return submissions.filter(submission => {
        if (!submission.showoff_attributes) {
          return false;
        }
        
        // Check if any of the grouping fields has the group value
        for (const field of groupingFields) {
          if (submission.showoff_attributes[field] === groupValue) {
            return true;
          }
        }
        
        return false;
      });
    },
    
    // Count submissions for a specific group value
    countSubmissionsForGroup(submissions, groupingFields, groupValue) {
      // If the group value is "Все" (All), return the total count
      if (groupValue === "Все") {
        return submissions.length;
      }
      
      // Otherwise, count submissions that match the group value
      return this.filterSubmissionsByGroup(submissions, groupingFields, groupValue).length;
    }
  }
};
</script>

<style scoped>
.group-tabs {
  max-width: 100%;
  overflow-x: auto;
}

.group-tabs .nav-link {
  white-space: nowrap;
}

.forms-submissions-stack {
  display: grid;
  gap: var(--silaeder-section-gap);
}

.form-category-section:empty {
  display: none;
}

.section-heading h5,
.form-category-section > h5 {
  line-height: 1.35;
}
</style>
