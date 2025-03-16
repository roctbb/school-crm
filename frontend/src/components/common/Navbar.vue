<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <!-- Логотип -->
            <a class="navbar-brand" href="/">Силаэдр CRM</a>

            <!-- Кнопка (тогглер), показывающая и скрывающая меню на маленьких экранах -->
            <button
                class="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarContent"
                aria-controls="navbarContent"
                aria-expanded="false"
                aria-label="Toggle navigation"
            >
                <span class="navbar-toggler-icon"></span>
            </button>

            <!-- Контейнер с навигационными ссылками, который будет сворачиваться -->
            <div class="collapse navbar-collapse" id="navbarContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0" v-if="hasAdminAccess()">
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
                    <li class="nav-item">
                        <router-link
                            to="/import"
                            class="nav-link"
                            active-class="active"
                        >
                            Импорт
                        </router-link>
                    </li>
                </ul>

                <!-- Профиль пользователя в правой части -->
                <div class="dropdown" v-if="profile">
                    <button
                        class="btn btn-light dropdown-toggle"
                        type="button"
                        id="userMenuButton"
                        data-bs-toggle="dropdown"
                        aria-expanded="false"
                    >
                        {{ profile.name }}
                    </button>
                    <ul
                        class="dropdown-menu dropdown-menu-end"
                        aria-labelledby="userMenuButton"
                    >
                        <li>
                            <button
                                class="dropdown-item"
                                type="button"
                                @click="logout"
                            >
                                Выйти
                            </button>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>
</template>

<script>
import { mapState, mapActions } from 'pinia'
import useMainStore from "@/stores/mainStore.js"
import {hasAdminAccess} from "@/utils/helpers.js";

export default {
    name: "Navbar",
    computed: {
        ...mapState(useMainStore, ["profile"]),
    },
    methods: {
        hasAdminAccess,
        ...mapActions(useMainStore, ["logout"]),
        handleLogout() {
            this.logout()
            this.$router.push("/login");
        },
    },
}
</script>

<style scoped>
.navbar {
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
</style>