<template>
    <BaseLayout>
        <!-- Заголовок -->
        <div class="d-flex align-items-center justify-content-between mt-3">
            <h4 class="mb-0">Формы</h4>
        </div>

        <!-- Поле поиска -->
        <div class="d-flex mt-3 align-items-center">
            <input
                type="text"
                class="form-control me-3"
                placeholder="Введите название формы для поиска..."
                v-model="searchQuery"
            />
        </div>

        <div class="tab-content mt-3">
            <loading v-if="isLoading"/>
            <div v-else-if="filteredCategories.length">
                <div
                    v-for="category in filteredCategories"
                    :key="category.id"
                    class="category-block"
                >
                    <!-- Заголовок категории + кнопка Добавить -->
                    <div class="d-flex justify-content-between align-items-center pb-2">
                        <h5 class="fw-bold mb-0">{{ category.name }}</h5>
                        <button
                            class="btn btn-sm btn-light"
                            @click="goToCreateForm(category.id)"
                        >
                            Добавить
                        </button>
                    </div>
                    <div class="row mt-2">
                        <div
                            v-for="form in category.forms"
                            :key="form.id"
                            class="col-md-3 col-lg-3 col-xl-2 mb-0 d-flex align-items-stretch"
                        >
                            <FormCard :form="form" :category="category"/>
                        </div>
                        <div v-if="!category.forms.length" class="col-12">
                            <p>Формы отсутствуют.</p>
                        </div>
                    </div>
                </div>
            </div>

        </div>

    </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import FormCard from "@/components/forms/FormCard.vue";
import useMainStore from "@/stores/mainStore.js";

export default {
    components: {BaseLayout, Loading, FormCard},

    data() {
        return {
            searchQuery: "", // Поле для фильтрации форм
            isLoading: true, // Состояние загрузки
            store: useMainStore(), // Подключение MainStore
        };
    },

    computed: {
        // Фильтр категорий по поисковому запросу
        filteredCategories() {
            if (!this.searchQuery.trim()) {
                return this.store.formCategories; // Без поиска возвращаем все категории
            }
            // Фильтрация категорий по названию форм
            return this.store.formCategories
                .map(category => ({
                    ...category,
                    forms: category.forms.filter(form =>
                        form.name.toLowerCase().includes(this.searchQuery.toLowerCase())
                    ),
                }))
                .filter(category => category.forms.length > 0); // Только категории, где есть формы
        }

    },

    methods: {
        // Загрузка категорий форм
        async loadCategories() {
            if (!this.store.formCategories.length) {
                await this.store.fetchFormCategories(); // Вызов метода загрузки категорий
            }
            this.isLoading = false; // Отключаем индикатор загрузки
        },
        goToCreateForm(categoryId) {
            this.$router.push({
                name: 'CreateForm',
                params: {categoryId: categoryId},
            });
        },
    },

    mounted() {
        this.loadCategories(); // Загрузка данных при монтировании компонента
    },
};
</script>

<style scoped>
.category-block {
    margin-bottom: 30px;
}
</style>