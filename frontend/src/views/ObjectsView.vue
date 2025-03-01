<template>
    <BaseLayout>
        <!-- Динамические вкладки с кнопкой создания объекта -->
        <div class="d-flex align-items-center justify-content-between border-bottom mt-3">
            <ul class="nav nav-tabs flex-grow-1 border-0">
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
            <button
                class="btn btn-success btn-sm ms-1 d-flex align-items-center"
                v-if="activeTab"
                @click="createObject(activeTab)"
            >
                <i class="bi bi-plus me-1"></i> Создать
            </button>
        </div>

        <!-- Поле поиска -->
        <div class="mt-3">
            <input
                type="text"
                class="form-control"
                placeholder="Введите текст для поиска..."
                v-model="searchQuery"
            />
        </div>


        <!-- Контент вкладок -->
        <div class="tab-content mt-3">
            <loading v-if="isLoading"/>
            <div v-else-if="filteredObjects.length" class="row">
                <div v-for="object in filteredObjects" :key="object.id" class="col-md-3 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ object.name }}</h5>
                            <router-link
                                :to="`/${activeTab}/${object.id}`"
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
    </BaseLayout>
</template>

<script>
import useMainStore from "@/stores/mainStore";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";

export default {
    components: {Loading, BaseLayout},
    data() {
        return {
            activeTab: "", // Активная вкладка
            searchQuery: "", // Поле для текста поиска
            store: useMainStore(), // Магазин состояния
        };
    },
    computed: {
        objectTypes() {
            return this.store.objectTypes;
        },
        activeObjects() {
            return this.store.getObjectsByType(this.activeTab);
        },
        filteredObjects() {
            return this.activeObjects.filter((object) =>
                object.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        },
        isLoading() {
            return this.store.isLoading;
        },
    },
    async created() {
        // Загружаем типы объектов (вкладки) и объекты
        if (!this.store.objectTypes.length) {
            await this.store.fetchObjectTypes();
            await this.store.fetchObjects();
        }
        // Устанавливаем активную вкладку из маршрута
        const initialTab = this.$route.path.replace("/", ""); // Получаем текущий маршрут
        this.activeTab = initialTab || (this.objectTypes.length ? this.objectTypes[0].code : "");
        // Если URL пустой, перенаправляем на первую вкладку
        if (!initialTab) {
            this.$router.replace(`/${this.activeTab}`);
        }
        // Инициализация строки поиска
        this.searchQuery = "";
    },
    watch: {
        // Следим за изменением маршрута
        "$route.path"(newPath) {
            this.activeTab = newPath.replace("/", ""); // Синхронизуем активную вкладку с маршрутом
        },
    },
    methods: {
        selectTab(tabCode) {
            // Меняем параметр маршрута (и, следовательно, активную вкладку)
            if (this.activeTab !== tabCode) {
                this.$router.push(`/${tabCode}`);
            }
        },
        createObject(typeCode) {
            this.$router.push(`/${typeCode}/create`);
        },
    },
};
</script>