<script>
import useMainStore from "@/stores/mainStore.js";
import {isEventActive, parseDate} from "@/utils/helpers.js";

export default {
    name: "ActiveEventsWidget",
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
    <div v-if="birthdaysToday.length > 0" class="card bg-light my-3 p-3 shadow-sm border-0">
        <div class="card-body">
            <h5 class="card-title d-flex align-items-center">
                <i class="bi bi-gift me-2"></i> Сегодня день рождения!
            </h5>
            <p class="card-text">
        <span
            class="badge bg-success text-white me-1 mb-1"
            v-for="student in birthdaysToday"
            :key="student.id"
        >
          <router-link :to="'/students/' + student.id" class="text-decoration-none text-reset">
            {{ student.name }}
          </router-link>
        </span>
            </p>
        </div>
    </div>

</template>

<style scoped>

</style>