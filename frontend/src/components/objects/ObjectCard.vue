<template>
    <div class="card flex-fill hover-card h-100">
        <!-- Шапка с картинкой (или плейсхолдером) -->
        <div class="card-img-container" v-if="canHavePhoto">
            <template v-if="photoUrl">
                <a :href="photoUrl" target="_blank" rel="noopener noreferrer">
                    <img
                        :src="photoUrl"
                        alt="Фото объекта"
                        class="card-img-top object-card-img"
                    />
                </a>
            </template>
            <template v-else>
                <div class="image-placeholder d-flex flex-column align-items-center justify-content-center">
                    <i class="bi bi-image fs-3 text-secondary"></i>
                    <p class="mb-0 text-secondary">Нет изображения</p>
                </div>
            </template>
        </div>

        <!-- Основное содержимое карточки -->
        <div class="card-body flex-grow-1 pb-2">
            <h5 class="card-title mb-2">
                {{ object.name }}
                <i
                    class="bi bi-person-check text-success"
                    title="Подтверждён владелец"
                    v-if="object.has_registered_owner"
                ></i>
            </h5>

            <!-- Метка «Не подтвержден» -->
            <div
                class="badge bg-warning mt-0"
                v-if="hasTeacherAccess() && object.isNotApproved()"
            >
                Не подтвержден
            </div>

            <!-- Список атрибутов (через AttributePresenter) -->
            <AttributePresenter
                class="mt-2"
                :object="object"
                :type="type"
                :display="false"
                :show_off="true"
            />
        </div>

        <!-- Нижняя часть карточки -->
        <div class="card-footer bg-white border-0">
            <router-link
                :to="`/${type.code}/${object.id}`"
                class="btn btn-sm btn-light"
            >
                Подробнее
            </router-link>

            <button
                v-if="object.invitation && hasAdminAccess()"
                class="btn btn-sm btn-light ms-2"
                @click="copyInviteLink"
            >
                <i class="bi bi-clipboard"></i>
            </button>

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
import {latestFileUrl, resolveFileUrl} from "@/api/files_api.js";

export default {
    name: "ObjectCard",
    components: { AttributePresenter },
    props: {
        object: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            store: useMainStore(),
            showCopied: false,
            photoUrl: null,
        };
    },
    computed: {
        // Проверяем, может ли объект иметь фото
        canHavePhoto() {
            return this.type?.available_attributes?.some(
                (attr) => attr.code === "photo"
            );
        },
        // Тип объекта из store
        type() {
            return this.store.getObjectTypeByCode(this.object.type);
        },
    },
    watch: {
        'object.attributes.photo': {
            immediate: true,
            handler(photo) {
                this.loadPhoto(photo);
            },
        },
    },
    beforeUnmount() {
        this.releasePhotoUrl();
    },
    methods: {
        hasAdminAccess,
        hasTeacherAccess,

        releasePhotoUrl() {
            if (this.photoUrl?.startsWith('blob:')) {
                URL.revokeObjectURL(this.photoUrl);
            }
            this.photoUrl = null;
        },

        async loadPhoto(photo) {
            this.releasePhotoUrl();
            const currentPhoto = latestFileUrl(photo);
            if (!currentPhoto) return;

            try {
                this.photoUrl = await resolveFileUrl(currentPhoto);
            } catch (error) {
                console.error("Не удалось загрузить фото объекта", error);
            }
        },

        copyInviteLink() {
            const invKey = this.object.invitation.key;
            const inviteUrl = `${window.location.origin}/register?invite=${invKey}`;

            navigator.clipboard
                .writeText(inviteUrl)
                .then(() => {
                    this.showCopied = true;
                    setTimeout(() => {
                        this.showCopied = false;
                    }, 1500);
                })
                .catch((err) => {
                    console.error("Ошибка при копировании ссылки:", err);
                });
        },
    },
};
</script>

<style scoped>

.hover-card:hover {
    box-shadow: 0 0 7px rgba(0, 0, 0, 0.08);
    transition: box-shadow 0.03s ease-in-out;
}

.object-card-img {
    border-top-left-radius: 0.25rem;
    border-top-right-radius: 0.25rem;
    object-fit: cover;
    width: 100%;
    height: 180px;
}

/* Плейсхолдер, если нет изображения */
.image-placeholder {
    width: 100%;
    height: 180px;
    background-color: #f8f9fa;
    border-top-left-radius: 0.25rem;
    border-top-right-radius: 0.25rem;
    text-align: center;
}
</style>
