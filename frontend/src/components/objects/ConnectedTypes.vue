<template>
  <div class="connected-types-stack">
    <div v-if="relationError" class="alert alert-danger py-2 small mb-0" role="alert">
      {{ relationError }}
    </div>
    <section v-for="type in connectedTypes" :key="type.code" class="detail-section">
      <div v-if="findRelativesByType(type).length">
        <h5 class="section-heading d-flex justify-content-between align-items-center">
          <span>
            {{ type.name }}
            <span
              class="badge text-bg-light rounded-pill py-1 px-2"
              style="font-size: 0.75rem;"
            >
              {{ findRelativesByType(type).length }}
            </span>
          </span>
          <button
            class="btn btn-outline-secondary btn-sm icon-button ms-2"
            @click="toggleTypeView(type)"
            :aria-label="viewModes[type.code] === 'table' ? 'Показать карточками' : 'Показать таблицей'"
            :title="viewModes[type.code] === 'table' ? 'Карточки' : 'Таблица'"
          >
            <i v-if="viewModes[type.code] === 'table'" class="bi bi-grid"></i>
            <i v-else class="bi bi-list"></i>
          </button>
        </h5>
        <TableView
          v-if="viewModes[type.code] === 'table'"
          :data="findRelativesByType(type)"
          :attributes="type.available_attributes.filter(a => a.show_off)"
          :sortKey.sync="sortKey"
          :sortDirection.sync="sortDirection"
          :canRemoveObject="canRemoveRelation"
          :removingObjectIds="removingRelationIds"
          @remove-object="removeRelation"
        />
        <CardView
          v-else
          :objects="findRelativesByType(type)"
          :objectType="type"
        />
      </div>
    </section>
  </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import TableView from "@/components/objects/TableView.vue";
import CardView from "@/components/objects/CardView.vue";
import {canModifyObject} from "@/utils/access.js";

export default {
  name: "ConnectedTypes",
  components: {
    TableView,
    CardView
  },
  props: {
    object: {
      type: Object,
      required: true
    },
    connectedTypes: {
      type: Array,
      required: true
    },
    viewModes: {
      type: Object,
      required: true
    },
    sortKey: {
      type: String,
      required: true
    },
    sortDirection: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      store: useMainStore(),
      relationError: "",
      removingRelationIds: []
    };
  },
  methods: {
    findRelativesByType(type) {
      const relatives = [
        ...this.object.children.filter(child => child.type === type.code),
        ...this.object.parents.filter(parent => parent.type === type.code)
      ].map(relative => this.store.getObject(relative.type, relative.id));
      return relatives.sort((a, b) => a.name.localeCompare(b.name));
    },
    findRelationship(relative) {
      const childReference = this.object.children.find(child => child.id === relative.id);
      if (childReference) {
        return {parent: this.object, child: relative};
      }

      const parentReference = this.object.parents.find(parent => parent.id === relative.id);
      if (parentReference) {
        return {
          parent: this.store.getObject(parentReference.type, parentReference.id),
          child: this.object
        };
      }

      return null;
    },
    canRemoveRelation(relative) {
      const relationship = this.findRelationship(relative);
      return Boolean(relationship?.parent && canModifyObject(relationship.parent));
    },
    async removeRelation(relative) {
      const relationship = this.findRelationship(relative);
      if (!relationship || !this.canRemoveRelation(relative)) return;

      const confirmed = window.confirm(
        `Удалить связь между «${relationship.parent.name}» и «${relationship.child.name}»? ` +
        "Сами объекты останутся в CRM."
      );
      if (!confirmed) return;

      this.relationError = "";
      this.removingRelationIds.push(relative.id);
      try {
        await relationship.parent.removeChild(relationship.child);
      } catch (error) {
        this.relationError = error.message || "Не удалось удалить связь.";
        console.error("Ошибка при удалении связи:", error);
      } finally {
        this.removingRelationIds = this.removingRelationIds.filter(id => id !== relative.id);
      }
    },
    toggleTypeView(type) {
      this.$emit("toggle-view", type);
    }
  }
};
</script>

<style scoped>
.connected-types-stack {
  display: grid;
  gap: 2rem;
}

.detail-section:empty {
  display: none;
}

.connected-types-stack:empty {
  display: none;
}

.section-heading {
  margin-bottom: 0.875rem;
}
</style>
