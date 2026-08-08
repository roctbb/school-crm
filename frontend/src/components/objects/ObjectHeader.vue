<template>
  <div class="d-flex align-items-start mb-3">
    <!-- Фото слева -->
    <div v-if="photoUrl" class="me-3 participant-photo-block">
      <img
        :src="photoUrl"
        alt="Object Photo"
        class="rounded-1"
        style="max-width: 150px;"
      />
      <button
        v-if="previousPhotos.length"
        class="btn btn-link btn-sm d-block px-0"
        type="button"
        @click="showPhotoHistory = !showPhotoHistory"
      >
        Предыдущие фото ({{ previousPhotos.length }})
      </button>
      <div v-if="showPhotoHistory" class="photo-history mt-2">
        <a
          v-for="(photo, index) in previousPhotos"
          :key="photo.original"
          :href="photo.resolved"
          target="_blank"
          rel="noopener noreferrer"
          :title="`Предыдущее фото ${index + 1}`"
        >
          <img :src="photo.resolved" alt="Предыдущее фото" class="photo-history-item rounded-1" />
        </a>
      </div>
    </div>
    <!-- Заголовок -->
    <div class="flex-grow-1">
      <h2 class="me-2">
        <small class="text-muted">{{ capitalize(object_type.name) }}:</small>
        {{ object.name }}
        <i class="bi bi-person-check" v-if="object.has_registered_owner"></i>
      </h2>
      <div>
        <div
          class="badge bg-warning mb-2"
          v-if="!object.is_approved"
          @click="hasTeacherAccess() && handleApprove()"
        >
          Не подтвержден
        </div>
        <AttributePresenter :object="object" :type="object_type" />
      </div>
    </div>
    <!-- Выпадающий список -->
    <div v-if="canModifyObject(object)">
      <div class="dropdown">
        <button
          class="btn btn-light dropdown-toggle"
          type="button"
          id="actionsMenu"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          Действия
        </button>
        <ul class="dropdown-menu" aria-labelledby="actionsMenu">
          <li>
            <router-link
              :to="`/${object_type.code}/${object.id}/edit`"
              class="dropdown-item"
            >
              <i class="bi bi-pencil me-1"></i> Редактировать
            </router-link>
          </li>
          <li v-if="!object.is_approved && hasTeacherAccess()">
            <button class="dropdown-item" @click="handleApprove()">
              <i class="bi bi-check-circle text-success me-1"></i> Утвердить
            </button>
          </li>
          <li v-if="!object.is_approved && hasTeacherAccess()">
            <button class="dropdown-item" @click="handleRestore()">
              <i class="bi bi-stop-circle me-1"></i> Отменить изменения
            </button>
          </li>
          <li v-if="canDeleteObject(object)">
            <button class="dropdown-item text-danger" @click="handleDelete()">
              <i class="bi bi-trash me-1"></i> Удалить
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import AttributePresenter from "@/components/objects/AttributePresenter.vue";
import { capitalize } from "@/utils/helpers.js";
import {
  canModifyObject,
  canDeleteObject,
  hasTeacherAccess
} from "@/utils/access.js";
import {normalizeFileUrls, resolveFileUrl} from "@/api/files_api.js";

export default {
  name: "ObjectHeader",
  components: {
    AttributePresenter
  },
  props: {
    object: {
      type: Object,
      required: true
    },
    object_type: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      photoUrl: null,
      previousPhotos: [],
      showPhotoHistory: false,
      photoLoadId: 0
    };
  },
  watch: {
    'object.attributes.photo': {
      immediate: true,
      handler(photo) {
        this.loadPhoto(photo);
      }
    }
  },
  beforeUnmount() {
    this.photoLoadId += 1;
    this.releasePhotoUrls();
  },
  methods: {
    capitalize,
    canModifyObject,
    canDeleteObject,
    hasTeacherAccess,
    releasePhotoUrls() {
      [this.photoUrl, ...this.previousPhotos.map(photo => photo.resolved)].forEach(url => {
        if (url?.startsWith('blob:')) URL.revokeObjectURL(url);
      });
      this.photoUrl = null;
      this.previousPhotos = [];
    },
    async loadPhoto(photo) {
      const loadId = ++this.photoLoadId;
      this.releasePhotoUrls();
      const photos = normalizeFileUrls(photo);
      if (!photos.length) return;

      const results = await Promise.allSettled(photos.map(async original => ({
          original,
          resolved: await resolveFileUrl(original)
      })));
      const resolved = results
        .filter(result => result.status === 'fulfilled')
        .map(result => result.value);

      if (loadId !== this.photoLoadId) {
        resolved.forEach(photoItem => {
          if (photoItem.resolved?.startsWith('blob:')) URL.revokeObjectURL(photoItem.resolved);
        });
        return;
      }

      if (!resolved.length) return;
      this.photoUrl = resolved[resolved.length - 1].resolved;
      this.previousPhotos = resolved.slice(0, -1).reverse();
    },
    handleDelete() {
      this.$emit("delete");
    },
    handleApprove() {
      this.$emit("approve");
    },
    handleRestore() {
      this.$emit("restore");
    }
  }
};
</script>

<style scoped>
.participant-photo-block {
  max-width: 190px;
}

.photo-history {
  display: grid;
  grid-template-columns: repeat(3, 52px);
  gap: 0.35rem;
}

.photo-history-item {
  width: 52px;
  height: 52px;
  object-fit: cover;
}
</style>
