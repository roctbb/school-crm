<template>
    <BaseLayout>
        <PageHeader
            title="Формы"
            subtitle="Шаблоны форм и ответы, сгруппированные по категориям."
        />

        <div class="page-toolbar">
            <div class="input-group toolbar-search flex-grow-1">
                <span class="input-group-text bg-white text-muted" aria-hidden="true">
                    <i class="bi bi-search"></i>
                </span>
                <input
                    type="search"
                    class="form-control"
                    placeholder="Поиск по названию формы…"
                    aria-label="Поиск по названию формы"
                    v-model="searchQuery"
                />
                <button
                    v-if="searchQuery"
                    class="btn btn-light icon-button"
                    type="button"
                    aria-label="Очистить поиск"
                    title="Очистить поиск"
                    @click="searchQuery = ''"
                >
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
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
                    <div class="category-heading d-flex justify-content-between align-items-center gap-3 pb-2 border-bottom">
                        <h5 class="fw-bold mb-0">{{ category.name }}</h5>
                        <button
                            class="btn btn-sm btn-outline-primary"
                            @click="goToCreateForm(category.id)"
                        >
                            <i class="bi bi-plus-lg me-1"></i>Добавить форму
                        </button>
                    </div>
                    <div class="row g-3 mt-0">
                        <div
                            v-for="form in category.forms"
                            :key="form.id"
                            class="col-sm-6 col-lg-4 col-xl-3 d-flex align-items-stretch"
                        >
                            <FormCard :form="form" :category="category"/>
                        </div>
                        <div v-if="!category.forms.length" class="col-12">
                            <div class="text-muted small py-3">В этой категории пока нет форм.</div>
                        </div>
                    </div>
                </div>
            </div>

            <EmptyState
                v-else
                title="Формы не найдены"
                :description="searchQuery ? 'Попробуйте изменить поисковый запрос.' : 'Категории форм пока не настроены.'"
                icon="bi-ui-checks-grid"
            />

        </div>

    </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import FormCard from "@/components/forms/FormCard.vue";
import useMainStore from "@/stores/mainStore.js";
import EmptyState from "@/components/common/EmptyState.vue";
import PageHeader from "@/components/common/PageHeader.vue";

export default {
    components: {BaseLayout, EmptyState, Loading, FormCard, PageHeader},

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
    margin-bottom: 2rem;
}

@media (max-width: 575.98px) {
    .category-heading {
        align-items: stretch !important;
        flex-direction: column;
    }

    .category-heading .btn {
        width: 100%;
    }
}
</style>
