import {defineAsyncComponent} from 'vue';

export const availableWidgets = {
    active_events: defineAsyncComponent(() => import('@/components/widgets/ActiveEventsWidget.vue')),
    birthdays: defineAsyncComponent(() => import('@/components/widgets/Birthdays.vue')),
};
