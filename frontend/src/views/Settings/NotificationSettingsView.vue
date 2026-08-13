<template>
    <BaseLayout>
            <PageHeader
                title="Настройки уведомлений"
                subtitle="По электронной почте уведомления приходят всегда. Telegram можно подключить дополнительно."
            />

            <div class="card notification-card">
                <div class="card-body">
                    <div class="d-flex align-items-start gap-3">
                        <i class="bi bi-telegram telegram-icon"></i>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                                <div>
                                    <h5 class="card-title mb-1">Telegram</h5>
                                    <p v-if="loading" class="text-muted mb-0">Проверяем подключение…</p>
                                    <template v-else-if="settings?.connected">
                                        <p class="text-success mb-1">
                                            <i class="bi bi-check-circle-fill me-1"></i>Подключён
                                        </p>
                                        <p class="text-muted small mb-0">
                                            {{ telegramAccount }}
                                        </p>
                                    </template>
                                    <p v-else class="text-muted mb-0">Получайте копии уведомлений в боте.</p>
                                </div>

                                <button
                                    v-if="settings?.connected"
                                    class="btn btn-outline-danger"
                                    type="button"
                                    :disabled="saving"
                                    @click="disconnect"
                                >
                                    Отключить
                                </button>
                                <button
                                    v-else
                                    class="btn btn-primary"
                                    type="button"
                                    :disabled="saving || !settings?.configured"
                                    @click="connect"
                                >
                                    <i class="bi bi-telegram me-1"></i>
                                    {{ saving ? 'Создаём ссылку…' : 'Подключить Telegram' }}
                                </button>
                            </div>

                            <div v-if="waitingForBot && !settings?.connected" class="alert alert-info mt-3 mb-0">
                                В открывшемся Telegram нажмите <strong>Start</strong>. Эта страница обновится автоматически.
                            </div>
                            <div v-if="settings && !settings.configured" class="alert alert-warning mt-3 mb-0">
                                Telegram-бот пока не настроен администратором.
                            </div>
                            <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
                        </div>
                    </div>
                </div>
            </div>
    </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import PageHeader from '@/components/common/PageHeader.vue';
import {
    createTelegramLink,
    disconnectTelegram,
    fetchTelegramSettings,
} from '@/api/notifications_api.js';


export default {
    name: 'NotificationSettingsView',
    components: {BaseLayout, PageHeader},
    data() {
        return {
            settings: null,
            loading: true,
            saving: false,
            waitingForBot: false,
            error: null,
            pollTimer: null,
        };
    },
    computed: {
        telegramAccount() {
            if (this.settings?.username) return `@${this.settings.username}`;
            return this.settings?.first_name || 'Telegram-аккаунт';
        },
    },
    async created() {
        await this.refresh();
    },
    beforeUnmount() {
        this.stopPolling();
    },
    methods: {
        async refresh(silent = false) {
            if (!silent) this.loading = true;
            try {
                this.settings = await fetchTelegramSettings();
                this.error = null;
                if (this.settings.connected) {
                    this.waitingForBot = false;
                    this.stopPolling();
                }
            } catch (error) {
                this.error = error.message || 'Не удалось загрузить настройки.';
            } finally {
                this.loading = false;
            }
        },
        async connect() {
            const telegramWindow = window.open('', '_blank');
            this.saving = true;
            this.error = null;
            try {
                const link = await createTelegramLink();
                if (telegramWindow) telegramWindow.location = link.url;
                else window.location.href = link.url;
                this.waitingForBot = true;
                this.startPolling();
            } catch (error) {
                if (telegramWindow) telegramWindow.close();
                this.error = error.message || 'Не удалось открыть Telegram.';
            } finally {
                this.saving = false;
            }
        },
        startPolling() {
            this.stopPolling();
            this.pollTimer = window.setInterval(() => this.refresh(true), 2500);
        },
        stopPolling() {
            if (this.pollTimer) window.clearInterval(this.pollTimer);
            this.pollTimer = null;
        },
        async disconnect() {
            if (!window.confirm('Отключить уведомления в Telegram?')) return;
            this.saving = true;
            this.error = null;
            try {
                await disconnectTelegram();
                await this.refresh(true);
            } catch (error) {
                this.error = error.message || 'Не удалось отключить Telegram.';
            } finally {
                this.saving = false;
            }
        },
    },
};
</script>

<style scoped>
.notification-card {
    max-width: 760px;
}

.telegram-icon {
    color: #229ed9;
    font-size: 2.5rem;
    line-height: 1;
}
</style>
