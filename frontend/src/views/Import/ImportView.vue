<template>
    <BaseLayout>
        <div class="container py-4">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="m-0">Импорт файла CSV</h3>
                        </div>

                        <div class="card-body">
                            <form @submit.prevent="uploadFile">
                                <!-- Выбор файла -->
                                <div class="mb-3">
                                    <label for="file" class="form-label">Выберите файл</label>
                                    <input
                                        type="file"
                                        id="file"
                                        ref="fileInput"
                                        @change="handleFileChange"
                                        class="form-control"
                                    />
                                </div>

                                <!-- Выбор типа импорта -->
                                <div class="mb-3">
                                    <label for="importType" class="form-label">Что импортировать</label>
                                    <select id="importType" v-model="importType" class="form-select">
                                        <option value="objects">Объекты</option>
                                        <option value="submissions">Записи</option>
                                    </select>
                                </div>

                                <!-- Кнопка отправки -->
                                <button
                                    type="submit"
                                    class="btn btn-primary"
                                    :disabled="isUploading"
                                >
                                    Импортировать
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- Отображение результата -->
                    <div
                        v-if="uploadMessage"
                        class="mt-3"
                    >
                        <div
                            class="alert"
                            :class="isSuccess ? 'alert-success' : 'alert-danger'"
                            role="alert"
                        >
                            {{ uploadMessage }}
                        </div>
                    </div>

                    <!-- Индикатор загрузки -->
                    <Loading v-if="isUploading" class="mt-3"/>
                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import { importObjects, importSubmissions } from "@/api/import_api.js";
import useMainStore from "@/stores/mainStore.js";
import Loading from "@/components/common/Loading.vue";
import BaseLayout from "@/components/layouts/BaseLayout.vue";

export default {
    components: { BaseLayout, Loading },
    name: "ImportView",
    data() {
        return {
            selectedFile: null,
            isUploading: false,
            uploadMessage: "",
            isSuccess: false,
            importType: "objects",
        };
    },
    methods: {
        handleFileChange(event) {
            const files = event.target.files;
            if (files && files.length) {
                this.selectedFile = files[0];
            }
        },
        async uploadFile() {
            if (!this.selectedFile) {
                this.uploadMessage = "Пожалуйста, выберите файл для импорта.";
                this.isSuccess = false;
                return;
            }

            this.isUploading = true;
            this.uploadMessage = "";

            try {
                let result;
                if (this.importType === "objects") {
                    result = await importObjects(this.selectedFile);
                } else {
                    result = await importSubmissions(this.selectedFile);
                }

                this.uploadMessage = "Файл успешно импортирован!";
                this.isSuccess = true;

                const mainStore = useMainStore();
                mainStore.reset();
                await mainStore.loadObjects();

            } catch (error) {
                this.uploadMessage = "Ошибка при импорте файла: " + error.message;
                this.isSuccess = false;
            } finally {
                this.isUploading = false;
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
.container {
    max-width: 720px;
}
.card {
    border-radius: 6px;
}
</style>