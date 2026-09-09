<template>
    <div class="portrait">
        <img v-if="photoUrl && !failed" :src="photoUrl" :alt="name" @error="failed = true" />
        <span v-else aria-hidden="true">{{ initials }}</span>
    </div>
</template>

<script setup>
import {computed, onBeforeUnmount, ref, watch} from 'vue';
import {fetchBirthdayResource} from '@/api/birthdays_api.js';

const props = defineProps({name: String, path: String, accessKey: String, revision: Number});
const photoUrl = ref('');
const failed = ref(false);
const initials = computed(() => props.name?.trim().split(/\s+/).slice(0, 2).map(part => part[0]).join(''));
let controller;
function clearPhoto() {
    if (photoUrl.value) URL.revokeObjectURL(photoUrl.value);
    photoUrl.value = '';
}
watch(() => [props.path, props.accessKey, props.revision], async () => {
    controller?.abort();
    const request = new AbortController();
    controller = request;
    const timeout = window.setTimeout(() => request.abort(), 15000);
    if (!props.path) { clearPhoto(); window.clearTimeout(timeout); return; }
    try {
        const blob = await fetchBirthdayResource(props.path, props.accessKey, request.signal, true);
        if (request.signal.aborted) return;
        clearPhoto();
        photoUrl.value = URL.createObjectURL(blob);
        failed.value = false;
    } catch (error) {
        if (controller === request && error.name !== 'AbortError') clearPhoto();
    } finally { window.clearTimeout(timeout); }
}, {immediate: true});
onBeforeUnmount(() => { controller?.abort(); clearPhoto(); });
</script>

<style scoped>
.portrait { width: var(--portrait-size); height: var(--portrait-size); flex: 0 0 auto; border-radius: 50%; overflow: hidden; background: #e1ebe2; display: grid; place-items: center; box-shadow: 0 0 0 7px #ffffffa8; }
.portrait img { width: 100%; height: 100%; object-fit: cover; object-position: center 25%; }
.portrait span { color: #56735d; font-size: calc(var(--portrait-size) * .32); font-weight: 650; }
</style>
