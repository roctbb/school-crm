<template>
  <ul class="nav nav-pills flex-grow-1 object-tabs">
    <li
      v-for="tab in tabs"
      :key="tab.code"
      class="nav-item"
    >
      <button
        class="nav-link"
        type="button"
        :class="[
          activeTab === tab.code ? 'active brand-active' : '',
          'position-relative'
        ]"
        @click="onTabSelected(tab.code)"
      >
        {{ tab.name }}
        <!-- Пример отображения счётчика -->
        <span
          v-if="objectCounts[tab.code] > 0"
          :class="[
            'badge',
            hasTeacherAccess && hasUnconfirmed(tab.code)
              ? 'bg-warning text-dark'
              : 'bg-secondary',
            'rounded-5',
            'ms-1'
          ]"
        >
          {{ objectCounts[tab.code] }}
        </span>
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  name: "TabNavigation",
  props: {
    tabs: {
      type: Array,
      default: () => [],
    },
    activeTab: {
      type: String,
      default: "",
    },
    objectCounts: {
      type: Object,
      default: () => ({}),
    },
    // Дополнительные функции доступа
    hasTeacherAccess: {
      type: Boolean,
      default: false,
    },
    hasUnconfirmed: {
      type: Function,
      default: () => false,
    },
  },
  methods: {
    onTabSelected(code) {
      this.$emit("tab-selected", code);
    },
  },
};
</script>

<style scoped>
.nav-link {
  color: #475962;
  font-weight: 500;
  white-space: nowrap;
}

.nav-link:hover {
  color: var(--silaeder-primary-dark);
  background: var(--silaeder-primary-soft);
}

.nav-link.active {
  color: var(--silaeder-primary-dark);
  font-weight: 600;
  background: var(--silaeder-primary-soft);
}

.object-tabs {
  min-width: 0;
  gap: 0.25rem;
}

@media (max-width: 767.98px) {
  .object-tabs {
    flex-wrap: nowrap;
    max-width: 100%;
    overflow-x: auto;
    scrollbar-width: thin;
  }
}
</style>
