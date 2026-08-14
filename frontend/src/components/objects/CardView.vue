<template>
    <div>
        <!-- Если есть сгруппированные данные -->
        <div
            v-if="groupedData && Object.keys(groupedData).length"
            class="mt-3"
        >
            <!-- Цикл по группам -->
            <div
                v-for="(groupData, group) in groupedData"
                :key="group"
                class="group-section mb-4"
            >
                <h5 class="group-heading fw-bold d-flex align-items-center mb-3">
                    <!-- Заголовок группы -->
                    <span class="me-2">
                      {{ primaryGroupingAttribute?.name }}: {{ formatGroupingLabel(group, primaryGroupingAttribute) }}
                    </span>
                    <!-- Число объектов в группе -->
                    <span
                        class="badge bg-secondary rounded-pill py-1 px-2"
                        style="font-size: 0.75rem;"
                    >
                      {{ groupCount([group]) || groupObjectCount(groupData) }}
                    </span>
                </h5>

                <template v-if="secondaryGroupingAttribute">
                    <div
                        v-for="(objects, secondaryGroup) in groupData"
                        :key="`${group}-${secondaryGroup}`"
                        class="subgroup-section"
                    >
                        <h6 class="subgroup-heading d-flex align-items-center gap-2 mb-3">
                            <span>
                                {{ secondaryGroupingAttribute.name }}:
                                {{ formatGroupingLabel(secondaryGroup, secondaryGroupingAttribute) }}
                            </span>
                            <span class="badge text-bg-light rounded-pill">
                                {{ groupCount([group, secondaryGroup]) || objects.length }}
                            </span>
                        </h6>
                        <div class="object-card-grid">
                            <div
                                v-for="object in objects"
                                :key="object.id"
                                class="d-flex align-items-stretch"
                            >
                                <ObjectCard :object="object"/>
                            </div>
                        </div>
                    </div>
                </template>

                <div v-else class="object-card-grid">
                    <div
                        v-for="object in groupData"
                        :key="object.id"
                        class="d-flex align-items-stretch"
                    >
                        <ObjectCard :object="object"/>
                    </div>
                </div>
            </div>
        </div>

        <!-- Если нет групп, но есть объекты -->
        <div v-else-if="objects.length" class="object-card-grid">
            <div
                v-for="object in objects"
                :key="object.id"
                class="d-flex align-items-stretch"
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
        groupingAttributes: {
            type: Array,
            default: () => []
        },
        size: {
            type: String,
            default: "medium"
        }
    },
    computed: {
        primaryGroupingAttribute() {
            return this.groupingAttributes[0] || null;
        },
        secondaryGroupingAttribute() {
            return this.groupingAttributes[1] || null;
        },
    },
    methods: {
        formatGroupingLabel: groupingLabel,
        groupCount(groups) {
            return this.groupCounts[JSON.stringify(groups)] || 0;
        },
        groupObjectCount(groupData) {
            if (Array.isArray(groupData)) return groupData.length;
            return Object.values(groupData).reduce((count, objects) => count + objects.length, 0);
        },
    },
};
</script>

<style scoped>
.group-section {
    min-width: 0;
}

.subgroup-section {
    min-width: 0;
    margin: 0 0 1.5rem 0.85rem;
    padding-left: 1rem;
    border-left: 3px solid var(--silaeder-primary-soft);
}

.subgroup-heading {
    color: var(--silaeder-text);
    font-weight: 600;
}

.object-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(13.25rem, 1fr));
    gap: 1rem;
}

@media (max-width: 575.98px) {
    .object-card-grid {
        grid-template-columns: minmax(0, 1fr);
    }
}

</style>
