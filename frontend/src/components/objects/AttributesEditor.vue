<template>
    <div>
        <div
            v-for="attribute in availableAttributes"
            :key="attribute.code"
            class="mb-3"
        >
            <label :for="attribute.code" class="form-label">
                {{ attribute.name }}
            </label>

            <!-- string -->
            <input
                v-if="attribute.type === 'string'"
                :id="attribute.code"
                v-model="localAttributes[attribute.code]"
                type="text"
                class="form-control"
                :placeholder="`Введите ${attribute.name}`"
            />

            <!-- text -->
            <textarea
                v-else-if="attribute.type === 'text'"
                :id="attribute.code"
                v-model="localAttributes[attribute.code]"
                class="form-control"
                :placeholder="`Введите ${attribute.name}`"
                rows="3"
            ></textarea>

            <!-- number -->
            <input
                v-else-if="attribute.type === 'number'"
                :id="attribute.code"
                v-model.number="localAttributes[attribute.code]"
                type="number"
                class="form-control"
                :placeholder="`Введите ${attribute.name}`"
            />

            <!-- date -->
            <VueDatePicker
                v-else-if="attribute.type === 'date'"
                v-model="localAttributes[attribute.code]"
                :enable-time-picker="false"
                :text-input="true"
                :model-type="'format'"
                :auto-apply="true"
                :input-class="'form-control'"
                locale="ru"
                :format="'dd.MM.yyyy'"
            />

            <!-- file -->
            <div v-else-if="attribute.type === 'file'" class="file-upload">
                <input
                    type="file"
                    :id="attribute.code"
                    @change="handleFileUpload($event, attribute.code)"
                    class="form-control"
                />
                <div v-if="localAttributes[attribute.code] && !isUploading" class="mt-2">
                    <a
                        :href="localAttributes[attribute.code]"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="text-primary"
                    >
                        Открыть файл
                    </a>
                </div>
                <div v-else-if="isUploading" class="text-muted mt-2">
                    Загружается...
                </div>
            </div>

            <!-- select -->
            <select
                v-else-if="attribute.type === 'select'"
                :id="attribute.code"
                class="form-select"
                v-model="localAttributes[attribute.code]"
            >
                <option
                    v-for="option in attribute.options || []"
                    :key="option"
                    :value="option"
                >
                    {{ option }}
                </option>
            </select>

            <!-- checkboxes -->
            <div
                v-else-if="attribute.type === 'checkboxes'"
                class="form-check"
            >
                <div
                    v-for="option in attribute.options || []"
                    :key="option"
                    class="form-check mb-1"
                >
                    <input
                        class="form-check-input"
                        type="checkbox"
                        :id="attribute.code + '_' + option"
                        :value="option"
                        v-model="localAttributes[attribute.code]"
                    />
                    <label
                        class="form-check-label"
                        :for="attribute.code + '_' + option"
                    >
                        {{ option }}
                    </label>
                </div>
            </div>

            <!-- неизвестный тип -->
            <div v-else class="form-text text-muted">
                Неизвестный тип: <strong>{{ attribute.type }}</strong>
            </div>
        </div>
    </div>
</template>

<script>
import { uploadFile } from "@/api/files_api.js";
import { API_URL } from "@/api/common.js";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css"; // Стили для Vue3

export default {
    name: "AttributesEditor",
    components: {
        VueDatePicker,
    },
    props: {
        attributes: {
            type: Object,
            default: () => ({}),
        },
        availableAttributes: {
            type: Array,
            default: () => [],
        },
    },
    emits: ["update:attributes"],
    data() {
        return {
            localAttributes: { ...this.attributes },
            isUploading: false,
        };
    },
    created() {
        for (let attribute of this.availableAttributes) {
            if (attribute.type === 'checkboxes' && !this.localAttributes[attribute.code]) {
                this.localAttributes[attribute.code] = [];
            }
        }
    },
    methods: {
        async handleFileUpload(event, code) {
            const file = event.target.files[0];
            if (!file) return;

            this.isUploading = true;
            try {
                const path = await uploadFile(file);
                this.localAttributes[code] = API_URL + path;
            } catch (err) {
                console.error("Ошибка при загрузке файла:", err);
            } finally {
                this.isUploading = false;
            }
        },
    },
    watch: {
        localAttributes: {
            handler(newAttributes) {
                this.$emit("update:attributes", newAttributes);
            },
            deep: true
        }
    }
};
</script>

<style scoped>
.file-upload input[type="file"] {
    cursor: pointer;
}
.file-upload a {
    text-decoration: underline;
}
</style>