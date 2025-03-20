<template>
    <div class="reset-password-page d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4" style="width: 100%; max-width: 400px;">
            <div class="text-center mb-3">
                <img src="@/assets/logo.png" alt="Logo" style="max-width: 150px; height: auto;">
            </div>

            <h3 class="card-title text-center mb-3">Сброс пароля</h3>

            <div v-if="success" class="alert alert-success my-3 px-3">
                {{ success }}
            </div>
            <div v-if="error" class="alert alert-danger my-3 px-3">
                {{ error }}
            </div>

            <form @submit.prevent="handleReset">
                <div class="mb-3">
                    <label for="password" class="form-label">Новый пароль</label>
                    <input
                        type="password"
                        id="password"
                        class="form-control"
                        v-model="password"
                        required
                    />
                </div>

                <div class="mb-3">
                    <label for="confirmPassword" class="form-label">Подтверждение пароля</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        class="form-control"
                        v-model="passwordConfirm"
                        required
                    />
                </div>

                <button type="submit" class="btn btn-primary w-100">
                    Сбросить пароль
                </button>
            </form>

            <div class="mt-3 text-center">
                <router-link to="/login">Вернуться к входу</router-link>
            </div>
        </div>
    </div>
</template>

<script>
import { resetPassword } from "@/api/auth_api.js";
// Импортируем Pinia-хранилище, чтобы сохранить токен
import useMainStore from "@/stores/mainStore.js";

export default {
    name: "ResetPasswordView",
    data() {
        return {
            token: "",
            password: "",
            passwordConfirm: "",
            success: "",
            error: "",
        };
    },
    mounted() {
        // Предположим, токен приходит через query: ?token=...
        this.token = this.$route.query.token || "";
    },
    methods: {
        async handleReset() {
            try {
                this.success = "";
                this.error = "";

                if (!this.password || this.password !== this.passwordConfirm) {
                    throw new Error("Пароли не совпадают.");
                }
                if (!this.token) {
                    throw new Error("Отсутствует токен сброса пароля.");
                }

                // resetPassword возвращает, например, { access_token, message }
                const result = await resetPassword({
                    token: this.token,
                    password: this.password,
                });

                this.success = result.message || "Пароль успешно сброшен.";

                // Если сервер возвращает access_token, то делаем «автовход»
                if (result.access_token) {
                    await useMainStore().setToken(result.access_token);
                    // Переход на главную страницу после входа
                    this.$router.push("/");
                }

            } catch (err) {
                this.error = err.message || "Ошибка при сбросе пароля.";
            }
        },
    },
};
</script>

<style>
.reset-password-page {
    background-color: #f8f9fa;
}
</style>