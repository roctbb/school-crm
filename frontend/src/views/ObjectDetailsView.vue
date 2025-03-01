<template>
    <BaseLayout>
        <div class="object-details-page" v-if="object">
            <h1>{{ capitalize(this.object_type.name) }}: {{ this.object.name }}</h1>

            <div>
                <p v-for="attribute in object_type.available_attributes.filter(attr => attr.display)">
                    <b>{{ attribute.name }}:</b> {{ object.attributes[attribute.code] }}</p>
            </div>

            <!-- Кнопки действий -->
            <div class="mt-3 d-flex gap-2">
                <!-- Кнопка Редактировать -->
                <router-link
                    :to="`/${object_type.code}/${object.id}/edit`"
                    class="btn btn-warning btn-sm"
                >
                    Редактировать
                </router-link>

                <button
                    class="btn btn-danger btn-sm"
                    @click="handleDelete"
                >
                    Удалить
                </button>

                <button
                    class="btn btn-secondary btn-sm"
                    @click="$router.push(`/${object_type.code}`)"
                >
                    Назад
                </button>
            </div>
        </div>
        <Loading v-else/>
    </BaseLayout>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import {deleteObject} from "@/api/objects.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import {capitalize} from "../utils/helpers.js";

export default {
    methods: {
        capitalize,
        async handleDelete() {
            await deleteObject(this.object.id);
            this.store.objects[this.object.type] = this.store.objects[this.object.type].filter(obj => obj.id !== this.object.id);
            this.$router.push(`/${this.object.type}`);
        }
    },
    components: {Loading, BaseLayout},
    data() {
        return {
            object: null,
            object_type: null,
            store: useMainStore()
        };
    },
    async created() {
        let {object_type, object_id} = this.$route.params;
        object_id = parseInt(object_id);
        await this.store.loadObjects();
        this.object_type = this.store.objectTypes.find(type => type.code === object_type);
        this.object = this.store.objects[object_type].find(obj => obj.id === object_id);
    }

};
</script>

<style>
.object-details-page {
    padding: 20px;
}
</style>