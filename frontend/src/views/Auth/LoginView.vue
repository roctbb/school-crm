<template>
    <div class="login-page auth-page">
        <div class="card auth-card p-4">
            <div class="text-center mb-3">
                <img src="@/assets/logo.png" :alt="$appName" class="auth-logo">
            </div>

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
                    <label for="password" class="form-label">Пароль <span class="text-danger">*</span></label>
                    <div class="input-group">
                        <input
                            :type="showPassword ? 'text' : 'password'"
                            id="password"
                            class="form-control"
                            v-model="password"
                            required
                        />
                        <button
                            class="btn btn-light icon-button"
                            type="button"
                            :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                            @click="showPassword = !showPassword"
                        >
                            <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                        </button>
                    </div>
                </div>
                <!-- Кнопка входа -->
                <button type="submit" class="btn btn-primary w-100">Войти</button>
            </form>

            <!-- Ссылки -->
            <div class="d-flex justify-content-between align-items-center mt-3">
                <router-link to="/password/email">Забыли пароль?</router-link>
                <router-link to="/register">Регистрация</router-link>
            </div>
        </div>
    </div>
</template>

<script lang="js">
import useMainStore from "@/stores/mainStore.js";
import { login } from "@/api/auth_api.js";

export default {
    name: "LoginView",
    data() {
        return {
            email: "",
            password: "",
            error: "",
            showPassword: false,
        };
    },
    methods: {
        async handleLogin() {
            try {
                const token = await login(this.email, this.password);
                await useMainStore().setToken(token);
                const redirect = typeof this.$route.query.redirect === 'string'
                    && this.$route.query.redirect.startsWith('/')
                    && !this.$route.query.redirect.startsWith('//')
                    ? this.$route.query.redirect
                    : '/';
                this.$router.push(redirect);
                this.error = "";
            } catch (error) {
                this.error = error.message || "Не удалось соединиться с сервером.";
            }
        },
    },
};
</script>

<style scoped>
</style>
