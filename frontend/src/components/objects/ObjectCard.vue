<template>
    <div class="card">
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


        <div class="card-body">
            <h5 class="card-title">{{ object.name }}</h5>

            <ul>
                <li
                    v-for="attribute in getShowOffFields(object)"
                    :key="attribute.code">
                    <b>{{ attribute.name }}:</b> {{ object.attributes[attribute.code] }}
                </li>
            </ul>

            <router-link
                :to="`/${type.code}/${object.id}`"
                class="btn btn-sm btn-light mt-2"
            >
                Подробнее
            </router-link>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js"; // Подключаем Pinia store

export default {
    name: "ObjectCard",
    props: {
        object: {
            type: Object,
            required: true,
        },
        type: {
            type: Object,
            required: true,
        },
    },
    computed: {
        // Получаем URL фото, если есть
        photoUrl() {
            return this.object.attributes.photo || null;
        },
        canHavePhoto() {
            return this.type.available_attributes?.filter(attr => attr.code === 'photo').length > 0;
        }
    },
    methods: {
        getShowOffFields(object) {
            return this.type.available_attributes?.filter(
                (attr) => attr.show_off === true && object.attributes[attr.code]
            );
        },
    },
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

</style>