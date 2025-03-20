<template>
    <div class="login-page d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4" style="width: 100%; max-width: 400px;">
            <!-- Блок с логотипом -->
            <div class="text-center mb-3">
                <img src="@/assets/logo.png" alt="Logo" style="max-width: 150px; height: auto;">
            </div>

            <h3 class="card-title text-center mb-3">Вход в систему</h3>

            <div class="alert alert-danger my-3 px-3" v-if="error">{{ error }}</div>

            <!-- Форма входа -->
            <form @submit.prevent="handleLogin">
                <!-- Поля ввода -->
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input
                        type="email"
                        id="email"
                        class="form-control"
                        v-model="email"
                        required
                        autofocus
                    />
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Пароль</label>
                    <input
                        type="password"
                        id="password"
                        class="form-control"
                        v-model="password"
                        required
                    />
                </div>
                <!-- Кнопка входа -->
                <button type="submit" class="btn btn-primary w-100">Войти</button>
            </form>

            <!-- Блок со ссылками -->
            <div class="d-flex justify-content-between align-items-center mt-3">
                <router-link to="/password/email">Забыли пароль?</router-link>
                <router-link to="/register">Регистрация</router-link>
            </div>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import { login } from "@/api/auth_api.js";

export default {
    name: "LoginView",
    data() {
        return {
            email: "",
            password: "",
            error: ""
        };
    },
    methods: {
        async handleLogin() {
            try {
                await useMainStore().setToken(await login(this.email, this.password));
                this.$router.push("/");
                this.error = "";
            } catch (error) {
                this.error = error.message || "Не удалось соединиться с сервером.";
            }
        },
    },
};
</script>

<style>
.login-page {
    background-color: #f8f9fa;
}
</style>