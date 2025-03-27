<template>
  <!-- Можно добавить общий <transition-group>, если мы хотим анимировать сами вкладки -->
  <transition-group name="tabs" tag="ul" class="nav nav-tabs flex-grow-1 border-0">
    <li
      v-for="tab in tabs"
      :key="tab.code"
      class="nav-item"
    >
      <button
        class="nav-link"
        :class="[
          activeTab === tab.code ? 'active brand-active' : '',
          'position-relative'
        ]"
        @click="onTabSelected(tab.code)"
      >
        {{ tab.name }}
        <!-- Пример отображения счётчика -->
        <transition name="fade">
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
        </transition>
      </button>
    </li>
  </transition-group>
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
  color: #343a40;
  font-weight: 500;
  transition: background-color 0.2s ease;
}


/* Анимация для перехода между вкладками */
.tabs-enter-active,
.tabs-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.tabs-enter,
.tabs-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

/* Вспомогательная анимация для fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s linear;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>