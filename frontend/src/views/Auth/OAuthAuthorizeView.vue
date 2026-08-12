<template>
    <div class="authorize-page d-flex justify-content-center align-items-center min-vh-100 p-3">
        <div class="card shadow-sm authorize-card">
            <div class="card-body p-4">
                <div class="text-center mb-4">
                    <img src="@/assets/logo.png" alt="Силаэдр CRM" class="logo mb-3" />
                    <h3>Вход через Силаэдр CRM</h3>
                </div>

                <div v-if="loading" class="text-center text-muted py-4">Проверяем запрос…</div>
                <div v-else-if="error" class="alert alert-danger mb-0">
                    {{ error }}
                </div>
                <template v-else-if="authorization">
                    <p>
                        Приложение <strong>{{ authorization.client.name }}</strong>
                        запрашивает доступ к вашему аккаунту.
                    </p>
                    <p v-if="authorization.client.description" class="text-muted">
                        {{ authorization.client.description }}
                    </p>

                    <div class="border rounded p-3 mb-3">
                        <div><strong>{{ authorization.identity.name }}</strong></div>
                        <div class="text-muted">{{ authorization.identity.email }}</div>
                        <div class="small text-muted">
                            Объект: {{ authorization.identity.type }} · Роль доступа: {{ authorization.identity.role }}
                        </div>
                    </div>

                    <h6>Приложение получит:</h6>
                    <ul class="mb-4">
                        <li v-for="scope in authorization.scopes" :key="scope">
                            {{ scopeLabels[scope] || scope }}
                        </li>
                    </ul>

                    <div v-if="actionError" class="alert alert-danger">{{ actionError }}</div>
                    <div class="d-flex gap-2 justify-content-end">
                        <button class="btn btn-outline-secondary" type="button" :disabled="submitting" @click="decide(false)">
                            Отказать
                        </button>
                        <button class="btn btn-primary" type="button" :disabled="submitting" @click="decide(true)">
                            {{ submitting ? 'Переходим…' : 'Продолжить' }}
                        </button>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import {fetchAuthorizationRequest, submitAuthorizationDecision} from '@/api/oidc_api.js';

const scalarQuery = query => Object.fromEntries(
    Object.entries(query).map(([key, value]) => [key, Array.isArray(value) ? value[0] : value])
);

export default {
    name: 'OAuthAuthorizeView',
    data() {
        return {
            loading: true,
            submitting: false,
            authorization: null,
            error: null,
            actionError: null,
            scopeLabels: {
                openid: 'идентификатор аккаунта',
                profile: 'имя и тип привязанного объекта CRM',
                email: 'адрес электронной почты',
                roles: 'роль в CRM',
                avatar: 'фотография профиля',
                offline_access: 'долговременный доступ с обновлением сессии',
            },
        };
    },
    computed: {
        requestParams() {
            return scalarQuery(this.$route.query);
        },
    },
    async created() {
        try {
            this.authorization = await fetchAuthorizationRequest(this.requestParams);
            if (!this.authorization.requires_consent) {
                await this.decide(true);
            }
        } catch (error) {
            this.error = error.message || 'Некорректный запрос авторизации.';
        } finally {
            this.loading = false;
        }
    },
    methods: {
        async decide(decision) {
            this.submitting = true;
            this.actionError = null;
            try {
                const result = await submitAuthorizationDecision(this.requestParams, decision);
                window.location.assign(result.redirect_uri);
            } catch (error) {
                this.actionError = error.message || 'Не удалось завершить авторизацию.';
                this.submitting = false;
            }
        },
    },
};
</script>

<style scoped>
.authorize-page {
    background: #f4f7f9;
}

.authorize-card {
    width: 100%;
    max-width: 520px;
}

.logo {
    max-width: 130px;
    height: auto;
}
</style>
