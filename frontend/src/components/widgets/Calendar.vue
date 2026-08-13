<template>
    <section class="calendar-widget surface-card p-3 my-3">
        <!-- Шапка с кнопками переключения месяцев -->
        <div class="row justify-content-center">
            <div class="col-12 calendar-header mb-3">
                <button class="btn btn-outline-secondary btn-sm icon-button" type="button" aria-label="Предыдущий месяц" @click="prevMonth">
                    <i class="bi bi-chevron-left"></i>
                </button>

                <span class="fw-bold text-capitalize">
          {{ monthYearLabel }}
        </span>

                <div class="calendar-header-actions d-flex align-items-center justify-content-end gap-2">
                <button
                    class="btn btn-sm btn-link text-secondary text-decoration-none calendar-toggle"
                    type="button"
                    :aria-expanded="expanded"
                    @click="expanded = !expanded"
                >
                    <i :class="expanded ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" class="me-1"></i>
                    {{ expanded ? 'Свернуть' : 'Показать календарь' }}
                </button>
                <button class="btn btn-outline-secondary btn-sm icon-button" type="button" aria-label="Следующий месяц" @click="nextMonth">
                    <i class="bi bi-chevron-right"></i>
                </button>
                </div>
            </div>
        </div>

        <!-- Таблица календаря -->
        <div v-if="expanded" class="row justify-content-center">
            <div class="col-12 table-responsive">
                <table class="table table-bordered text-center align-middle mb-0">
                    <thead class="table-light">
                    <tr>
                        <th
                            v-for="(day, i) in weekDays"
                            :key="i"
                            scope="col"
                        >
                            {{ day }}
                        </th>
                    </tr>
                    </thead>

                    <tbody>
                    <tr
                        v-for="(week, wIndex) in calendarDays"
                        :key="`week-${wIndex}`"
                    >
                        <td
                            v-for="(dayObj, dayIndex) in week"
                            :key="dayObj.date ? dayObj.date.getTime() : `empty-cell-${wIndex}-${dayIndex}`"
                            style="height: 80px; width: 14%;"
                        >
                            <div
                                v-if="dayObj.date"
                                class="fw-bold"
                            >
                                {{ dayObj.date.getDate() }}
                            </div>
                            <div
                                v-for="ev in dayObj.events"
                                :key="ev.id"
                                class="d-block small text-truncate event-item"
                                @click="goToEvent(ev.id)"
                            >
                                <i class="bi bi-calendar3 me-1"></i>
                                {{ ev.name }}
                            </div>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import { parseDate } from "@/utils/helpers.js";
import { useRouter } from "vue-router";

export default {
    name: "CalendarWidget",

    data() {
        const currentDate = new Date();
        return {
            store: useMainStore(),
            router: useRouter(),
            currentMonth: currentDate.getMonth(),
            currentYear: currentDate.getFullYear(),
            weekDays: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            expanded: false,
        };
    },

    computed: {
        allEvents() {
            return this.store.getObjectsByType("events");
        },
        monthYearLabel() {
            const date = new Date(this.currentYear, this.currentMonth);
            return date.toLocaleString("ru-RU", { month: "long", year: "numeric" });
        },
        calendarDays() {
            const firstDayOfMonth = new Date(this.currentYear, this.currentMonth, 1);
            let dayOfWeek = firstDayOfMonth.getDay();
            // Преобразуем воскресенье в 7-й день
            if (dayOfWeek === 0) {
                dayOfWeek = 7;
            }

            const daysInMonth = new Date(
                this.currentYear,
                this.currentMonth + 1,
                0
            ).getDate();

            const weeks = [];
            let currentWeek = [];

            // Пустые ячейки до первого дня
            for (let i = 1; i < dayOfWeek; i++) {
                currentWeek.push({ date: null, events: [] });
            }

            // Заполнение числами месяца
            for (let day = 1; day <= daysInMonth; day++) {
                const dateObj = new Date(this.currentYear, this.currentMonth, day);
                currentWeek.push({
                    date: dateObj,
                    events: this.filterEventsForDay(dateObj),
                });

                if (currentWeek.length === 7) {
                    weeks.push(currentWeek);
                    currentWeek = [];
                }
            }

            // Хвостовые пустые ячейки
            if (currentWeek.length > 0) {
                while (currentWeek.length < 7) {
                    currentWeek.push({ date: null, events: [] });
                }
                weeks.push(currentWeek);
            }

            return weeks;
        },
    },

    methods: {
        filterEventsForDay(date) {
            if (!date) {
                return [];
            }
            return this.allEvents.filter((ev) => this.isEventOnDate(ev, date));
        },

        isEventOnDate(event, date) {
            const start = event?.attributes?.start;
            const end = event?.attributes?.end;
            if (!start) return false;

            const startDate = parseDate(start);
            let endDate = end ? parseDate(end) : null;

            // Если событие однодневное
            if (!endDate) {
                endDate = new Date(startDate);
            } else {
                // Включаем конец дня
                endDate.setHours(23, 59, 59, 999);
            }

            return date >= startDate && date <= endDate;
        },

        goToEvent(eventId) {
            this.router.push(`/events/${eventId}`);
        },

        nextMonth() {
            if (this.currentMonth === 11) {
                this.currentMonth = 0;
                this.currentYear++;
            } else {
                this.currentMonth++;
            }
        },

        prevMonth() {
            if (this.currentMonth === 0) {
                this.currentMonth = 11;
                this.currentYear--;
            } else {
                this.currentMonth--;
            }
        },
    },
};
</script>

<style scoped>
.calendar-widget {
    overflow: hidden;
    background: var(--silaeder-surface);
}

.calendar-toggle {
    font-size: 0.875rem;
}

.calendar-header {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 0.75rem;
}

.calendar-header > .icon-button:first-child {
    justify-self: start;
}

.calendar-header-actions {
    justify-self: end;
}

@media (max-width: 575.98px) {
    .calendar-header {
        grid-template-columns: auto 1fr auto;
    }

    .calendar-header > .fw-bold {
        text-align: center;
    }

    .calendar-toggle {
        width: 2.75rem;
        min-height: 2.75rem;
        padding: 0;
        overflow: hidden;
        white-space: nowrap;
        text-indent: -999rem;
    }

    .calendar-toggle i {
        margin: 0 !important;
        text-indent: 0;
    }
}

/* Чтобы название события не растягивало ячейку,
   задаём максимальную ширину и обрезаем текст многоточием. */
.event-item {
    display: inline-block;      /* или block/inline-block по вкусу */
    max-width: 100px;           /* подберите нужную ширину */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
}

.fw-bold {
    font-weight: 600; /* Служебный класс Bootstrap, оставлен для наглядности */
}
</style>
