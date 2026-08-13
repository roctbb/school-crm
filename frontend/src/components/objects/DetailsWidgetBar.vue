<script>

import {availableWidgets} from "@/components/widgets/map.js";

export default {
    name: "DetailsWidgetBar",
    props: {
        object: Object,
        type: Object,
    },
    computed: {
        widgets() {
            if (!this.type?.params.details_widgets) return []
            return this.type?.params.details_widgets
                .map(key => availableWidgets[key])
                .filter(Boolean);

        }
    }
}
</script>

<template>
    <div v-if="widgets.length" class="details-widget-stack">
        <component
            v-for="(widget, index) in widgets"
            :key="index"
            :is="widget"
            :object="object"
            :type="type"
        />
    </div>
</template>

<style scoped>

</style>
