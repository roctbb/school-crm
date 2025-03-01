<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="/">Силаэдр CRM</a>

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
import useMainStore from "@/stores/mainStore.js"; // Подключаем Pinia store
import {mapActions, mapState} from "pinia"; // Для работы с состоянием из Pinia

export default {
    name: "Navbar",
    computed: {
        ...mapState(useMainStore, ["profile"]), // Отображаем профиль пользователя из стора
    },
    methods: {
        logout() {
            useMainStore().logout();
            this.$router.push("/login");
        }
    },
};
</script>

<style scoped>
.navbar {
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
}

.dropdown-menu-end {
    right: 0;
    left: auto;
}
</style>