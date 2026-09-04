<template>
    <BaseLayout>
        <PageHeader
            title="Пользователи"
            subtitle="Учетные записи и ссылки для самостоятельной установки нового пароля."
        />

        <Loading v-if="loading" />
        <div v-else-if="loadError" class="alert alert-danger" role="alert">{{ loadError }}</div>
        <div v-else class="row g-3">
            <div class="col-lg-5">
                <div class="surface-card overflow-hidden">
                    <div class="p-3 border-bottom">
                        <div class="input-group">
                            <span class="input-group-text bg-white text-muted"><i class="bi bi-search"></i></span>
                            <input
                                v-model.trim="search"
                                class="form-control"
                                type="search"
                                placeholder="Имя или email"
                                aria-label="Поиск пользователей"
                            />
                        </div>
                    </div>
                    <div class="list-group list-group-flush user-list">
                        <router-link
                            v-for="user in filteredUsers"
                            :key="user.id"
                            :to="{name: 'UsersAdmin', params: {userId: user.id}}"
                            class="list-group-item list-group-item-action px-3 py-3"
                            :class="{active: selectedUser?.id === user.id}"
                        >
                            <div class="d-flex justify-content-between gap-3">
                                <div class="overflow-hidden">
                                    <div class="fw-semibold text-truncate">{{ user.name || 'Без имени' }}</div>
                                    <div class="small text-truncate" :class="selectedUser?.id === user.id ? 'text-white-50' : 'text-muted'">
                                        {{ user.email }}
                                    </div>
                                </div>
                                <span class="badge align-self-start" :class="selectedUser?.id === user.id ? 'text-bg-light' : roleBadge(user.role)">
                                    {{ roleLabel(user.role) }}
                                </span>
                            </div>
                        </router-link>
                        <div v-if="!filteredUsers.length" class="p-4 text-center text-muted">
                            Пользователи не найдены.
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-7">
                <EmptyState
                    v-if="!selectedUser"
                    icon="bi-person-lines-fill"
                    title="Выберите пользователя"
                    description="Здесь появятся данные учетной записи и действие для сброса пароля."
                />
                <div v-else class="card">
                    <div class="card-body p-4">
                        <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
                            <div>
                                <h2 class="h4 mb-1">{{ selectedUser.name || 'Без имени' }}</h2>
                                <a :href="`mailto:${selectedUser.email}`">{{ selectedUser.email }}</a>
                            </div>
                            <span class="badge" :class="roleBadge(selectedUser.role)">
                                {{ roleLabel(selectedUser.role) }}
                            </span>
                        </div>

                        <dl class="row mb-4 small">
                            <dt class="col-sm-4 text-muted fw-normal">ID</dt>
                            <dd class="col-sm-8">{{ selectedUser.id }}</dd>
                            <dt class="col-sm-4 text-muted fw-normal">Создан</dt>
                            <dd class="col-sm-8">{{ formatDate(selectedUser.created_at) }}</dd>
                            <dt class="col-sm-4 text-muted fw-normal">Связанный объект</dt>
                            <dd class="col-sm-8 mb-0">
                                <router-link
                                    v-if="selectedUser.identity_object"
                                    :to="objectRoute(selectedUser.identity_object)"
                                >
                                    {{ selectedUser.identity_object.name }}
                                    <i class="bi bi-box-arrow-up-right ms-1 small"></i>
                                </router-link>
                                <span v-else class="text-muted">Не привязан</span>
                            </dd>
                        </dl>

                        <div class="border rounded-3 p-3 bg-body-tertiary">
                            <h3 class="h6">Сброс пароля</h3>
                            <p class="small text-muted mb-3">
                                Новая ссылка отменит ранее созданную. Передайте ее только этому пользователю.
                            </p>
                            <button
                                class="btn btn-primary"
                                type="button"
                                :disabled="generating"
                                @click="generateAndCopy"
                            >
                                <span v-if="generating" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                                <i v-else class="bi bi-clipboard-check me-2"></i>
                                {{ generating ? 'Создаем…' : 'Сгенерировать и скопировать ссылку' }}
                            </button>

                            <div v-if="resetUrl" class="input-group mt-3">
                                <input
                                    ref="resetUrlInput"
                                    :value="resetUrl"
                                    class="form-control"
                                    type="text"
                                    readonly
                                    aria-label="Ссылка для сброса пароля"
                                    @focus="$event.target.select()"
                                />
                                <button class="btn btn-outline-secondary" type="button" @click="copyResetUrl">
                                    <i class="bi bi-copy me-1"></i> Копировать
                                </button>
                            </div>
                            <div v-if="message" class="small text-success mt-2" role="status">{{ message }}</div>
                            <div v-if="actionError" class="small text-danger mt-2" role="alert">{{ actionError }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import EmptyState from '@/components/common/EmptyState.vue';
import Loading from '@/components/common/Loading.vue';
import PageHeader from '@/components/common/PageHeader.vue';
import {fetchUsers, generatePasswordResetLink} from '@/api/users_api.js';

const ROLE_LABELS = {
    admin: 'Администратор',
    teacher: 'Учитель',
    student: 'Ученик',
    user: 'Пользователь',
};

export default {
    name: 'UsersAdminView',
    components: {BaseLayout, EmptyState, Loading, PageHeader},
    data() {
        return {
            users: [],
            search: '',
            loading: true,
            loadError: '',
            generating: false,
            resetUrl: '',
            message: '',
            actionError: '',
        };
    },
    computed: {
        selectedUser() {
            const userId = Number(this.$route.params.userId);
            return this.users.find(user => user.id === userId) || null;
        },
        filteredUsers() {
            const query = this.search.toLocaleLowerCase('ru');
            if (!query) return this.users;
            return this.users.filter(user => (
                (user.name || '').toLocaleLowerCase('ru').includes(query)
                || user.email.toLocaleLowerCase('ru').includes(query)
            ));
        },
    },
    watch: {
        selectedUser() {
            this.resetUrl = '';
            this.message = '';
            this.actionError = '';
        },
    },
    async created() {
        try {
            this.users = await fetchUsers();
            if (!this.selectedUser && this.users.length && !this.$route.params.userId) {
                await this.$router.replace({name: 'UsersAdmin', params: {userId: this.users[0].id}});
            }
        } catch (error) {
            this.loadError = error.message || 'Не удалось загрузить пользователей.';
        } finally {
            this.loading = false;
        }
    },
    methods: {
        roleLabel(role) {
            return ROLE_LABELS[role] || role;
        },
        roleBadge(role) {
            return role === 'admin' ? 'text-bg-danger' : role === 'teacher' ? 'text-bg-primary' : 'text-bg-secondary';
        },
        formatDate(value) {
            if (!value) return '—';
            return new Intl.DateTimeFormat('ru-RU', {dateStyle: 'long'}).format(new Date(value));
        },
        objectRoute(object) {
            return {name: 'ObjectDetails', params: {object_type: object.type, object_id: object.id}};
        },
        async copyText(value) {
            if (navigator.clipboard?.writeText) {
                try {
                    await navigator.clipboard.writeText(value);
                    return true;
                } catch (_error) {
                    // В небезопасном контексте пробуем совместимый запасной способ.
                }
            }
            const input = this.$refs.resetUrlInput;
            if (!input) return false;
            input.focus();
            input.select();
            return document.execCommand('copy');
        },
        async generateAndCopy() {
            if (!this.selectedUser || this.generating) return;
            this.generating = true;
            this.resetUrl = '';
            this.message = '';
            this.actionError = '';
            try {
                const result = await generatePasswordResetLink(this.selectedUser.id);
                this.resetUrl = result.reset_url;
                await this.$nextTick();
                const copied = await this.copyText(this.resetUrl);
                this.message = copied
                    ? 'Новая ссылка создана и скопирована.'
                    : 'Новая ссылка создана. Скопируйте ее из поля ниже.';
            } catch (error) {
                this.actionError = error.message || 'Не удалось создать ссылку.';
            } finally {
                this.generating = false;
            }
        },
        async copyResetUrl() {
            const copied = await this.copyText(this.resetUrl);
            this.message = copied ? 'Ссылка скопирована.' : '';
            this.actionError = copied ? '' : 'Не удалось скопировать ссылку автоматически.';
        },
    },
};
</script>

<style scoped>
.user-list {
    max-height: min(68vh, 46rem);
    overflow-y: auto;
}

dt,
dd {
    padding-block: 0.35rem;
}
</style>
