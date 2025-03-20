<template>
  <div class="d-flex align-items-start mb-3">
    <!-- Фото слева -->
    <div v-if="object.attributes?.photo" class="me-3">
      <img
        :src="object.attributes.photo"
        alt="Object Photo"
        class="rounded-1"
        style="max-width: 150px;"
      />
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
  methods: {
    capitalize,
    canModifyObject,
    canDeleteObject,
    hasTeacherAccess,
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