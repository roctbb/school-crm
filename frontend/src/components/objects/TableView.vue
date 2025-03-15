<template>
  <div>
    <div v-if="groupedData && Object.keys(groupedData).length">
      <div
        v-for="(objects, group) in groupedData"
        :key="group"
        class="mb-4"
      >
        <h5 class="fw-bold pb-2">
          {{ groupingAttribute?.name }}: {{ group }}
        </h5>
        <table class="table table-sm table-bordered table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th @click="onSort('name')">
                Имя
                <span v-if="sortKey === 'name'">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th
                v-for="attr in attributes"
                :key="attr.code"
                @click="onSort(attr.code)"
              >
                {{ attr.name }}
                <span v-if="sortKey === attr.code">
                  {{ sortDirection === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="object in sortData(objects)"
              :key="object.id"
            >
              <td>{{ object.name }}</td>
              <td
                v-for="attr in attributes"
                :key="attr.code"
              >
                {{ object.attributes[attr.code] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else-if="data.length" class="table-responsive">
      <table class="table table-sm table-bordered table-hover align-middle">
        <thead class="table-light">
          <tr>
            <th @click="onSort('name')">
              Имя
              <span v-if="sortKey === 'name'">
                {{ sortDirection === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
            <th
              v-for="attr in attributes"
              :key="attr.code"
              @click="onSort(attr.code)"
            >
              {{ attr.name }}
              <span v-if="sortKey === attr.code">
                {{ sortDirection === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="object in sortData(data)"
            :key="object.id"
          >
            <td>{{ object.name }}</td>
            <td
              v-for="attr in attributes"
              :key="attr.code"
            >
              {{ object.attributes[attr.code] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p class="text-center">Объекты отсутствуют для данного типа.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "TableView",
  props: {
    data: { type: Array, required: true },
    groupedData: { type: Object, default: null },
    attributes: { type: Array, required: true },
    groupingAttribute: { type: Object, default: null },
    sortKey: { type: String, required: true },
    sortDirection: { type: String, required: true }
  },
  emits: ["update:sortKey", "update:sortDirection"],
  methods: {
    onSort(key) {
      if (this.sortKey === key) {
        this.$emit("update:sortDirection", this.sortDirection === "asc" ? "desc" : "asc");
      } else {
        this.$emit("update:sortKey", key);
        this.$emit("update:sortDirection", "asc");
      }
    },
    sortData(objects) {
      const sorted = [...objects];
      sorted.sort((a, b) => {
        let aVal = this.sortKey === "name" ? a.name : a.attributes[this.sortKey];
        let bVal = this.sortKey === "name" ? b.name : b.attributes[this.sortKey];

        if (typeof aVal === "number" && typeof bVal === "number") {
          return this.sortDirection === "asc" ? aVal - bVal : bVal - aVal;
        }

        const aStr = String(aVal ?? "");
        const bStr = String(bVal ?? "");
        return this.sortDirection === "asc" ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
      });
      return sorted;
    }
  }
};
</script>