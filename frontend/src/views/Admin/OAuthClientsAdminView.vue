<template>
    <BaseLayout>
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h2 class="mb-1">Внешний вход</h2>
                    <p class="text-muted mb-0">OIDC-клиенты для LMS, внутренней валюты и других сервисов.</p>
                </div>
                <button class="btn btn-success" type="button" @click="startCreate">
                    <i class="bi bi-plus-lg me-1"></i> Новый клиент
                </button>
            </div>

            <div v-if="clientSecret" class="alert alert-warning">
                <strong>Сохраните client secret сейчас — повторно он показан не будет.</strong>
                <div class="input-group mt-2">
                    <input :value="clientSecret" class="form-control font-monospace" readonly />
                    <button class="btn btn-outline-dark" type="button" @click="copySecret">Копировать</button>
                </div>
            </div>

            <div class="row g-3">
                <div class="col-lg-4">
                    <div class="list-group">
                        <button
                            v-for="client in clients"
                            :key="client.id"
                            class="list-group-item list-group-item-action"
                            :class="{active: draft?.id === client.id}"
                            type="button"
                            @click="selectClient(client)"
                        >
                            <div class="d-flex justify-content-between align-items-center">
                                <strong>{{ client.name }}</strong>
                                <span v-if="!client.is_active" class="badge bg-secondary">выключен</span>
                            </div>
                            <code :class="{'text-white': draft?.id === client.id}">{{ client.client_id }}</code>
                        </button>
                        <div v-if="!clients.length" class="list-group-item text-muted">Клиентов пока нет.</div>
                    </div>
                </div>

                <div class="col-lg-8">
                    <div v-if="!draft" class="alert alert-light border">Выберите или создайте OIDC-клиент.</div>
                    <form v-else @submit.prevent="save">
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div v-if="saved" class="alert alert-success">Настройки сохранены.</div>

                        <div class="card mb-3">
                            <div class="card-header">Основное</div>
                            <div class="card-body row g-3">
                                <div class="col-md-7">
                                    <label class="form-label">Название сервиса</label>
                                    <input v-model.trim="draft.name" class="form-control" maxlength="120" required />
                                </div>
                                <div class="col-md-5">
                                    <label class="form-label">client_id</label>
                                    <input
                                        v-model.trim="draft.client_id"
                                        class="form-control font-monospace"
                                        :readonly="Boolean(draft.id)"
                                        pattern="[a-z][a-z0-9._-]{2,119}"
                                        required
                                    />
                                </div>
                                <div class="col-12">
                                    <label class="form-label">Описание на странице подтверждения</label>
                                    <textarea v-model="draft.description" class="form-control" rows="2" maxlength="4000"></textarea>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-check">
                                        <input v-model="draft.is_confidential" class="form-check-input" type="checkbox" />
                                        <span class="form-check-label">Конфиденциальный серверный клиент</span>
                                    </label>
                                    <div class="form-text">Для Flask-приложения этот флаг должен быть включён.</div>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-check">
                                        <input v-model="draft.is_active" class="form-check-input" type="checkbox" />
                                        <span class="form-check-label">Клиент активен</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div class="card mb-3">
                            <div class="card-header">Разрешённые адреса</div>
                            <div class="card-body">
                                <label class="form-label">Redirect URI, по одному на строку</label>
                                <textarea v-model="draft.redirectUrisText" class="form-control font-monospace" rows="4" required></textarea>
                                <div class="form-text mb-3">Адрес должен совпадать полностью. HTTP разрешён только для localhost.</div>

                                <label class="form-label">Post-logout Redirect URI, по одному на строку</label>
                                <textarea v-model="draft.logoutUrisText" class="form-control font-monospace" rows="3"></textarea>
                            </div>
                        </div>

                        <div class="card mb-3">
                            <div class="card-header">Доступ и данные</div>
                            <div class="card-body row g-3">
                                <div class="col-md-6">
                                    <h6>Роли</h6>
                                    <label v-for="role in roles" :key="role" class="form-check">
                                        <input v-model="draft.allowed_roles" :value="role" class="form-check-input" type="checkbox" />
                                        <span class="form-check-label">{{ role }}</span>
                                    </label>
                                </div>
                                <div class="col-md-6">
                                    <h6>Scopes</h6>
                                    <label v-for="scope in scopes" :key="scope" class="form-check">
                                        <input
                                            v-model="draft.allowed_scopes"
                                            :value="scope"
                                            class="form-check-input"
                                            type="checkbox"
                                            :disabled="scope === 'openid'"
                                        />
                                        <span class="form-check-label font-monospace">{{ scope }}</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div class="d-flex justify-content-between mb-5">
                            <button
                                v-if="draft.id && draft.is_confidential"
                                class="btn btn-outline-warning"
                                type="button"
                                :disabled="saving"
                                @click="rotateSecret"
                            >
                                Сменить secret
                            </button>
                            <span v-else></span>
                            <button class="btn btn-primary" type="submit" :disabled="saving">
                                {{ saving ? 'Сохранение…' : 'Сохранить' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import {
    createOAuthClient,
    fetchOAuthClients,
    rotateOAuthClientSecret,
    updateOAuthClient,
} from '@/api/oidc_api.js';

const clone = value => JSON.parse(JSON.stringify(value));
const lines = value => value.split('\n').map(item => item.trim()).filter(Boolean);

export default {
    name: 'OAuthClientsAdminView',
    components: {BaseLayout},
    data() {
        return {
            clients: [],
            draft: null,
            saving: false,
            saved: false,
            error: null,
            clientSecret: null,
            roles: ['student', 'teacher', 'admin'],
            scopes: ['openid', 'profile', 'email', 'roles', 'offline_access'],
        };
    },
    async created() {
        try {
            this.clients = await fetchOAuthClients();
            if (this.clients.length) this.selectClient(this.clients[0]);
            else this.startCreate();
        } catch (error) {
            this.error = error.message || 'Не удалось загрузить OIDC-клиентов.';
        }
    },
    methods: {
        prepareDraft(client) {
            return {
                ...clone(client),
                redirectUrisText: (client.redirect_uris || []).join('\n'),
                logoutUrisText: (client.post_logout_redirect_uris || []).join('\n'),
            };
        },
        selectClient(client) {
            this.draft = this.prepareDraft(client);
            this.error = null;
            this.saved = false;
            this.clientSecret = null;
        },
        startCreate() {
            this.draft = this.prepareDraft({
                id: null,
                client_id: '',
                name: '',
                description: '',
                redirect_uris: [],
                post_logout_redirect_uris: [],
                allowed_scopes: ['openid', 'profile', 'email', 'roles'],
                allowed_roles: ['student', 'teacher', 'admin'],
                is_confidential: true,
                is_active: true,
            });
            this.error = null;
            this.saved = false;
            this.clientSecret = null;
        },
        payload() {
            return {
                client_id: this.draft.client_id,
                name: this.draft.name,
                description: this.draft.description,
                redirect_uris: lines(this.draft.redirectUrisText),
                post_logout_redirect_uris: lines(this.draft.logoutUrisText),
                allowed_scopes: [...this.draft.allowed_scopes],
                allowed_roles: [...this.draft.allowed_roles],
                is_confidential: this.draft.is_confidential,
                is_active: this.draft.is_active,
            };
        },
        async save() {
            this.saving = true;
            this.error = null;
            this.saved = false;
            try {
                const result = this.draft.id
                    ? await updateOAuthClient(this.draft.id, this.payload())
                    : await createOAuthClient(this.payload());
                this.clientSecret = result.client_secret || null;
                delete result.client_secret;
                const index = this.clients.findIndex(client => client.id === result.id);
                if (index >= 0) this.clients[index] = result;
                else this.clients.push(result);
                this.draft = this.prepareDraft(result);
                this.saved = true;
            } catch (error) {
                this.error = error.message || 'Не удалось сохранить OIDC-клиент.';
            } finally {
                this.saving = false;
            }
        },
        async rotateSecret() {
            if (!window.confirm('Старый secret и все активные токены этого клиента перестанут работать. Продолжить?')) return;
            this.saving = true;
            this.error = null;
            try {
                const result = await rotateOAuthClientSecret(this.draft.id);
                this.clientSecret = result.client_secret;
                delete result.client_secret;
                const index = this.clients.findIndex(client => client.id === result.id);
                this.clients[index] = result;
                this.draft = this.prepareDraft(result);
            } catch (error) {
                this.error = error.message || 'Не удалось сменить secret.';
            } finally {
                this.saving = false;
            }
        },
        async copySecret() {
            await navigator.clipboard.writeText(this.clientSecret);
        },
    },
};
</script>
