<template>
  <Transition name="global-loading-fade">
    <div
      v-if="visible"
      class="global-loading-overlay"
      role="status"
      aria-live="polite"
      aria-label="Загрузка страницы"
    >
      <div class="global-loading-card">
        <div class="spinner-border text-primary" aria-hidden="true"></div>
        <div>
          <div class="fw-semibold">Загружаем…</div>
          <div class="small text-muted">Это может занять несколько секунд</div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script>
export default {
  name: 'GlobalLoadingOverlay',
  props: {
    visible: {
      type: Boolean,
      required: true,
    },
  },
};
</script>

<style scoped>
.global-loading-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgb(241 245 248 / 82%);
  backdrop-filter: blur(2px);
}

.global-loading-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: min(22rem, 100%);
  padding: 1.25rem 1.5rem;
  color: var(--bs-body-color);
  background: var(--bs-body-bg);
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: var(--bs-border-radius-lg);
  box-shadow: var(--silaeder-shadow-md);
}

.global-loading-fade-enter-active,
.global-loading-fade-leave-active {
  transition: opacity 150ms ease;
}

.global-loading-fade-enter-from,
.global-loading-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .global-loading-fade-enter-active,
  .global-loading-fade-leave-active {
    transition: none;
  }
}
</style>
