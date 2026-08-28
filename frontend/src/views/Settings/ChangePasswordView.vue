<template>
    <BaseLayout>
        <PageHeader
            title="Изменение пароля"
            subtitle="После сохранения остальные активные сеансы будут завершены."
        />

        <div class="card password-card">
            <div class="card-body p-4">
                <div v-if="success" class="alert alert-success" role="status">
                    {{ success }}
                </div>
                <div v-if="error" class="alert alert-danger" role="alert">
                    {{ error }}
                </div>

                <form @submit.prevent="handleSubmit">
                    <div class="mb-3">
                        <label for="currentPassword" class="form-label">
                            Текущий пароль <span class="text-danger">*</span>
                        </label>
                        <div class="input-group">
                            <input
                                id="currentPassword"
                                ref="currentPassword"
                                v-model="currentPassword"
                                :type="showPasswords ? 'text' : 'password'"
                                class="form-control"
                                :class="{'is-invalid': errorField === 'current_password'}"
                                autocomplete="current-password"
                                maxlength="256"
                                required
                            />
                            <button
                                class="btn btn-outline-secondary"
                                type="button"
                                :aria-label="showPasswords ? 'Скрыть пароли' : 'Показать пароли'"
                                @click="showPasswords = !showPasswords"
                            >
                                <i class="bi" :class="showPasswords ? 'bi-eye-slash' : 'bi-eye'"></i>
                            </button>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="newPassword" class="form-label">
                            Новый пароль <span class="text-danger">*</span>
                        </label>
                        <input
                            id="newPassword"
                            ref="newPassword"
                            v-model="newPassword"
                            :type="showPasswords ? 'text' : 'password'"
                            class="form-control"
                            :class="{'is-invalid': errorField === 'new_password'}"
                            autocomplete="new-password"
                            minlength="6"
                            maxlength="32"
                            required
                        />
                        <div class="form-text">От 6 до 32 символов.</div>
                    </div>

                    <div class="mb-4">
                        <label for="newPasswordConfirmation" class="form-label">
                            Подтверждение нового пароля <span class="text-danger">*</span>
                        </label>
                        <input
                            id="newPasswordConfirmation"
                            ref="newPasswordConfirmation"
                            v-model="newPasswordConfirmation"
                            :type="showPasswords ? 'text' : 'password'"
                            class="form-control"
                            :class="{'is-invalid': errorField === 'new_password_confirmation'}"
                            autocomplete="new-password"
                            minlength="6"
                            maxlength="32"
                            required
                        />
                    </div>

                    <button class="btn btn-primary" type="submit" :disabled="saving">
                        <span
                            v-if="saving"
                            class="spinner-border spinner-border-sm me-2"
                            aria-hidden="true"
                        ></span>
                        {{ saving ? 'Сохраняем…' : 'Изменить пароль' }}
                    </button>
                </form>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import PageHeader from '@/components/common/PageHeader.vue';
import {changePassword} from '@/api/auth_api.js';
import useMainStore from '@/stores/mainStore.js';

export default {
    name: 'ChangePasswordView',
    components: {BaseLayout, PageHeader},
    data() {
        return {
            currentPassword: '',
            newPassword: '',
            newPasswordConfirmation: '',
            showPasswords: false,
            saving: false,
            success: '',
            error: '',
            errorField: null,
        };
    },
    methods: {
        focusField(field) {
            const refs = {
                current_password: 'currentPassword',
                new_password: 'newPassword',
                new_password_confirmation: 'newPasswordConfirmation',
            };
            this.$nextTick(() => this.$refs[refs[field]]?.focus());
        },
        async handleSubmit() {
            this.success = '';
            this.error = '';
            this.errorField = null;

            if (this.newPassword !== this.newPasswordConfirmation) {
                this.error = 'Новый пароль и подтверждение не совпадают.';
                this.errorField = 'new_password_confirmation';
                this.focusField(this.errorField);
                return;
            }

            this.saving = true;
            try {
                const session = await changePassword({
                    currentPassword: this.currentPassword,
                    newPassword: this.newPassword,
                    newPasswordConfirmation: this.newPasswordConfirmation,
                });
                await useMainStore().setSession(session, session.persistent);
                this.currentPassword = '';
                this.newPassword = '';
                this.newPasswordConfirmation = '';
                this.success = 'Пароль изменён. Остальные активные сеансы завершены.';
            } catch (error) {
                this.error = error.message || 'Не удалось изменить пароль.';
                this.errorField = error.field || null;
                if (this.errorField) this.focusField(this.errorField);
            } finally {
                this.saving = false;
            }
        },
    },
};
</script>

<style scoped>
.password-card {
    max-width: 620px;
}
</style>
