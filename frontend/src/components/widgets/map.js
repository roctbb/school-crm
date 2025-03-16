import {defineAsyncComponent} from 'vue';

export const availableWidgets = {
    active_events: defineAsyncComponent(() => import('@/components/widgets/ActiveEventsWidget.vue')),
};
