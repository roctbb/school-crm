<template>
  <div class="container mt-5">
    <h2>Object Types</h2>
    <ul v-if="objectTypes.length" class="list-group">
      <li v-for="objectType in objectTypes" :key="objectType.id" class="list-group-item">
        {{ objectType.name }}
      </li>
    </ul>
    <p v-else>Loading...</p>
  </div>
</template>

<script>
import { fetchObjectTypes } from '../../api/objects';

export default {
  data() {
    return {
      objectTypes: [],
    };
  },
  async created() {
    try {
      const token = localStorage.getItem('token');
      const result = await fetchObjectTypes(token);
      this.objectTypes = result;
    } catch (error) {
      alert('Failed to fetch object types');
    }
  },
};
</script>