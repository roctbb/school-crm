<template>
    <BaseLayout>
        <PageHeader title="Экран дней рождения" subtitle="Открытая страница с фотографиями учеников для большого экрана в холле." />
        <div class="card display-settings">
            <div class="card-body p-4">
                <h2 class="h5"><i class="bi bi-display me-2"></i>Именинники недели</h2>
                <p class="text-muted">С понедельника по воскресенье, с особым выделением тех, у кого день рождения сегодня.
                    Страница обновляется автоматически, карточки переключаются каждые 15 секунд.</p>
                <p v-if="loading">Загружаем настройки…</p>
                <template v-else-if="settings">
                    <template v-if="settings.enabled">
                        <label class="form-label fw-semibold" for="birthday-link">Ссылка для экрана</label>
                        <input id="birthday-link" class="form-control" :value="displayUrl" readonly @focus="$event.target.select()" />
                        <p class="form-text">По этой ссылке без входа доступны имена, фотографии и дни рождения учеников на текущей неделе.</p>
                        <div class="d-flex flex-wrap gap-2 mt-3">
                            <button class="btn btn-primary" @click="copyLink">{{ copied ? 'Скопировано' : 'Скопировать ссылку' }}</button>
                            <a class="btn btn-outline-primary" :href="displayUrl" target="_blank" rel="noopener noreferrer">Открыть экран <i class="bi bi-box-arrow-up-right ms-1"></i></a>
                        </div>
                        <hr class="my-4" />
                        <p class="small text-muted">При замене ссылки старая перестанет работать. Новую нужно будет открыть на экране в холле.</p>
                        <div class="d-flex flex-wrap gap-2">
                            <button class="btn btn-outline-secondary" :disabled="saving" @click="changeLink('POST')">Заменить ссылку</button>
                            <button class="btn btn-outline-danger" :disabled="saving" @click="changeLink('DELETE')">Отключить экран</button>
                        </div>
                    </template>
                    <template v-else>
                        <p>Публичная ссылка пока отключена.</p>
                        <button class="btn btn-primary" :disabled="saving" @click="changeLink('POST')">Создать ссылку</button>
                    </template>
                    <p class="small text-muted mt-4 mb-0">Часовой пояс: {{ settings.timezone }}. Если фотографии нет, на карточке будут инициалы.</p>
                </template>
                <div v-if="error" class="alert alert-danger mt-3 mb-0" role="alert">{{ error }}</div>
                <button v-if="!loading && !settings" class="btn btn-outline-primary mt-3" @click="load">Повторить</button>
                <p class="visually-hidden" role="status">{{ copied ? 'Ссылка скопирована' : '' }}</p>
            </div>
        </div>
    </BaseLayout>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue';
import BaseLayout from '@/components/layouts/BaseLayout.vue';
import PageHeader from '@/components/common/PageHeader.vue';
import {birthdayDisplaySettings} from '@/api/birthdays_api.js';

const settings = ref(null);
const loading = ref(true);
const saving = ref(false);
const error = ref('');
const copied = ref(false);
const displayUrl = computed(() => settings.value?.path ? new URL(settings.value.path, window.location.origin).href : '');

async function load() {
    loading.value = true;
    error.value = '';
    try { settings.value = await birthdayDisplaySettings(); }
    catch (e) { error.value = e.message || 'Не удалось загрузить настройки.'; }
    finally { loading.value = false; }
}
async function changeLink(method) {
    if (settings.value.enabled && !window.confirm(method === 'DELETE'
        ? 'Отключить публичный экран? Текущая ссылка перестанет работать.'
        : 'Заменить ссылку? Старую ссылку на экране нужно будет обновить.')) return;
    saving.value = true;
    error.value = '';
    copied.value = false;
    try { settings.value = await birthdayDisplaySettings(method); }
    catch (e) { error.value = e.message || 'Не удалось сохранить настройки.'; }
    finally { saving.value = false; }
}
async function copyLink() {
    error.value = '';
    try { await navigator.clipboard.writeText(displayUrl.value); copied.value = true; }
    catch { error.value = 'Выделите ссылку в поле и скопируйте её вручную.'; }
}
onMounted(load);
</script>

<style scoped>
.display-settings { max-width: 880px; }
</style>
