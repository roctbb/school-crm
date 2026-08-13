<template>
    <div>
        <!-- Если есть сгруппированные данные -->
        <div
            v-if="groupedData && Object.keys(groupedData).length"
            class="mt-3"
        >
            <!-- Цикл по группам -->
            <div
                v-for="(objects, group) in groupedData"
                :key="group"
                class="group-section surface-card mb-3 p-3"
            >
                <h5 class="group-heading fw-bold d-flex align-items-center pb-2 mb-3 border-bottom">
                    <!-- Заголовок группы -->
                    <span class="me-2">
                      {{ groupingAttribute?.name }}: {{ formatGroupingLabel(group, groupingAttribute) }}
                    </span>
                    <!-- Число объектов в группе -->
                    <span
                        class="badge bg-secondary rounded-pill py-1 px-2"
                        style="font-size: 0.75rem;"
                    >
                      {{ groupCounts[group] || objects.length }}
                    </span>
                </h5>

                <div class="row g-3">
                    <div
                        v-for="object in objects"
                        :key="object.id"
                        class="d-flex align-items-stretch"
                        :class="{
                          'col-md-3 col-lg-3 col-xl-2': size === 'big',
                          'col-md-6 col-lg-4 col-xl-3': size !== 'big'
                        }"
                    >
                        <ObjectCard :object="object"/>
                    </div>
                </div>
            </div>
        </div>

        <!-- Если нет групп, но есть объекты -->
        <div v-else-if="objects.length" class="row g-3">
            <div
                v-for="object in objects"
                :key="object.id"
                class="d-flex align-items-stretch"
                :class="{
                  'col-md-3 col-lg-3 col-xl-2': size === 'big',
                  'col-md-6 col-lg-4 col-xl-3': size !== 'big'
                }"
            >
                <ObjectCard :object="object"/>
            </div>
        </div>

        <!-- Если вообще нет объектов -->
        <EmptyState
            v-else
            title="Записей пока нет"
            description="Измените фильтры или создайте первую запись этого типа."
            icon="bi-folder2-open"
        />
    </div>
</template>

<script>
import ObjectCard from "@/components/objects/ObjectCard.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import {groupingLabel} from "@/utils/objectGrouping.js";

export default {
    name: "CardView",
    components: {EmptyState, ObjectCard},
    props: {
        objects: {
            type: Array,
            required: true
        },
        groupedData: {
            type: Object,
            default: null
        },
        groupCounts: {
            type: Object,
            default: () => ({})
        },
        groupingAttribute: {
            type: Object,
            default: null
        },
        size: {
            type: String,
            default: "medium"
        }
    },
    methods: {
        formatGroupingLabel: groupingLabel,
    },
};
</script>

<style scoped>
.group-section {
    min-width: 0;
}

.group-heading {
    border-color: var(--silaeder-border) !important;
}
</style>
