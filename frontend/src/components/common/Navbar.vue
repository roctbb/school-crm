<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <!-- Логотип -->
            <a class="navbar-brand" href="/">Силаэдр CRM</a>

            <!-- Навигационная ссылка -->
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <router-link
                        to="/"
                        class="nav-link"
                        active-class="active"
                    >
                        Записи
                    </router-link>
                </li>
                <li class="nav-item">
                    <router-link
                        to="/forms"
                        class="nav-link"
                        active-class="active"
                    >
                        Формы
                    </router-link>
                </li>
            </ul>

            <!-- Профиль пользователя в правой части -->
            <div class="ml-auto dropdown" v-if="profile">
                <button
                    class="btn btn-light dropdown-toggle"
                    type="button"
                    id="userMenuButton"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                >
                    {{ profile.name }}
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userMenuButton">
                    <li>
                        <button class="dropdown-item" type="button" @click="logout">
                            Выйти
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script>
import { mapState, mapActions } from 'pinia'; // Убедимся, что используется Vue 3 версия Pinia
import useMainStore from "@/stores/mainStore.js";

export default {
    name: "Navbar",
    computed: {
        // Подключаем состояние пользователя из Pinia Store
        ...mapState(useMainStore, ["profile"]),
    },
    methods: {
        // Логика выхода
        ...mapActions(useMainStore, ["logout"]),
        handleLogout() {
            this.logout(); // Вызов экшена из Pinia
            this.$router.push("/login"); // Переход на страницу логина
        },
    },
};
</script>

<style scoped>
.navbar {
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.dropdown-menu-end {
    right: 0;
    left: auto;
}


</style>