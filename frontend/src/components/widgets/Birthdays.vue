<script>
import useMainStore from "@/stores/mainStore.js";
import {parseDate} from "@/utils/helpers.js";

export default {
    name: "BirthdaysWidget",
    data() {
        return {
            store: useMainStore(),
        }
    },
    computed: {
        birthdaysToday() {
            const today = new Date();
            const currentDay = today.getDate();
            const currentMonth = today.getMonth();

            return this.store.getObjectsByType('students').filter(student => {
                const birthdayDate = parseDate(student.attributes.birthday);
                return (
                    birthdayDate &&
                    birthdayDate.getDate() === currentDay &&
                    birthdayDate.getMonth() === currentMonth
                );
            });
        },
    }
}
</script>

<template>
    <section v-if="birthdaysToday.length > 0" class="birthdays-widget surface-card my-3">
        <div class="birthdays-icon" aria-hidden="true">
            <i class="bi bi-gift"></i>
        </div>
        <div>
            <h5 class="mb-2">Сегодня день рождения!</h5>
            <div class="d-flex flex-wrap gap-1">
                <span
                    class="badge bg-success text-white"
                    v-for="student in birthdaysToday"
                    :key="student.id"
                >
                    <router-link :to="'/students/' + student.id" class="text-decoration-none text-reset">
                        {{ student.name }}
                    </router-link>
                </span>
            </div>
        </div>
    </section>
</template>

<style scoped>
.birthdays-widget {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem 1.1rem;
}

.birthdays-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    width: 2.25rem;
    height: 2.25rem;
    color: var(--silaeder-primary-dark);
    border-radius: 50%;
    background: var(--silaeder-primary-soft);
}
</style>
