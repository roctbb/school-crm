<template>
  <div class="forms-submissions-stack">
    <template
      v-for="form_category in object_type.form_categories"
      :key="form_category.id"
    >
      <section
        v-if="
          submissionsInCategory(form_category).length ||
          (canFillInCategory(form_category) && canModifyObject(object))
        "
        class="form-category-section"
      >
        <header class="category-header">
          <div class="category-title-line">
            <h5 class="category-title">{{ form_category.name }}</h5>
            <span
              class="category-visibility"
              v-if="form_category.params.is_private"
            >
              <i class="bi bi-eye-slash" aria-hidden="true"></i> Приватный
            </span>
            <span
              class="category-visibility"
              v-if="form_category.params.is_hidden"
            >
              <i class="bi bi-eye-slash" aria-hidden="true"></i> Скрытый
            </span>
          </div>

          <div
            class="btn-group category-create-action"
            v-if="canFillInCategory(form_category) && canModifyObject(object)"
          >
            <button
              class="btn btn-sm btn-outline-primary dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-plus-lg me-1"></i>Добавить
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li
                v-for="form in store.getFormCategory(form_category.id).forms"
                :key="form.id"
              >
                <button
                  class="dropdown-item"
                  type="button"
                  @click="goToCreateSubmission(form.id)"
                >
                  {{ form.name }}
                </button>
              </li>
            </ul>
          </div>
        </header>

        <div v-if="hasShowOffGrouping(form_category)" class="group-tabs">
          <div class="category-group-nav" role="tablist" :aria-label="`Период: ${form_category.name}`">
            <button
              v-for="(group, index) in getGroupingValues(form_category)"
              :key="index"
              class="category-group-pill"
              :class="{ active: isActiveGroup(form_category, group) }"
              type="button"
              role="tab"
              :aria-selected="isActiveGroup(form_category, group)"
              @click="setActiveGroup(form_category.id, group)"
            >
              <span>{{ group }}</span>
              <span class="category-group-count">
                · {{ countSubmissionsForGroup(submissionsInCategory(form_category), form_category.params.show_off_grouping, group) }}
              </span>
            </button>
          </div>
        </div>
        
        <div
          v-for="(submissionsGroup, formId) in groupSubmissionsByFormId(
            filterSubmissionsByActiveGroup(submissionsInCategory(form_category), form_category)
          )"
          :key="formId"
          class="submission-group"
        >
          <div class="submission-card-grid">
            <div
              class="submission-card-cell"
              v-for="submission in submissionsGroup"
              :key="submission.id"
            >
              <SubmissionCard
                :submission="submission"
                :object="object"
                :hidden-attributes="hiddenGroupingAttributes(form_category)"
              />
            </div>
          </div>
        </div>
      </section>
    </template>
    <!-- Внешние категории -->
    <div
      v-for="(category_name, i) in externalCategories"
      :key="i"
      class="form-category-section"
    >
      <h5 class="mb-4">{{ category_name }}</h5>
      <div class="submission-card-grid">
        <div
          class="submission-card-cell"
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
import {currentAcademicYearGroup, sortAcademicYearGroups} from "@/utils/academicYear.js";
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
      
      return sortAcademicYearGroups(Array.from(values));
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
    },
    hiddenGroupingAttributes(category) {
      if (!this.hasShowOffGrouping(category) || this.selectedGroup(category) === "Все") {
        return [];
      }
      return category.params.show_off_grouping;
    }
  }
};
</script>

<style scoped>
.group-tabs {
  max-width: 100%;
  overflow-x: auto;
  margin-bottom: 1.25rem;
  scrollbar-width: thin;
}

.category-group-nav {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: max-content;
  min-width: 100%;
}

.category-group-pill {
  display: inline-flex;
  align-items: baseline;
  gap: 0.15rem;
  min-height: 2.25rem;
  padding: 0.4rem 0.75rem;
  color: var(--silaeder-muted);
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  border: 1px solid transparent;
  border-radius: 0.6rem;
  background: transparent;
  transition: color 140ms ease, background-color 140ms ease, border-color 140ms ease;
}

.category-group-pill:hover {
  color: var(--silaeder-primary-dark);
  background: var(--silaeder-primary-soft);
}

.category-group-pill.active {
  color: var(--silaeder-primary-dark);
  border-color: #bfd2dc;
  background: var(--silaeder-primary-soft);
  font-weight: 600;
}

.category-group-pill:focus-visible {
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgb(57 118 152 / 18%);
}

.category-group-count {
  color: var(--silaeder-muted);
  font-variant-numeric: tabular-nums;
}

.forms-submissions-stack {
  display: grid;
  gap: 2.5rem;
}

.submission-group + .submission-group {
  margin-top: 1.5rem;
}

.category-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}

.category-title-line {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.4rem 0.75rem;
  min-width: 0;
}

.category-title,
.form-category-section > h5 {
  margin: 0;
  line-height: 1.35;
}

.category-visibility {
  color: var(--silaeder-muted);
  font-size: 0.8rem;
  font-weight: 500;
}

.submission-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
  align-items: start;
  justify-content: start;
  gap: 1rem;
}

.submission-card-cell {
  min-width: 0;
}

@media (max-width: 575.98px) {
  .category-header {
    grid-template-columns: minmax(0, 1fr);
    align-items: stretch;
  }

  .category-create-action,
  .category-create-action > button {
    width: 100%;
  }

  .group-tabs {
    width: 100%;
  }

  .submission-card-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
