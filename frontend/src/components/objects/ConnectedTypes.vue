<template>
  <div>
    <div v-for="type in connectedTypes" :key="type.code" class="mb-4">
      <div v-if="findRelativesByType(type).length">
        <h5 class="pb-2 d-flex justify-content-between align-items-center">
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
            class="btn btn-outline-secondary btn-sm ms-2"
            @click="toggleTypeView(type)"
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
        />
        <CardView
          v-else
          :objects="findRelativesByType(type)"
          :objectType="type"
        />
      </div>
    </div>
  </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import TableView from "@/components/objects/TableView.vue";
import CardView from "@/components/objects/CardView.vue";

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
      store: useMainStore()
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
    toggleTypeView(type) {
      this.$emit("toggle-view", type);
    }
  }
};
</script>