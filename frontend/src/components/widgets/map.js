import {defineAsyncComponent} from 'vue';

export const availableWidgets = {
    active_events: defineAsyncComponent(() => import('@/components/widgets/ActiveEventsWidget.vue')),
    birthdays: defineAsyncComponent(() => import('@/components/widgets/Birthdays.vue')),
    calendar: defineAsyncComponent(() => import('@/components/widgets/Calendar.vue')),
    portfolio_progress: defineAsyncComponent(() => import('@/components/widgets/PortfolioGamificationWidget.vue'))
};
