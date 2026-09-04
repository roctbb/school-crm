<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-brand sticky-top shadow-sm">
        <div class="container">
            <router-link :to="{name: 'Objects'}" class="navbar-brand d-flex align-items-center gap-2">
                <span class="brand-logo-wrap" aria-hidden="true">
                    <img src="@/assets/logo.png" alt="" class="brand-logo" />
                </span>
                <span>{{ $appName }}</span>
            </router-link>

            <!-- Кнопка (тогглер) -->
            <button
                class="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarContent"
                aria-controls="navbarContent"
                aria-expanded="false"
                aria-label="Открыть меню"
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
                            :to="{name: 'Objects'}"
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
                            :to="{name: 'Forms'}"
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
                            :to="{name: 'Import'}"
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
                            :to="{name: 'Invitations'}"
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
                        <i class="bi bi-person-circle me-1"></i>
                        <span class="user-name">{{ profile.name }}</span>
                    </button>

                    <ul
                        class="dropdown-menu dropdown-menu-end"
                        aria-labelledby="userMenuButton"
                    >
                        <template v-if="hasAdminAccess()">
                            <li><h6 class="dropdown-header">Администрирование</h6></li>
                            <li>
                                <router-link
                                    :to="{name: 'UsersAdmin'}"
                                    class="dropdown-item"
                                    active-class="active"
                                >
                                    <i class="bi bi-people me-2"></i>Пользователи
                                </router-link>
                            </li>
                            <li>
                                <router-link
                                    :to="{name: 'ObjectTypesAdmin'}"
                                    class="dropdown-item"
                                    active-class="active"
                                >
                                    <i class="bi bi-diagram-3 me-2"></i>Типы сущностей
                                </router-link>
                            </li>
                            <li>
                                <router-link
                                    :to="{name: 'FormCategoriesAdmin'}"
                                    class="dropdown-item"
                                    active-class="active"
                                >
                                    <i class="bi bi-ui-checks-grid me-2"></i>Категории форм
                                </router-link>
                            </li>
                            <li>
                                <router-link
                                    :to="{name: 'OAuthClientsAdmin'}"
                                    class="dropdown-item"
                                    active-class="active"
                                >
                                    <i class="bi bi-box-arrow-in-right me-2"></i>Внешний вход
                                </router-link>
                            </li>
                            <li><hr class="dropdown-divider" /></li>
                        </template>
                        <li>
                            <router-link
                                :to="{name: 'ChangePassword'}"
                                class="dropdown-item"
                                active-class="active"
                            >
                                <i class="bi bi-key me-2"></i>Изменить пароль
                            </router-link>
                        </li>
                        <li>
                            <router-link
                                :to="{name: 'NotificationSettings'}"
                                class="dropdown-item"
                                active-class="active"
                            >
                                <i class="bi bi-bell me-2"></i>Уведомления
                            </router-link>
                        </li>
                        <li>
                            <button
                                class="dropdown-item"
                                type="button"
                                @click="handleLogout"
                            >
                                <i class="bi bi-box-arrow-right me-2"></i>Выйти
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
        async handleLogout() {
            await this.logout();
            this.$router.push("/login");
        },
    },
};
</script>

<style scoped>
.bg-brand {
    background-color: #397698;
}

.navbar {
    --bs-navbar-padding-y: 0.55rem;
    z-index: 1030;
}

.navbar-brand {
    font-size: 1.05rem;
    font-weight: 650;
    letter-spacing: -0.01em;
}

.brand-logo-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    overflow: hidden;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.28);
}

.brand-logo {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.nav-link {
    margin-inline: 0.08rem;
    padding-inline: 0.75rem !important;
    border-radius: 0.45rem;
}

.nav-link:hover,
.nav-link:focus-visible {
    background: rgba(255, 255, 255, 0.09);
}

.nav-link.active {
    color: #fff;
    background: rgba(255, 255, 255, 0.16);
}

.btn-user-menu {
    color: #fff;
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.14);
}

.btn-user-menu:hover,
.btn-user-menu:focus-visible,
.btn-user-menu.show {
    color: #fff;
    background-color: rgba(255, 255, 255, 0.16);
    border-color: rgba(255, 255, 255, 0.25);
}

@media (max-width: 991.98px) {
    .navbar-collapse {
        padding-top: 0.75rem;
        padding-bottom: 0.25rem;
    }

    .nav-link {
        margin-bottom: 0.2rem;
    }

    .btn-user-menu {
        width: 100%;
        margin-top: 0.4rem;
        text-align: left;
    }

    .dropdown-menu-end {
        width: 100%;
    }
}
</style>
