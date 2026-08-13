<template>
    <div class="card flex-fill hover-card h-100">
        <!-- Шапка с картинкой (или плейсхолдером) -->
        <div class="card-img-container" v-if="canHavePhoto">
            <template v-if="photoUrl && !photoFailed">
                <router-link :to="`/${type.code}/${object.id}`" :aria-label="`Открыть ${object.name}`">
                    <img
                        :src="photoUrl"
                        alt="Фото объекта"
                        class="card-img-top object-card-img"
                        loading="lazy"
                        decoding="async"
                        @error="photoFailed = true"
                    />
                </router-link>
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
                <router-link :to="`/${type.code}/${object.id}`" class="card-title-link stretched-link">
                    {{ object.name }}
                </router-link>
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
        <div v-if="hasFooterActions" class="card-footer bg-white border-0">
            <a
                v-if="photoUrl && !photoFailed"
                :href="photoUrl"
                class="btn btn-sm btn-light icon-button"
                target="_blank"
                rel="noopener noreferrer"
                :aria-label="`Открыть фото ${object.name}`"
                title="Открыть фото"
            >
                <i class="bi bi-image"></i>
            </a>

            <button
                v-if="object.invitation && hasAdminAccess()"
                class="btn btn-sm btn-light icon-button"
                :class="{ 'ms-2': photoUrl && !photoFailed }"
                aria-label="Скопировать ссылку-приглашение"
                title="Скопировать приглашение"
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
            <small v-if="copyError" class="text-danger ms-2">{{ copyError }}</small>
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
            copyError: "",
            photoUrl: null,
            photoFailed: false,
            photoLoadId: 0,
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
        hasFooterActions() {
            return Boolean(
                (this.photoUrl && !this.photoFailed) ||
                (this.object.invitation && hasAdminAccess()) ||
                this.showCopied ||
                this.copyError
            );
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
        this.photoLoadId += 1;
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
            this.photoFailed = false;
        },

        async loadPhoto(photo) {
            const loadId = ++this.photoLoadId;
            this.releasePhotoUrl();
            const currentPhoto = latestFileUrl(photo);
            if (!currentPhoto) return;

            try {
                const resolvedUrl = await resolveFileUrl(currentPhoto);
                if (loadId !== this.photoLoadId) {
                    if (resolvedUrl?.startsWith('blob:')) URL.revokeObjectURL(resolvedUrl);
                    return;
                }
                this.photoUrl = resolvedUrl;
                this.photoFailed = false;
            } catch (error) {
                console.error("Не удалось загрузить фото объекта", error);
            }
        },

        copyInviteLink() {
            this.copyError = "";
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
                    this.copyError = "Не удалось скопировать";
                    console.error("Ошибка при копировании ссылки:", err);
                });
        },
    },
};
</script>

<style scoped>

.hover-card:hover {
    border-color: #bfd2dc;
    box-shadow: var(--silaeder-shadow);
    transform: translateY(-2px);
}

.hover-card {
    overflow: hidden;
    cursor: pointer;
    transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}

.hover-card:focus-within {
    border-color: var(--silaeder-primary);
    box-shadow: 0 0 0 0.2rem rgb(57 118 152 / 18%);
}

.card-title-link {
    color: var(--silaeder-text);
    text-decoration: none;
}

.card-title-link:hover {
    color: var(--silaeder-primary-dark);
}

.object-card-img {
    border-top-left-radius: 0.25rem;
    border-top-right-radius: 0.25rem;
    object-fit: cover;
    width: 100%;
    height: 180px;
}

.card-body {
    min-width: 0;
}

.card-title {
    overflow-wrap: anywhere;
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

.card-footer {
    position: relative;
    z-index: 2;
}
</style>
