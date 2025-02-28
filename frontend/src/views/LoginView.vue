<template>
    <div class="login-page d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4" style="width: 100%; max-width: 400px;">
            <h3 class="card-title text-center mb-3">Вход в систему</h3>

            <div class="alert alert-danger my-3 px-3" v-if="error">{{ error }}</div>

            <!-- Форма входа -->
            <form @submit.prevent="handleLogin">
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
                <button type="submit" class="btn btn-primary w-100">Войти</button>
            </form>

            <!-- Ссылка на регистрацию -->
            <div class="mt-3 text-center">
                <p class="mb-0">
                    Нет аккаунта?
                    <router-link to="/register">Зарегистрироваться</router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore"; // Подключаем Pinia-хранилище
import {mapActions} from "pinia"; // Операции Pinia
import {login} from "@/api/auth.js";

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
        ...mapActions(useMainStore, ["setToken"]),
        async handleLogin() {
            try {
                this.setToken(await login(this.email, this.password));
                this.$router.push("/");
                this.error = "";
            } catch (error) {
                console.error("Login failed:", error);
                this.error = "Неверный email или пароль. Попробуйте снова!"
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