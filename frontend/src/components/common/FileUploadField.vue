<template>
    <div class="file-upload">
        <input
            type="file"
            :id="id"
            class="form-control"
            :required="required"
            @change="onFileChange"
        />

        <!-- Если URL к файлу уже есть (и ничего не загружается) -->
        <div v-if="fileUrl && !isUploading" class="mt-2">
            <a
                :href="fileUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary"
            >
                Открыть файл
            </a>
        </div>

        <!-- Показать индикатор процесса загрузки -->
        <div v-else-if="isUploading" class="text-muted mt-2">
            Загружается...
        </div>
    </div>
</template>

<script>
import {uploadFile} from "@/api/files_api.js";

export default {
    name: "FileUploadField",
    props: {
        /* v-model со значением URL или Base64 (проще всего),
           куда будет сохраняться загруженный файл */
        modelValue: {
            type: String,
            default: "",
        },
        id: {
            type: String,
            default: "",
        },
        required: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            fileUrl: this.modelValue, // текущее значение, которое видит компонент
            isUploading: false,
        };
    },
    watch: {
        // Если извне меняется значение (например, сброс),
        // подхватываем и у себя
        modelValue(newVal) {
            this.fileUrl = newVal;
        },
    },
    methods: {
        async onFileChange(e) {
            const file = e.target.files[0];
            if (!file) return;

            // Пример: эмулируем "загрузку" на сервер
            this.isUploading = true;
            try {
                // Здесь можно сделать реальную отправку на сервер (через formData, axios и т.п.)
                // Либо просто преобразовать в Base64, если нужно хранить в базе
                // Примерно так:
                const path = await uploadFile(file);
                this.isUploading = false;
                this.fileUrl = path
                this.$emit("update:modelValue", path);
            } catch (error) {
                console.error("Ошибка загрузки файла", error);
                this.isUploading = false;
            }
        },
    },
};
</script>