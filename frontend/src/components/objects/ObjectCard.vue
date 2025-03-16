<template>
    <div class="card flex-fill">
        <!-- Если у объекта есть фото -->
        <div class="card-img-container" v-if="canHavePhoto">
            <!-- Если есть фото, показывается изображение -->
            <template v-if="photoUrl">
                <a :href="photoUrl" target="_blank" rel="noopener noreferrer">
                    <img :src="photoUrl" alt="Фото объекта" class="card-img">
                </a>
            </template>
            <!-- Если фото нет, показывается плейсхолдер -->
            <template v-else>
                <div class="image-placeholder">
                    <i class="bi bi-image"></i>
                    <p>Нет изображения</p>
                </div>
            </template>
        </div>

        <div class="card-body flex-grow-1 pb-0">
            <h5 class="card-title mb-2">{{ object.name }}</h5>

            <div class="badge bg-warning mt-0" v-if="hasTeacherAccess() && object.isNotApproved()">Не подтвержден</div>

            <AttributePresenter class="mt-2" :object="object" :type="type" :display="false" :show_off="true"/>
        </div>

        <div class="mt-auto py-3 ps-3">
            <router-link
                :to="`/${type.code}/${object.id}`"
                class="btn btn-sm btn-light"
            >
                Подробнее
            </router-link>
        </div>
    </div>
</template>


<script>
import useMainStore from "@/stores/mainStore.js";
import AttributePresenter from "@/components/objects/AttributePresenter.vue";
import {hasTeacherAccess} from "@/utils/access.js"; // Подключаем Pinia store

export default {
    name: "ObjectCard",
    methods: {hasTeacherAccess},
    components: {AttributePresenter},
    props: {
        object: {
            type: Object,
            required: true,
        }
    },
    data() {
        return {
            store: useMainStore(),
        }
    },
    computed: {
        // Получаем URL фото, если есть
        photoUrl() {
            return this.object.attributes.photo || null;
        },
        canHavePhoto() {
            return this.type.available_attributes?.filter(attr => attr.code === 'photo').length > 0;
        },
        type() {
            return this.store.getObjectTypeByCode(this.object.type);
        }
    }
};
</script>

<style scoped>
.card-img-container {
    width: 100%; /* Занимает всю ширину карточки */
    aspect-ratio: 1 / 1; /* Пропорции блока изображения */
    display: flex; /* Flexbox для выравнивания */
    justify-content: center; /* Центрирование по горизонтали */
    align-items: center; /* Центрирование по вертикали */
    background-color: #f7f7f7; /* Фон, если изображения нет */
    border-top-left-radius: calc(0.25rem - 1px); /* Скругленные углы сверху */
    border-top-right-radius: calc(0.25rem - 1px);
    overflow: hidden;
    position: relative; /* Для позиционирования плейсхолдера */
}

.card-img {
    width: 100%; /* Занимает всю ширину */
    height: auto; /* Пропорциональная высота */
    object-fit: cover; /* Заполнение контейнера без искажения */
}

/* Стили плейсхолдера */
.image-placeholder {
    display: flex; /* Flexbox для центрирования */
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-size: 1rem; /* Размер шрифта */
}

.image-placeholder i {
    font-size: 2rem; /* Размер иконки */
    margin-bottom: 5px; /* Отступ между иконкой и текстом */
}

ul {
    list-style-type: none; /* Убирает стандартные маркеры */
    padding: 0 !important; /* Убирает отступы */
    margin: 0; /* Убирает внешние отступы */
}

li {
    margin: 0; /* Убирает внешние отступы у элементов списка */
    padding: 0; /* Убирает внутренние отступы у элементов списка */
}

.created-at-text {
    font-size: 0.75rem; /* Маленький размер текста */
    color: #6c757d; /* Серый цвет */
    margin-top: 5px; /* Отступ сверху от названия */
    display: flex; /* Используем флекс для выравнивания иконки и текста */
    align-items: center; /* Выравнивание по центру */
}

.created-at-text i {
    font-size: 0.875rem; /* Размер иконки чуть больше текста */
    margin-right: 5px; /* Отступ справа от иконки */
}

</style>