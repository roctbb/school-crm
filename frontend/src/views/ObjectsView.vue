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

        <!-- Поле поиска и выпадающий список -->
        <div class="d-flex mt-3 align-items-center">
            <input
                type="text"
                class="form-control me-3"
                placeholder="Введите текст для поиска..."
                v-model="searchQuery"
            />
            <select
                class="form-select w-auto"
                v-if="groupingAttributes.length"
                v-model="selectedAttribute"
            >
                <option :value="{}">Не группировать</option>
                <option v-for="attribute in groupingAttributes" :key="attribute.code" :value="attribute">
                    {{ attribute.name }}
                </option>
            </select>
        </div>

        <!-- Контент вкладок -->
        <div class="tab-content mt-3">
            <loading v-if="isLoading"/>
            <div v-else-if="groupedObjects && Object.keys(groupedObjects).length" class="mt-3">
                <!-- Группировка объектов -->
                <div v-for="(objects, group) in groupedObjects" :key="group" class="mb-4">
                    <h5 class="fw-bold">{{ selectedAttribute.name }}: {{ group }}</h5>
                    <div class="row">
                        <div v-for="object in objects" :key="object.id" class="col-md-3 col-lg-3 col-xl-2 mb-4">
                            <ObjectCard :type="store.getObjectTypeByCode(activeTab)" :object="object"/>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else-if="filteredObjects.length" class="row">
                <!-- Отображение без группировки -->
                <div v-for="object in filteredObjects" :key="object.id" class="col-md-3 col-lg-3 col-xl-2 mb-4">
                    <ObjectCard :object="object" :type="store.getObjectTypeByCode(activeTab)"/>
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
import ObjectCard from "@/components/objects/ObjectCard.vue"; // Импортируем ObjectCard

export default {
    components: {Loading, BaseLayout, ObjectCard}, // Регистрируем ObjectCard
    data() {
        return {
            activeTab: "", // Активная вкладка
            searchQuery: "", // Поле для текста поиска
            selectedAttribute: {}, // Выбранный атрибут для группировки
            store: useMainStore(), // Магазин состояния
        };
    },
    computed: {
        objectTypes() {
            return [...this.store.objectTypes].sort((a, b) => a.params.index - b.params.index);
        },
        activeObjects() {
            return this.store.getObjectsByType(this.activeTab);
        },
        filteredObjects() {
            return this.activeObjects.filter((object) =>
                object.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        },
        groupingAttributes() {
            // Получаем атрибуты с `show_off: true` для активного типа объектов
            const activeType = this.store.getObjectTypeByCode(this.activeTab);
            return activeType ? activeType.available_attributes.filter((attr) => attr.show_off) : [];
        },
        groupedObjects() {
            // Группировать объекты по выбранному атрибуту
            if (!this.selectedAttribute.code) return null; // Если фильтр не выбран
            const groups = {};
            this.filteredObjects.forEach((object) => {
                const groupKey = object.attributes[this.selectedAttribute.code] || "Без группы";
                if (!groups[groupKey]) {
                    groups[groupKey] = [];
                }
                groups[groupKey].push(object);
            });
            return groups;
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
        selectedAttribute() {
            // Сброс строки поиска при изменении группировки
            this.searchQuery = "";
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

<style scoped>

</style>