<template>
    <div class="login-page auth-page">
        <div class="card auth-card p-4">
            <div class="text-center mb-3">
                <img src="@/assets/logo.png" :alt="$appName" class="auth-logo">
            </div>

            <h3 class="card-title text-center mb-3">Вход в систему</h3>

            <div class="alert alert-warning my-3 px-3" role="status" v-if="sessionMessage">
                {{ sessionMessage }}
            </div>
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
                <div class="form-check mb-3">
                    <input
                        id="remember-me"
                        v-model="rememberMe"
                        class="form-check-input"
                        type="checkbox"
                    />
                    <label class="form-check-label" for="remember-me">
                        Не выходить из системы
                    </label>
                </div>
                <!-- Кнопка входа -->
                <button type="submit" class="btn btn-primary w-100" :disabled="isSubmitting">
                    <span
                        v-if="isSubmitting"
                        class="spinner-border spinner-border-sm me-2"
                        aria-hidden="true"
                    ></span>
                    {{ isSubmitting ? 'Входим…' : 'Войти' }}
                </button>
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
            sessionMessage: "",
            showPassword: false,
            rememberMe: false,
            isSubmitting: false,
        };
    },
    methods: {
        async handleLogin() {
            this.error = "";
            this.sessionMessage = "";
            this.isSubmitting = true;
            try {
                const session = await login(this.email, this.password, this.rememberMe);
                const isValid = await useMainStore().setSession(session, this.rememberMe);
                if (!isValid) return;
                const redirect = typeof this.$route.query.redirect === 'string'
                    && this.$route.query.redirect.startsWith('/')
                    && !this.$route.query.redirect.startsWith('//')
                    ? this.$route.query.redirect
                    : '/';
                this.$router.push(redirect);
                this.error = "";
            } catch (error) {
                this.error = error.code
                    ? error.message
                    : "Не удалось соединиться с сервером. Проверьте подключение и попробуйте снова.";
            } finally {
                this.isSubmitting = false;
            }
        },
    },
    created() {
        this.sessionMessage = useMainStore().consumeAuthMessage();
    },
};
</script>

<style scoped>
</style>
