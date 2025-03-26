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
                class="mb-5 p-3 border border-light rounded"
            >
                <h5 class="fw-bold d-flex align-items-center pb-2 border-bottom">
                    <!-- Заголовок группы -->
                    <span class="me-2">
                      {{ groupingAttribute?.name }}: {{ group }}
                    </span>
                    <!-- Число объектов в группе -->
                    <span
                        class="badge bg-secondary rounded-pill py-1 px-2"
                        style="font-size: 0.75rem;"
                    >
                      {{ objects.length }}
                    </span>
                </h5>

                <div class="row mt-3">
                    <div
                        v-for="object in objects"
                        :key="object.id"
                        class="mb-4 d-flex align-items-stretch"
                        :class="{
                          'col-md-3 col-lg-3 col-xl-2': size === 'big',
                          'col-md-6 col-lg-4 col-xl-3 col-xl-2': size !== 'big'
                        }"
                    >
                        <ObjectCard :object="object"/>
                    </div>
                </div>
            </div>
        </div>

        <!-- Если нет групп, но есть объекты -->
        <div v-else-if="objects.length" class="row">
            <div
                v-for="object in objects"
                :key="object.id"
                class="mb-4 px-2 d-flex align-items-stretch"
                :class="{
                  'col-md-3 col-lg-3 col-xl-2': size === 'big',
                  'col-md-6 col-lg-4 col-xl-3 col-xl-2': size !== 'big'
                }"
            >
                <ObjectCard :object="object"/>
            </div>
        </div>

        <!-- Если вообще нет объектов -->
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
        objects: {
            type: Array,
            required: true
        },
        groupedData: {
            type: Object,
            default: null
        },
        groupingAttribute: {
            type: Object,
            default: null
        },
        size: {
            type: String,
            default: "medium"
        }
    }
};
</script>

<style scoped>
/* Стиль для всей секции */
.mb-5 {
    margin-bottom: 3rem !important;
}

.border-bottom {
    border-bottom: 2px solid #dee2e6 !important;
}
</style>