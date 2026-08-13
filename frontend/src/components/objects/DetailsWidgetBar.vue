<script>

import {availableWidgets} from "@/components/widgets/map.js";

export default {
    name: "DetailsWidgetBar",
    props: {
        object: Object,
        type: Object,
        embedded: {
            type: Boolean,
            default: false,
        },
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
    <div
        v-if="widgets.length"
        class="details-widget-stack"
        :class="{ 'details-widget-stack--embedded': embedded }"
    >
        <component
            v-for="(widget, index) in widgets"
            :key="index"
            :is="widget"
            :class="{ 'embedded-detail-widget': embedded }"
            :object="object"
            :type="type"
        />
    </div>
</template>

<style scoped>
.details-widget-stack {
    display: grid;
    gap: var(--silaeder-section-gap);
}

.details-widget-stack--embedded {
    gap: 0;
}

.details-widget-stack--embedded :deep(.embedded-detail-widget) {
    margin: 0;
    border: 0;
    border-radius: 0;
    box-shadow: none;
}

.details-widget-stack--embedded :deep(.embedded-detail-widget .card-body) {
    padding-top: 0.5rem !important;
}

</style>
