<template>
    <div>
        <div
            v-if="groupedData && Object.keys(groupedData).length"
            class="mt-3"
        >
            <div
                v-for="(objects, group) in groupedData"
                :key="group"
                class="mb-4"
            >
                <h5 class="fw-bold d-flex align-items-center pb-2 mb-0">
                    <span class="me-2">{{ groupingAttribute?.name }}: {{ group }}</span>
                    <span class="badge bg-secondary rounded-pill py-1 px-2"
                          style="font-size: 0.75rem;">{{ objects.length }}</span>
                </h5>
                <div class="row">
                    <div
                        v-for="object in objects"
                        :key="object.id"
                        class="mb-4 d-flex align-items-stretch me-0"
                        :class="{'col-md-3 col-lg-3 col-xl-2': size === 'big', 'col-md-6 col-lg-4 col-xl-3 col-xl-2': size !== 'big'}"
                    >
                        <ObjectCard
                            :object="object"
                            :type="objectType"
                        />
                    </div>
                </div>
            </div>
        </div>
        <div v-else-if="objects.length" class="row">
            <div
                v-for="object in objects"
                :key="object.id"
                class="mb-4 d-flex align-items-stretch me-0"
                :class="{'col-md-3 col-lg-3 col-xl-2': size === 'big', 'col-md-6 col-lg-4 col-xl-3 col-xl-2': size !== 'big'}"
            >
                <ObjectCard
                    :object="object"
                    :type="objectType"
                />
            </div>
        </div>
        <div v-else>
            <p class="text-center">Объекты отсутствуют для данного типа.</p>
        </div>
    </div>
</template>

<script>
import ObjectCard from "@/components/objects/ObjectCard.vue";

export default {
    name: "CardView",
    components: {ObjectCard},
    props: {
        objects: {type: Array, required: true},
        groupedData: {type: Object, default: null},
        groupingAttribute: {type: Object, default: null},
        objectType: {type: Object, required: true},
        size: {type: String, default: "medium"}
    }
};
</script>