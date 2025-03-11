<template>
    <div class="register-page d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4" style="width: 100%; max-width: 400px;">
            <h3 class="card-title text-center mb-3">Регистрация</h3>

            <div class="alert alert-danger my-2 p-2" v-if="error">{{ error }}</div>

            <!-- Форма регистрации -->
            <form @submit.prevent="handleRegister" class="mt-1">
                <div class="mb-3">
                    <label for="name" class="form-label">Имя</label>
                    <input
                        type="text"
                        id="name"
                        class="form-control"
                        v-model="name"
                        :class="{ 'is-invalid': errors.name }"
                        required
                        autofocus
                    />
                    <div class="invalid-feedback">Введите имя</div>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input
                        type="email"
                        id="email"
                        class="form-control"
                        v-model="email"
                        :class="{ 'is-invalid': errors.email }"
                        required
                    />
                    <div class="invalid-feedback">Введите корректный email</div>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Пароль</label>
                    <input
                        type="password"
                        id="password"
                        class="form-control"
                        v-model="password"
                        :class="{ 'is-invalid': errors.password }"
                        required
                    />
                    <div class="invalid-feedback">Введите пароль</div>
                </div>
                <div class="mb-3">
                    <label for="confirmPassword" class="form-label">Подтвердите пароль</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        class="form-control"
                        v-model="confirmPassword"
                        :class="{ 'is-invalid': errors.confirmPassword }"
                        required
                    />
                    <div class="invalid-feedback">Пароли не совпадают</div>
                </div>
                <div class="mb-3">
                    <label for="invite" class="form-label">Код приглашения</label>
                    <input
                        type="text"
                        id="invite"
                        class="form-control"
                        v-model="invite"
                        :class="{ 'is-invalid': errors.invite }" :disabled="!errors.invite"
                    />
                    <div class="invalid-feedback">Приглашение отсутствует или недействительно</div>
                </div>
                <button type="submit" class="btn btn-primary w-100">Зарегистрироваться</button>
            </form>

            <!-- Ссылка на вход -->
            <div class="mt-3 text-center">
                <p class="mb-0">
                    Уже есть аккаунт?
                    <router-link to="/login">Войти</router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js"; // Pinia Store
import {mapActions} from "pinia";
import {register, login} from "@/api/auth_api.js"; // Импорты из auth_api.js

export default {
    name: "RegisterView",
    data() {
        return {
            name: "",
            email: "",
            password: "",
            confirmPassword: "",
            invite: "", // Поле для кода приглашения
            error: "",
            errors: {
                name: false,
                email: false,
                password: false,
                confirmPassword: false,
                invite: false,
            },
        };
    },
    methods: {
        ...mapActions(useMainStore, ["setToken"]),
        validateForm() {
            // Проверяем каждое поле и выставляем соответствующий флаг ошибок
            this.errors.name = !this.name.trim();
            this.errors.email = !this.email.trim(); // Можно добавить более строгую проверку на email
            this.errors.password = !this.password.trim();
            this.errors.invite = !this.invite.trim();
            this.errors.confirmPassword = this.password !== this.confirmPassword;

            // Если есть хотя бы одна ошибка, возвращаем false
            return !Object.values(this.errors).includes(true);
        },

        async handleRegister() {
            console.log("Handling register form")
            // Проверяем форму, если есть ошибки - выходим
            if (!this.validateForm()) {
                return;
            }

            try {
                // Выполняем регистрацию
                await register({
                    name: this.name,
                    email: this.email,
                    password: this.password,
                    invite: this.invite || null, // Если код приглашения не заполнен, передаем null
                });

                // После успешной регистрации автоматически логинимся
                const token = await login(this.email, this.password);
                this.setToken(token);
                this.error = "";
                this.errors = {}
                this.$router.push("/"); // Перенаправляем пользователя на главную страницу
            } catch (error) {
                console.error("Registration failed:", error);
                if (error.field) {
                    this.errors[error.field] = true;
                }
                if (error.message) {
                    this.error = error.message;
                } else {
                    this.error = "Ошибка регистрации. Проверьте данные и попробуйте снова.";
                }
            }
        },
    },
    created() {
        const inviteCode = this.$route.query.invite;
        if (inviteCode) {
            this.invite = inviteCode;
        }
        else {
            this.errors.invite = true;
        }

    }
};
</script>

<style>
.register-page {
    background-color: #f8f9fa;
}

.is-invalid {
    border-color: #dc3545;
}

.invalid-feedback {
    display: block;
    color: #dc3545;
}
</style>