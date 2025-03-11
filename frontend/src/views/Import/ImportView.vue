<template>
    <BaseLayout>
        <div class="import-container">
            <h2>Импорт файла CSV</h2>
            <form @submit.prevent="uploadFile" class="import-form">
                <div>
                    <label for="file">Выберите файл:</label>
                    <input type="file" id="file" ref="fileInput" @change="handleFileChange"/>
                </div>
                <button type="submit" class="btn btn-primary" :disabled="isUploading">Импортировать</button>
            </form>
            <div v-if="uploadMessage" class="upload-message" :class="{ success: isSuccess, error: !isSuccess }">
                {{ uploadMessage }}
            </div>
            <Loading v-if="isUploading"/>
        </div>
    </BaseLayout>
</template>

<script>
import {importFile} from "@/api/import_api.js";
import useMainStore from "@/stores/mainStore.js";
import Loading from "@/components/common/Loading.vue";
import BaseLayout from "@/components/layouts/BaseLayout.vue"; // Импорт функции API

export default {
    components: {BaseLayout, Loading},
    name: "ImportView",
    data() {
        return {
            selectedFile: null, // Для хранения выбранного файла
            isUploading: false, // Флаг состояния загрузки
            uploadMessage: "", // Сообщение о результате загрузки
            isSuccess: false // Успешно ли выполнение
        };
    },
    methods: {
        // Обработка изменения файла
        handleFileChange(event) {
            const files = event.target.files;
            if (files && files.length) {
                this.selectedFile = files[0];
            }
        },
        // Загрузка файла на сервер
        async uploadFile() {
            // Проверяем, выбран ли файл
            if (!this.selectedFile) {
                this.uploadMessage = "Пожалуйста, выберите файл для импорта.";
                this.isSuccess = false;
                return;
            }

            this.isUploading = true;
            this.uploadMessage = "";

            try {
                // Вызываем API для импорта файла
                const result = await importFile(this.selectedFile);

                // Обрабатываем успешный ответ
                this.uploadMessage = "Файл успешно импортирован!";
                this.isSuccess = true;
                useMainStore().reset()
                await useMainStore().loadObjects()
            } catch (error) {
                // Обрабатываем ошибку
                this.uploadMessage = "Ошибка при импорте файла: " + error.message;
                this.isSuccess = false;
            } finally {
                this.isUploading = false;
                // Сбрасываем состояние формы
                if (this.$refs.fileInput) {
                    this.$refs.fileInput.value = null;
                }
                this.selectedFile = null;
            }
        }
    }
};
</script>

<style scoped>
.import-container {
    padding: 20px;
}

.import-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.import-form label {
    font-weight: bold;
}

.upload-message {
    margin-top: 20px;
    font-weight: bold;
}

.upload-message.success {
    color: green;
}

.upload-message.error {
    color: red;
}
</style>