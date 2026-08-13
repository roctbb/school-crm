<template>
    <BaseLayout>
            <PageHeader title="Внешний вход" subtitle="OIDC-клиенты для LMS, внутренней валюты и других сервисов.">
                <template #actions>
                <button class="btn btn-primary" type="button" @click="startCreate">
                    <i class="bi bi-plus-lg me-1"></i> Новый клиент
                </button>
                </template>
            </PageHeader>

            <div v-if="clientSecret" class="alert alert-warning">
                <strong>Сохраните client secret сейчас — повторно он показан не будет.</strong>
                <div class="input-group mt-2">
                    <input :value="clientSecret" class="form-control font-monospace" readonly />
                    <button class="btn btn-outline-dark" type="button" @click="copySecret">Копировать</button>
                </div>
            </div>

            <div class="row g-3">
                <div class="col-lg-4">
                    <div class="list-group sticky-lg-top client-list">
                        <div class="list-group-item p-2">
                            <div class="input-group input-group-sm">
                                <span class="input-group-text bg-white text-muted"><i class="bi bi-search"></i></span>
                                <input v-model="listSearch" class="form-control" type="search" placeholder="Найти клиент…" aria-label="Поиск OIDC-клиентов" />
                            </div>
                        </div>
                        <button
                            v-for="client in filteredClients"
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
                        <div v-else-if="!filteredClients.length" class="list-group-item text-muted small">Ничего не найдено.</div>
                    </div>
                </div>

                <div class="col-lg-8">
                    <div v-if="!draft" class="alert alert-light border">Выберите или создайте OIDC-клиент.</div>
                    <form v-else @submit.prevent="save" @input="saved = false" @change="saved = false">
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div v-if="saved" class="alert alert-success">Настройки сохранены.</div>

                        <nav class="editor-section-nav d-flex flex-wrap gap-2 mb-3" aria-label="Разделы редактора">
                            <a class="btn btn-sm btn-light" href="#client-main">Основное</a>
                            <a class="btn btn-sm btn-light" href="#client-uris">Адреса</a>
                            <a class="btn btn-sm btn-light" href="#client-access">Доступ</a>
                        </nav>

                        <div id="client-main" class="card editor-card mb-3">
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
                                <div class="col-12">
                                    <hr />
                                    <label class="form-check">
                                        <input
                                            v-model="draft.can_send_notifications"
                                            class="form-check-input"
                                            type="checkbox"
                                            :disabled="!draft.is_confidential"
                                        />
                                        <span class="form-check-label">Разрешить отправку уведомлений</span>
                                    </label>
                                    <div class="form-text">
                                        Сервис сможет отправлять пользователям уведомления по email и в подключённый Telegram,
                                        используя этот client_id и client secret.
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="client-uris" class="card editor-card mb-3">
                            <div class="card-header">Разрешённые адреса</div>
                            <div class="card-body">
                                <label class="form-label">Redirect URI, по одному на строку</label>
                                <textarea v-model="draft.redirectUrisText" class="form-control font-monospace" rows="4" required></textarea>
                                <div class="form-text mb-3">Адрес должен совпадать полностью. HTTP разрешён только для localhost.</div>

                                <label class="form-label">Post-logout Redirect URI, по одному на строку</label>
                                <textarea v-model="draft.logoutUrisText" class="form-control font-monospace" rows="3"></textarea>
                            </div>
                        </div>

                        <div id="client-access" class="card editor-card mb-3">
                            <div class="card-header">Доступ и данные</div>
                            <div class="card-body row g-3">
                                <div class="col-md-6">
                                    <h6>Роли</h6>
                                    <label v-for="role in roles" :key="role" class="form-check">
                                        <input v-model="draft.allowed_roles" :value="role" class="form-check-input" type="checkbox" />
                                        <span class="form-check-label">{{ roleLabel(role) }}</span>
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

                        <div class="editor-save-bar">
                            <button
                                v-if="draft.id && draft.is_confidential"
                                class="btn btn-outline-warning"
                                type="button"
                                :disabled="saving"
                                @click="rotateSecret"
                            >
                                Сменить secret
                            </button>
                            <span v-else class="small" :class="hasUnsavedChanges ? 'text-warning-emphasis' : 'text-muted'">
                                {{ hasUnsavedChanges ? 'Есть несохранённые изменения' : 'Изменений нет' }}
                            </span>
                            <div class="d-flex align-items-center gap-3">
                                <span v-if="draft.id && hasUnsavedChanges" class="small text-warning-emphasis d-none d-md-inline">
                                    Есть несохранённые изменения
                                </span>
                                <button class="btn btn-primary" type="submit" :disabled="saving">
                                    {{ saving ? 'Сохранение…' : 'Сохранить' }}
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import PageHeader from '@/components/common/PageHeader.vue';
import {
    createOAuthClient,
    fetchOAuthClients,
    rotateOAuthClientSecret,
    updateOAuthClient,
} from '@/api/oidc_api.js';
import unsavedChangesMixin from '@/mixins/unsavedChangesMixin.js';

const clone = value => JSON.parse(JSON.stringify(value));
const lines = value => value.split('\n').map(item => item.trim()).filter(Boolean);

export default {
    name: 'OAuthClientsAdminView',
    components: {BaseLayout, PageHeader},
    mixins: [unsavedChangesMixin],
    data() {
        return {
            clients: [],
            draft: null,
            saving: false,
            saved: false,
            error: null,
            clientSecret: null,
            initialSnapshot: '',
            listSearch: '',
            roles: ['student', 'teacher', 'admin'],
            scopes: ['openid', 'profile', 'email', 'roles', 'avatar', 'offline_access'],
        };
    },
    computed: {
        filteredClients() {
            const query = this.listSearch.trim().toLowerCase();
            if (!query) return this.clients;
            return this.clients.filter(client => (
                client.name.toLowerCase().includes(query) || client.client_id.toLowerCase().includes(query)
            ));
        },
        hasUnsavedChanges() {
            return Boolean(this.draft && this.initialSnapshot && JSON.stringify(this.payload()) !== this.initialSnapshot);
        },
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
            if (this.draft?.id === client.id) return;
            if (this.hasUnsavedChanges && !window.confirm('Отменить несохранённые изменения и открыть другой клиент?')) return;
            this.draft = this.prepareDraft(client);
            this.initialSnapshot = JSON.stringify(this.payload());
            this.error = null;
            this.saved = false;
            this.clientSecret = null;
        },
        startCreate() {
            if (this.hasUnsavedChanges && !window.confirm('Отменить несохранённые изменения и создать новый клиент?')) return;
            this.draft = this.prepareDraft({
                id: null,
                client_id: '',
                name: '',
                description: '',
                redirect_uris: [],
                post_logout_redirect_uris: [],
                allowed_scopes: ['openid', 'profile', 'email', 'roles', 'avatar'],
                allowed_roles: ['student', 'teacher', 'admin'],
                is_confidential: true,
                is_active: true,
                can_send_notifications: false,
            });
            this.error = null;
            this.saved = false;
            this.clientSecret = null;
            this.initialSnapshot = JSON.stringify(this.payload());
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
                can_send_notifications: this.draft.is_confidential
                    && this.draft.can_send_notifications,
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
                this.initialSnapshot = JSON.stringify(this.payload());
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
                this.initialSnapshot = JSON.stringify(this.payload());
            } catch (error) {
                this.error = error.message || 'Не удалось сменить secret.';
            } finally {
                this.saving = false;
            }
        },
        async copySecret() {
            await navigator.clipboard.writeText(this.clientSecret);
        },
        roleLabel(role) {
            return {student: 'Ученик', teacher: 'Учитель', admin: 'Администратор'}[role] || role;
        },
    },
};
</script>

<style scoped>
.client-list {
    top: 4.75rem;
}
</style>
