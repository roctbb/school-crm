<script>

import {availableWidgets} from "@/components/widgets/map.js";

export default {
    name: "ListWidgetBar",
    props: {
        type: Object,
    },
    computed: {
        widgets() {
            if (!this.type?.params.widgets) return []

            return this.type?.params.widgets
                .map(key => availableWidgets[key])
                .filter(Boolean);

        }
    }
}
</script>

<template>
    <component
        v-for="(widget, index) in widgets"
        :key="index"
        :is="widget"
    />
</template>

<style scoped>

</style>