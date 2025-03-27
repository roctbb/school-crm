<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-brand">
        <div class="container">
            <!-- Логотип -->
            <router-link to="/" class="navbar-brand">
                Силаэдр CRM
            </router-link>

            <!-- Кнопка (тогглер) -->
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

            <!-- Навигационные ссылки -->
            <div class="collapse navbar-collapse" id="navbarContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li
                        v-if="hasAdminAccess()"
                        class="nav-item"
                    >
                        <router-link
                            to="/"
                            class="nav-link"
                            active-class="active"
                        >
                            Записи
                        </router-link>
                    </li>
                    <li
                        v-if="hasAdminAccess()"
                        class="nav-item"
                    >
                        <router-link
                            to="/forms"
                            class="nav-link"
                            active-class="active"
                        >
                            Формы
                        </router-link>
                    </li>
                    <li
                        v-if="hasAdminAccess()"
                        class="nav-item"
                    >
                        <router-link
                            to="/import"
                            class="nav-link"
                            active-class="active"
                        >
                            Импорт
                        </router-link>
                    </li>
                    <li
                        v-if="hasAdminAccess()"
                        class="nav-item"
                    >
                        <router-link
                            to="/invitations"
                            class="nav-link"
                            active-class="active"
                        >
                            Инвайты
                        </router-link>
                    </li>
                </ul>

                <!-- Профиль пользователя -->
                <div v-if="profile" class="dropdown">
                    <button
                        class="btn btn-user-menu dropdown-toggle"
                        type="button"
                        id="userMenuButton"
                        data-bs-toggle="dropdown"
                        aria-expanded="false"
                    >
                        <!-- Иконка пользователя (например, из bootstrap-icons) -->
                        <i class="bi bi-person-circle me-1"></i>
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
                                @click="handleLogout"
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
import { mapState, mapActions } from "pinia";
import useMainStore from "@/stores/mainStore.js";
import { hasAdminAccess } from "@/utils/access.js";

export default {
    name: "Navbar",
    computed: {
        ...mapState(useMainStore, ["profile"]),
    },
    methods: {
        hasAdminAccess,
        ...mapActions(useMainStore, ["logout"]),
        handleLogout() {
            this.logout();
            this.$router.push("/login");
        },
    },
};
</script>

<style scoped>
/* Фирменный цвет для Navbar */
.bg-brand {
    background-color: #397698; /* Основной брендовый цвет */
}

/* Темный текст и иконки для кнопки-тогглера */
.navbar-dark .navbar-toggler-icon {
    filter: brightness(0) invert(1);
}

/* Пример плавного перехода для ссылок */
.nav-link {
    transition: background-color 0.3s ease, color 0.3s ease;
}

/* Кнопка с именем пользователя */
.btn-user-menu {
    color: #fff;
    background-color: transparent;
    border: none;
}

/* Плавное раскрытие dropdown (Bootstrap 5 по умолчанию скрывает)
   Для наглядности можно добавить transition, но придётся переопределять сегменты BS.
   Проще оставить «как есть», чтобы не усложнять. */
</style>