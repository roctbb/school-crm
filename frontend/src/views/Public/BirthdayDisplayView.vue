<template>
    <main class="birthday-screen">
        <div class="decoration decoration-one" aria-hidden="true"></div>
        <div class="decoration decoration-two" aria-hidden="true"></div>
        <header class="screen-header">
            <div class="school-brand"><img src="@/assets/logo.png" alt="" /><span>{{ APP_NAME }}</span></div>
            <div class="screen-clock"><span>{{ currentDate }}</span><strong>{{ currentTime }}</strong></div>
        </header>

        <section class="screen-heading">
            <div>
                <p class="eyebrow">НА ЭТОЙ НЕДЕЛЕ <span v-if="data">· {{ formatDate(data.week_start) }} — {{ formatDate(data.week_end) }}</span></p>
                <h1>С днём <span>рождения!</span><span class="heading-star" aria-hidden="true">✳</span></h1>
                <p class="heading-note">Пусть впереди будет много открытий и счастливых дней.</p>
            </div>
            <div v-if="todayCount" class="today-count"><i class="bi bi-stars" aria-hidden="true"></i><span>Поздравляем сегодня<strong>{{ todayCount }} {{ peopleWord(todayCount) }}</strong></span></div>
        </section>

        <section v-if="loading && !data" class="screen-message" role="status">
            <i class="bi bi-gift" aria-hidden="true"></i><h2>Собираем поздравления…</h2>
        </section>
        <section v-else-if="!data" class="screen-message" role="alert">
            <i class="bi bi-display" aria-hidden="true"></i><h2>{{ unavailable ? 'Экран недоступен' : 'Нет связи с сервером' }}</h2><p>{{ error }}</p>
        </section>
        <section v-else-if="!data.students.length" class="screen-message">
            <span class="empty-star" aria-hidden="true">✳</span><h2>На этой неделе именинников нет</h2><p>А поводы для радости есть каждый день!</p>
        </section>
        <section v-else class="birthday-grid" :class="{'single-row': pageSize <= 3 || visibleStudents.length <= 3}" aria-label="Именинники недели">
            <article v-for="student in visibleStudents" :key="student.id" class="birthday-card" :class="{'is-today': student.is_today}">
                <div class="card-day"><span>{{ student.is_today ? '★ Сегодня' : weekday(student.date) }}</span><time :datetime="student.date">{{ formatDate(student.date) }}</time></div>
                <BirthdayPortrait :name="student.name" :path="student.photo_path" :access-key="accessKey" :revision="revision" />
                <h2>{{ student.name }}</h2>
                <p>{{ student.is_today ? 'С днём рождения!' : 'Принимает поздравления' }}</p>
            </article>
        </section>

        <footer class="screen-footer">
            <span class="footer-note"><span class="status-dot" :class="{'offline': error}"></span>{{ error && data ? 'Нет связи · пробуем подключиться' : 'Хорошо, что вы с нами' }}</span>
            <div v-if="pageCount > 1" class="page-controls">
                <span>{{ page + 1 }} / {{ pageCount }}</span>
                <button @click="paused = !paused" :aria-label="paused ? 'Продолжить переключение' : 'Приостановить переключение'"><i :class="paused ? 'bi bi-play-fill' : 'bi bi-pause-fill'"></i></button>
                <button @click="nextPage" aria-label="Следующая страница"><i class="bi bi-arrow-right"></i></button>
            </div>
            <button class="fullscreen-button" @click="toggleFullscreen"><i class="bi bi-arrows-fullscreen" aria-hidden="true"></i><span>На весь экран</span></button>
        </footer>
        <p v-if="fullscreenError" class="fullscreen-error" role="status">{{ fullscreenError }}</p>
    </main>
</template>

<script setup>
import {computed, onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {useRoute} from 'vue-router';
import {APP_NAME} from '@/config/app.js';
import BirthdayPortrait from '@/components/widgets/BirthdayPortrait.vue';
import {fetchBirthdayResource} from '@/api/birthdays_api.js';

const route = useRoute();
const accessKey = computed(() => new URLSearchParams(route.hash.slice(1)).get('key') || '');
const data = ref(null);
const loading = ref(true);
const unavailable = ref(false);
const error = ref('');
const fullscreenError = ref('');
const now = ref(new Date());
const page = ref(0);
const revision = ref(0);
const pageSize = ref(6);
const paused = ref(false);
const timezone = computed(() => data.value?.timezone || 'Europe/Moscow');
const currentDate = computed(() => now.value.toLocaleDateString('ru-RU', {day: 'numeric', month: 'long', weekday: 'long', timeZone: timezone.value}));
const currentTime = computed(() => now.value.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit', timeZone: timezone.value}));
const todayCount = computed(() => data.value?.students.filter(student => student.is_today).length || 0);
const pageCount = computed(() => Math.max(1, Math.ceil((data.value?.students.length || 0) / pageSize.value)));
const visibleStudents = computed(() => data.value?.students.slice(page.value * pageSize.value, (page.value + 1) * pageSize.value) || []);
let controller;
let refreshTimer;
let clockTimer;
let pageTimer;
let previousTitle;
let robotsTag;

function parseDate(value) { return new Date(`${value}T12:00:00`); }
function formatDate(value) { return parseDate(value).toLocaleDateString('ru-RU', {day: 'numeric', month: 'long'}); }
function weekday(value) { return parseDate(value).toLocaleDateString('ru-RU', {weekday: 'long'}); }
function peopleWord(count) { return count % 10 === 1 && count % 100 !== 11 ? 'именинника' : 'именинников'; }
function nextPage() { page.value = (page.value + 1) % pageCount.value; }
function resize() {
    pageSize.value = window.innerWidth < 700 ? 2 : window.innerHeight < 760 ? 3 : 6;
    page.value = Math.min(page.value, pageCount.value - 1);
}
function clearStaleDay() {
    if (!data.value) return;
    const today = new Intl.DateTimeFormat('en-CA', {timeZone: timezone.value, year: 'numeric', month: '2-digit', day: '2-digit'}).format(now.value);
    if (today !== data.value.today) { data.value = null; page.value = 0; }
}
async function refresh() {
    controller?.abort();
    if (!accessKey.value) {
        unavailable.value = true;
        error.value = 'Откройте полную ссылку из настроек администратора.';
        loading.value = false;
        data.value = null;
        return;
    }
    const request = new AbortController();
    controller = request;
    const timeout = window.setTimeout(() => request.abort(), 20000);
    try {
        const result = await fetchBirthdayResource('/public/birthdays', accessKey.value, request.signal);
        if (controller !== request || request.signal.aborted) return;
        if (data.value?.today !== result.today) page.value = 0;
        data.value = result;
        page.value = Math.min(page.value, pageCount.value - 1);
        revision.value += 1;
        error.value = '';
        unavailable.value = false;
    } catch (e) {
        if (controller !== request) return;
        unavailable.value = e.code === 403;
        error.value = unavailable.value ? e.message : 'Проверяем подключение. Страница восстановится автоматически.';
        if (unavailable.value) data.value = null;
        else clearStaleDay();
    } finally {
        window.clearTimeout(timeout);
        if (controller === request) loading.value = false;
    }
}
function resume() { now.value = new Date(); clearStaleDay(); refresh(); }
async function toggleFullscreen() {
    fullscreenError.value = '';
    try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await document.documentElement.requestFullscreen();
    } catch { fullscreenError.value = 'Используйте полноэкранный режим в меню браузера.'; }
}
watch(accessKey, () => { data.value = null; page.value = 0; loading.value = true; refresh(); });
onMounted(() => {
    previousTitle = document.title;
    document.title = `Дни рождения · ${APP_NAME}`;
    robotsTag = document.createElement('meta');
    robotsTag.name = 'robots';
    robotsTag.content = 'noindex, nofollow, noarchive';
    document.head.appendChild(robotsTag);
    resize();
    refresh();
    refreshTimer = window.setInterval(refresh, 60000);
    clockTimer = window.setInterval(() => {
        now.value = new Date();
        if (data.value) {
            clearStaleDay();
            if (!data.value) refresh();
        }
    }, 1000);
    pageTimer = window.setInterval(() => { if (!paused.value) nextPage(); }, 15000);
    window.addEventListener('resize', resize);
    window.addEventListener('online', resume);
    document.addEventListener('visibilitychange', resume);
});
onBeforeUnmount(() => {
    controller?.abort();
    window.clearInterval(refreshTimer);
    window.clearInterval(clockTimer);
    window.clearInterval(pageTimer);
    window.removeEventListener('resize', resize);
    window.removeEventListener('online', resume);
    document.removeEventListener('visibilitychange', resume);
    document.title = previousTitle;
    robotsTag?.remove();
});
</script>

<style scoped>
.birthday-screen { --ink: #234e43; position: relative; isolation: isolate; display: flex; flex-direction: column; gap: 2.3vh; height: 100dvh; min-height: 540px; padding: 3vh 3.5vw 2vh; overflow: hidden; color: var(--ink); background: #f6f6ed; font-family: 'Trebuchet MS', system-ui, sans-serif; }
.decoration { position: absolute; z-index: -1; pointer-events: none; border-radius: 50%; }
.decoration-one { width: 45vw; height: 45vw; background: #e3ecd9; top: -29vw; right: -10vw; }
.decoration-two { width: 38vw; height: 38vw; border: 1px solid #cedecf; left: -27vw; bottom: -23vw; box-shadow: 0 0 0 3vw #f6f6ed, 0 0 0 calc(3vw + 1px) #cedecf; }
.screen-header, .screen-heading, .screen-footer { display: flex; align-items: center; justify-content: space-between; gap: 2vw; flex-shrink: 0; }
.school-brand { display: flex; align-items: center; gap: .7vw; font-weight: 700; font-size: clamp(15px, 1.15vw, 28px); }
.school-brand img { width: clamp(34px, 2.6vw, 60px); aspect-ratio: 1; object-fit: contain; border-radius: 50%; }
.screen-clock { display: flex; align-items: center; gap: 1.2vw; font-size: clamp(14px, 1.15vw, 26px); }
.screen-clock strong { font-size: clamp(22px, 1.8vw, 44px); font-variant-numeric: tabular-nums; }
.screen-heading { padding-block: .8vh 1vh; }
.eyebrow { margin: 0 0 .8vh; font-size: clamp(12px, .95vw, 23px); letter-spacing: .1em; font-weight: 700; }
.eyebrow span { letter-spacing: .02em; font-weight: 400; }
h1 { margin: 0; font-size: clamp(34px, 4.1vw, 106px); font-weight: 750; line-height: 1.12; letter-spacing: -.055em; }
h1 > span:first-child { color: #bb513b; }
.heading-star { display: inline-block; margin-left: 1.5vw; color: #d7ab3e; transform: rotate(-12deg); }
.heading-note { margin: 1vh 0 0; color: #60776a; font-size: clamp(14px, 1.2vw, 28px); }
.today-count { display: flex; align-items: center; gap: 1vw; padding: 1.4vh 1.5vw; border: 1px solid #dbc88a; border-radius: 18px; background: #f4e9be; font-size: clamp(13px, 1vw, 25px); }
.today-count i { font-size: 2.2vw; }
.today-count strong { display: block; font-size: clamp(20px, 1.75vw, 42px); }
.birthday-grid { min-height: 0; flex: 1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-rows: repeat(2, minmax(0, 1fr)); gap: 1.6vh 1.2vw; }
.birthday-grid.single-row { grid-template-rows: minmax(0, 1fr); }
.birthday-card { --portrait-size: min(14.5vh, 11vw); display: flex; flex-direction: column; align-items: center; justify-content: center; min-width: 0; min-height: 0; position: relative; padding: 1.4vh 1.2vw; border: 1px solid #dbe3d7; border-radius: 22px; background: #fffffff0; box-shadow: 0 5px 20px #234e4304; }
.birthday-card.is-today { background: #f8edc4; border: 2px solid #d9b95d; }
.single-row .birthday-card { --portrait-size: min(26vh, 17vw); }
.card-day { width: 100%; display: flex; justify-content: space-between; align-items: center; gap: .5vw; margin-bottom: 1.2vh; font-size: clamp(12px, 1vw, 24px); color: #657a69; }
.card-day > span { text-transform: capitalize; }
.is-today .card-day > span { padding: .35vh .65vw; border-radius: 30px; background: #285b49; color: white; font-weight: 700; }
.birthday-card h2 { max-width: 100%; margin: 1.2vh 0 .3vh; font-size: clamp(18px, 1.65vw, 44px); line-height: 1.12; font-weight: 700; text-align: center; overflow-wrap: anywhere; }
.birthday-card p { margin: 0; color: #718070; font-size: clamp(12px, .9vw, 23px); }
.is-today p { color: #986426; }
.screen-message { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 1.5vh; }
.screen-message > i, .empty-star { font-size: clamp(60px, 6vw, 150px); color: #c7a151; }
.screen-message h2 { font-size: clamp(24px, 2.5vw, 62px); }
.screen-message p { font-size: clamp(16px, 1.4vw, 32px); color: #60776a; }
.screen-footer { min-height: 3.5vh; color: #617669; font-size: clamp(12px, .95vw, 23px); }
.footer-note, .page-controls { display: flex; align-items: center; gap: .7vw; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: #759d71; }
.status-dot.offline { background: #c99844; }
.screen-footer button { display: inline-flex; align-items: center; justify-content: center; gap: .5vw; min-width: 32px; min-height: 32px; border: 0; border-radius: 8px; background: transparent; color: inherit; }
.screen-footer button:hover { background: #e1e8db; }
.fullscreen-error { position: absolute; right: 3.5vw; bottom: 7vh; max-width: 80vw; padding: 12px; border-radius: 8px; background: #fff; }
@media (max-width: 1000px) { .today-count { display: none; } }
@media (max-width: 699px) {
    .birthday-screen { padding: 18px; gap: 16px; min-height: 650px; }
    .screen-clock { flex-direction: column-reverse; align-items: flex-end; gap: 0; font-size: 11px; }
    .screen-heading { padding: 0; }
    h1 { font-size: 34px; }
    .heading-star { display: none; }
    .eyebrow { font-size: 10px; }
    .heading-note { font-size: 12px; }
    .birthday-grid, .birthday-grid.single-row { grid-template-columns: 1fr; grid-template-rows: repeat(2, minmax(0, 1fr)); }
    .birthday-card, .single-row .birthday-card { --portrait-size: min(12vh, 90px); padding: 10px 18px; }
    .birthday-card h2 { font-size: 20px; }
    .card-day { margin-bottom: 10px; }
    .fullscreen-button span { display: none; }
}
</style>
