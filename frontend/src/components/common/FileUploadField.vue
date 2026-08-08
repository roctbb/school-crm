<template>
    <div class="file-upload">
        <input
            type="file"
            :id="id"
            class="form-control"
            :required="required && fileUrls.length === 0"
            @change="onFileChange"
        />

        <div v-if="historyEnabled && fileUrls.length" class="form-check mt-2">
            <input
                :id="`${id || 'file'}-append-history`"
                v-model="appendToHistory"
                class="form-check-input"
                type="checkbox"
            />
            <label :for="`${id || 'file'}-append-history`" class="form-check-label">
                Добавить к истории вместо замены
            </label>
        </div>

        <!-- Если URL к файлу уже есть (и ничего не загружается) -->
        <div v-if="currentFileUrl && !isUploading" class="mt-2">
            <a
                :href="currentFileUrl"
                @click.prevent="handleOpenFile(currentFileUrl)"
                rel="noopener noreferrer"
                class="text-primary"
            >
                Открыть текущий файл
            </a>

            <details v-if="historyEnabled && fileUrls.length > 1" class="mt-1">
                <summary class="small text-muted">Предыдущие файлы: {{ fileUrls.length - 1 }}</summary>
                <div v-for="(url, index) in previousFileUrls" :key="url" class="small">
                    <a :href="url" @click.prevent="handleOpenFile(url)">Версия {{ index + 1 }}</a>
                </div>
            </details>
        </div>

        <!-- Показать индикатор процесса загрузки -->
        <div v-else-if="isUploading" class="text-muted mt-2">
            Загружается...
        </div>
    </div>
</template>

<script>
import {latestFileUrl, normalizeFileUrls, openFile, uploadFile} from "@/api/files_api.js";

export default {
    name: "FileUploadField",
    props: {
        /* v-model со значением URL или Base64 (проще всего),
           куда будет сохраняться загруженный файл */
        modelValue: {
            type: [String, Array],
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
        historyEnabled: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            isUploading: false,
            appendToHistory: false,
        };
    },
    computed: {
        fileUrls() {
            return normalizeFileUrls(this.modelValue);
        },
        currentFileUrl() {
            return latestFileUrl(this.modelValue);
        },
        previousFileUrls() {
            return this.fileUrls.slice(0, -1).reverse();
        },
    },
    methods: {
        async handleOpenFile(url) {
            await openFile(url);
        },
        async onFileChange(e) {
            const file = e.target.files[0];
            if (!file) return;

            this.isUploading = true;
            try {
                const path = await uploadFile(file);
                this.isUploading = false;
                const nextValue = this.historyEnabled
                    ? (this.appendToHistory ? [...this.fileUrls, path] : [path])
                    : path;
                this.$emit("update:modelValue", nextValue);
            } catch (error) {
                console.error("Ошибка загрузки файла", error);
                this.isUploading = false;
            }
        },
    },
};
</script>
