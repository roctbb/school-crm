<script setup>
import {useId} from 'vue';
import {hasAdminAccess} from '@/utils/access.js';

defineProps({modelValue: {type: Boolean, default: false}});
const emit = defineEmits(['update:modelValue']);
const id = useId();
</script>

<template>
    <label v-if="hasAdminAccess()" :for="id" class="show-hidden-control" :class="{'is-active': modelValue}">
        <input :id="id" class="form-check-input m-0" type="checkbox" :checked="modelValue"
               @change="emit('update:modelValue', $event.target.checked)" />
        <span>Показывать скрытые</span>
    </label>
</template>

<style scoped>
.show-hidden-control {
    display: inline-flex;
    align-items: center;
    align-self: center;
    gap: 0.5rem;
    width: fit-content;
    padding: 0.4rem 0.65rem;
    margin: 0;
    border: 1px solid var(--silaeder-border);
    border-radius: 0.5rem;
    color: var(--bs-secondary-color);
    font-size: 0.8125rem;
    line-height: 1.25;
    white-space: nowrap;
    cursor: pointer;
}
.show-hidden-control.is-active {
    color: var(--silaeder-primary-dark);
    background: var(--silaeder-primary-soft);
    border-color: var(--silaeder-primary);
}
.show-hidden-control:focus-within {
    outline: 2px solid var(--silaeder-primary);
    outline-offset: 2px;
}
</style>
