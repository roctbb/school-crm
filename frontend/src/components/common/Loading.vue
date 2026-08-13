<template>
  <div
    v-if="isVisible"
    class="loading-state"
    :class="{ 'loading-state--compact': compact }"
    role="status"
    aria-live="polite"
  >
    <div class="spinner-border text-primary" :class="{ 'spinner-border-sm': compact }" aria-hidden="true"></div>
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
    compact: {
      type: Boolean,
      default: false,
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
  min-height: 6rem;
  gap: 0.8rem;
  padding: 1.5rem;
  border-radius: 0.75rem;
  background: transparent;
}

.loading-state--compact {
  min-height: 0;
  flex-direction: row;
  justify-content: flex-start;
  gap: 0.5rem;
  padding: 0.4rem 0;
  font-size: 0.875rem;
}
</style>
