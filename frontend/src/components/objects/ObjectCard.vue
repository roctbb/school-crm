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
            <h5 class="card-title mb-2">
                {{ object.name }}
                <i class="bi bi-person-check" v-if="object.has_registered_owner"></i>
            </h5>

            <div
                class="badge bg-warning mt-0"
                v-if="hasTeacherAccess() && object.isNotApproved()"
            >
                Не подтвержден
            </div>

            <AttributePresenter
                class="mt-2"
                :object="object"
                :type="type"
                :display="false"
                :show_off="true"
            />
        </div>

        <div class="mt-auto py-3 ps-3">
            <!-- Кнопка "Подробнее" -->
            <router-link
                :to="`/${type.code}/${object.id}`"
                class="btn btn-sm btn-light"
            >
                Подробнее
            </router-link>

            <!-- Кнопка копирования ссылки -->
            <button
                v-if="object.invitation && hasAdminAccess()"
                class="btn btn-sm btn-light ms-2"
                @click="copyInviteLink"
            ><i class="bi bi-clipboard"></i>
            </button>

            <!-- Индикация копирования -->
            <small
                v-if="showCopied"
                class="text-success ms-2"
                style="vertical-align: middle;"
            >
                Скопировано!
            </small>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import AttributePresenter from "@/components/objects/AttributePresenter.vue";
import { hasAdminAccess, hasTeacherAccess } from "@/utils/access.js";

export default {
    name: "ObjectCard",
    components: { AttributePresenter },
    props: {
        object: {
            type: Object,
            required: true,
        }
    },
    data() {
        return {
            store: useMainStore(),
            showCopied: false
        };
    },
    computed: {
        // Получаем URL фото, если есть
        photoUrl() {
            return this.object.attributes.photo || null;
        },
        // Проверка, может ли объект иметь фото
        canHavePhoto() {
            return this.type.available_attributes?.some(attr => attr.code === 'photo');
        },
        // Определение типа объекта из store
        type() {
            return this.store.getObjectTypeByCode(this.object.type);
        }
    },
    methods: {
        hasAdminAccess,
        hasTeacherAccess,
        copyInviteLink() {
            const invKey = this.object.invitation.key;
            const inviteUrl = `${window.location.origin}/register?invite=${invKey}`;

            navigator.clipboard
                .writeText(inviteUrl)
                .then(() => {
                    this.showCopied = true;
                    // Прячем уведомление через полторы секунды
                    setTimeout(() => {
                        this.showCopied = false;
                    }, 1500);
                })
                .catch(err => {
                    console.error("Ошибка при копировании ссылки:", err);
                });
        }
    }
};
</script>

<style scoped>
.card-img-container {
    width: 100%;
    aspect-ratio: 1 / 1;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f7f7f7;
    border-top-left-radius: calc(0.25rem - 1px);
    border-top-right-radius: calc(0.25rem - 1px);
    overflow: hidden;
    position: relative;
}

.card-img {
    width: 100%;
    height: auto;
    object-fit: cover;
}

/* Стили плейсхолдера */
.image-placeholder {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-size: 1rem;
}

.image-placeholder i {
    font-size: 2rem;
    margin-bottom: 5px;
}

ul {
    list-style-type: none;
    padding: 0 !important;
    margin: 0;
}

li {
    margin: 0;
    padding: 0;
}

.created-at-text {
    font-size: 0.75rem;
    color: #6c757d;
    margin-top: 5px;
    display: flex;
    align-items: center;
}

.created-at-text i {
    font-size: 0.875rem;
    margin-right: 5px;
}
</style>