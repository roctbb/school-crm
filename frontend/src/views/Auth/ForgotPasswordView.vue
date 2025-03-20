<!-- src/views/Auth/ForgotPasswordView.vue -->
<template>
    <div class="forgot-password-page d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4" style="width: 100%; max-width: 400px;">
            <div class="text-center mb-3">
                <img src="@/assets/logo.png" alt="Logo" style="max-width: 150px; height: auto;">
            </div>
            <h3 class="card-title text-center mb-3">Восстановление пароля</h3>

            <div v-if="success" class="alert alert-success my-3 px-3">
                {{ success }}
            </div>
            <div v-if="error" class="alert alert-danger my-3 px-3">
                {{ error }}
            </div>

            <form @submit.prevent="handlePasswordReset">
                <div class="mb-3">
                    <label for="email" class="form-label">Введите ваш Email</label>
                    <input
                        type="email"
                        id="email"
                        class="form-control"
                        v-model="email"
                        required
                    />
                </div>
                <button type="submit" class="btn btn-primary w-100">Отправить</button>
            </form>

            <div class="mt-3 text-center">
                <router-link to="/login">Вернуться к входу</router-link>
            </div>
        </div>
    </div>
</template>

<script>
import {sendPasswordResetEmail} from "@/api/auth_api.js";

export default {
    name: "ForgotPasswordView",
    data() {
        return {
            email: "",
            error: "",
            success: "",
        };
    },
    methods: {
        async handlePasswordReset() {
            try {
                this.error = "";
                this.success = "";
                await sendPasswordResetEmail(this.email);
                // Предположим, что при успехе сервер возвращает сообщение:
                this.success = "Письмо для сброса пароля отправлено.";
            } catch (err) {
                this.error = err.message || "Произошла ошибка при отправке письма.";
            }
        },
    },
};
</script>

<style>
.forgot-password-page {
    background-color: #f8f9fa;
}
</style>