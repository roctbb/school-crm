<template>
    <div class="object-details-page">
        <h1>Детали объекта</h1>
        <div v-if="object">
            <p><b>Название:</b> {{ object.name }}</p>
            <p><b>Тип:</b> {{ object.type }}</p>
            <p><b>Описание:</b> {{ object.attributes?.description || "Нет описания" }}</p>
        </div>
        <p v-else>Загрузка...</p>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import {fetchObjectDetails} from "@/api/objects.js";

export default {
    data() {
        return {
            object: null,
        };
    },
    created() {
        const {object_type, object_id} = this.$route.params;
        const token = useMainStore().token; // Получаем токен
        fetchObjectDetails(object_type, object_id, token)
            .then(object => {
                this.object = object;
            })
            .catch(error => console.error("Ошибка загрузки деталей объекта:", error));
    }

};
</script>

<style>
.object-details-page {
    padding: 20px;
}
</style>