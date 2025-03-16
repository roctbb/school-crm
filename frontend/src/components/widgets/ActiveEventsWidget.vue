<script>
import useMainStore from "@/stores/mainStore.js";
import {isEventActive} from "@/utils/helpers.js";

export default {
    name: "ActiveEventsWidget",
    data() {
        return {
            store: useMainStore(),
        }
    },
    props: {
        object: {
            type: Object,
            required: true
        },
        type: {
            type: Object,
            required: true
        }
    },
    computed: {
        actual_events() {
            return this.store.getObjectsByType('events').filter(event => isEventActive(event, this.object));
        }
    },
    methods: {
        describeEvent(event) {
            if (event.attributes.end) {
                return `${event.name} (${event.attributes.start} - ${event.attributes.end})`
            }
            return event.name;
        }
    }
}
</script>

<template>
    <div class="my-1">
        <span class="badge text-bg-primary" v-for="event in actual_events" :key="event.id">{{ describeEvent(event) }}</span>
    </div>
</template>

<style scoped>

</style>