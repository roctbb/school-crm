<template>
  <div class="spinner-container" v-if="isVisible">
    <div class="spinner" />
    <p v-if="message">{{ message }}</p>
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
/* Контейнер для спиннера */
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgba(255, 255, 255, 0.8); /* Полупрозрачный фон */
  z-index: 1000;
}

/* Стиль самого спиннера */
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3; /* Светлый бордюр */
  border-top: 5px solid #3498db; /* Синий бордюр (анимация вращения) */
  border-radius: 50%; /* Круглая форма */
  animation: spin 1s linear infinite; /* Анимация вращения */
}

/* Текст под спиннером */
p {
  margin-top: 10px;
  font-size: 16px;
  color: #555;
}

/* Анимация вращения */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>