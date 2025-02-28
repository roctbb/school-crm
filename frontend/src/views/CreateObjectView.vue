<template>
    <div class="create-object-page">
        <h1>Создать новый объект</h1>
        <form @submit.prevent="submitForm">
            <div class="form-group">
                <label for="name">Название:</label>
                <input v-model="form.name" id="name" type="text" required/>
            </div>

            <div class="form-group">
                <label for="type">Тип:</label>
                <select v-model="form.type" id="type" required>
                    <option v-for="type in objectTypes" :key="type.code" :value="type.code">
                        {{ type.name }}
                    </option>
                </select>
            </div>

            <button type="submit" class="btn btn-success">Создать</button>
        </form>
    </div>
</template>

<script>
import {fetchObjectTypes, createObject} from "@/api/objects";
import useMainStore from "@/stores/mainStore";

export default {
    data() {
        return {
            form: {name: "", type: ""},
            objectTypes: [],
        };
    },
    async created() {
        try {
            const mainStore = useMainStore();
            const token = mainStore.token;
            this.objectTypes = await fetchObjectTypes(token); // Загружаем типы объектов
        } catch (error) {
            console.error("Ошибка при загрузке типов объектов:", error);
        }
    },
    methods: {
        async submitForm() {
            try {
                const token = useMainStore().token; // Получаем токен
                const newObject = await createNewObject(this.form, this.form.type, token);
                console.log("Объект создан:", newObject);
                this.$router.push(`/objects/${this.form.type}/${newObject.id}`);
            } catch (error) {
                console.error("Ошибка при создании объекта:", error);
            }
        },
    }

};
</script>

<style>
.create-object-page {
    padding: 20px;
}
</style>