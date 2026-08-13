<template>
  <div class="object-tabs-scroll flex-grow-1">
    <ul class="nav nav-pills object-tabs">
      <li
        v-for="tab in tabs"
        :key="tab.code"
        class="nav-item"
      >
        <button
          ref="tabButtons"
          class="nav-link"
          type="button"
          :data-tab-code="tab.code"
          :class="[
            activeTab === tab.code ? 'active brand-active' : '',
            'position-relative'
          ]"
          @click="onTabSelected(tab.code)"
        >
          {{ tab.name }}
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
  </div>
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
    scrollActiveTabIntoView() {
      this.$nextTick(() => {
        const buttons = Array.isArray(this.$refs.tabButtons)
          ? this.$refs.tabButtons
          : [this.$refs.tabButtons].filter(Boolean);
        const activeButton = buttons.find(button => button?.dataset?.tabCode === this.activeTab);
        activeButton?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
      });
    },
  },
  mounted() {
    this.scrollActiveTabIntoView();
  },
  watch: {
    activeTab() {
      this.scrollActiveTabIntoView();
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

.object-tabs-scroll {
  position: relative;
  min-width: 0;
}

@media (max-width: 767.98px) {
  .object-tabs-scroll {
    margin-inline: -0.25rem;
  }

  .object-tabs-scroll::after {
    position: absolute;
    z-index: 2;
    top: 0;
    right: 0;
    bottom: 0;
    width: 2rem;
    content: "";
    pointer-events: none;
    background: linear-gradient(90deg, rgba(244, 247, 249, 0), var(--silaeder-page-bg));
  }

  .object-tabs {
    flex-wrap: nowrap;
    max-width: 100%;
    padding-inline: 0.25rem 1.5rem;
    overflow-x: auto;
    scroll-padding-inline: 0.25rem 1.5rem;
    scroll-snap-type: x proximity;
    scrollbar-width: none;
  }

  .object-tabs::-webkit-scrollbar {
    display: none;
  }

  .object-tabs .nav-item {
    scroll-snap-align: start;
  }
}
</style>
