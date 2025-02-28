<template>
  <div class="objects-page">
    <h1 class="text-center mt-5">Objects</h1>

    <!-- Динамические вкладки -->
    <ul class="nav nav-tabs">
      <li class="nav-item" v-for="type in objectTypes" :key="type.code">
        <button
          class="nav-link"
          :class="{ active: activeTab === type.code }"
          @click="selectTab(type.code)"
        >
          {{ type.name }}
        </button>
      </li>
    </ul>

    <!-- Контент вкладок -->
    <div class="tab-content mt-4">
      <div v-if="isLoading" class="text-center">
        <p>Загрузка объектов...</p>
      </div>
      <div v-else-if="activeObjects.length" class="row">
        <div v-for="object in activeObjects" :key="object.id" class="col-md-4 mb-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ object.name }}</h5>
              <router-link
                :to="`/objects/${activeTab}/${object.id}`"
                class="btn btn-primary"
              >
                Подробнее
              </router-link>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p class="text-center">Объекты отсутствуют для данного типа.</p>
      </div>
    </div>

    <!-- Кнопка создания нового объекта -->
    <div class="mt-4 text-center">
      <button
        class="btn btn-success"
        v-if="activeTab"
        @click="createObject(activeTab)"
      >
        Создать новый объект
      </button>
    </div>
  </div>
</template>

<script>
import useMainStore from "@/stores/mainStore";

export default {
  data() {
    return {
      activeTab: "", // Текущий активный тип объекта
    };
  },
  computed: {
    objectTypes() {
      const store = useMainStore();
      return store.objectTypes;
    },
    activeObjects() {
      const store = useMainStore();
      return store.getObjectsByType(this.activeTab);
    },
    isLoading() {
      const store = useMainStore();
      return store.isLoading;
    },
  },
  async created() {
    const store = useMainStore();
    const token = store.token;

    // Загружаем типы объектов
    if (!store.objectTypes.length) {
      await store.fetchObjectTypes();
    }

    // Загружаем объекты для первой вкладки
    if (store.objectTypes.length > 0) {
      this.activeTab = store.objectTypes[0].code;
      await store.fetchObjectsByType(this.activeTab);
    }
  },
  methods: {
    async selectTab(tabCode) {
      const store = useMainStore();
      this.activeTab = tabCode;
      await store.fetchObjectsByType(tabCode);
    },
    createObject(typeCode) {
      this.$router.push(`/objects/${typeCode}/create`);
    },
  },
};
</script>

<style scoped>
.objects-page {
  padding: 20px;
}
</style>