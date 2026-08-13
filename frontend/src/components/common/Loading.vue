<template>
  <div
    v-if="isVisible"
    class="loading-state"
    role="status"
    aria-live="polite"
  >
    <div class="spinner-border text-primary" aria-hidden="true"></div>
    <p class="mb-0 text-muted">{{ message || 'Загрузка…' }}</p>
  </div>
</template>

<script>
export default {
  name: "Loading",
  props: {
    isVisible: {
      type: Boolean,
      default: true, // Это обязательный пропс для управления видимостью
    },
    message: {
      type: String,
      default: "", // Сообщение, показываемое под спиннером (например: "Загрузка")
    },
  },
};
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 10rem;
  gap: 0.8rem;
  padding: 2rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.55);
}
</style>
