<script>

import {availableWidgets} from "@/components/widgets/map.js";

export default {
    name: "WidgetBar",
    props: {
        object: Object,
        type: Object,
    },
    computed: {
        widgets() {
            if (!this.type.params.widgets) return []
            return this.type.params.widgets
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
        :object="object" :type="type"
    />
</template>

<style scoped>

</style>