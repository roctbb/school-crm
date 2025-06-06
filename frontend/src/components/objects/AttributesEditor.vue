<template>
    <div>
        <div
            v-for="attribute in availableAttributes"
            :key="attribute.code"
            class="mb-3"
        >
            <div v-if="canEditAttribute(attribute) || hasTeacherAccess()">
                <label :for="attribute.code" class="form-label">
                    {{ attribute.name }}
                </label>

                <!-- string -->
                <input
                    v-if="attribute.type === 'string' || attribute.type === 'link'"
                    :id="attribute.code"
                    v-model="localAttributes[attribute.code]"
                    type="text"
                    class="form-control"
                    :placeholder="`Введите ${attribute.name}`"
                    :required="attribute.required"
                />

                <!-- text -->
                <textarea
                    v-else-if="attribute.type === 'text'"
                    :id="attribute.code"
                    v-model="localAttributes[attribute.code]"
                    class="form-control"
                    :placeholder="`Введите ${attribute.name}`"
                    :required="attribute.required"
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
                    :required="attribute.required"
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
                    :required="attribute.required"
                />


                <FileUploadField
                    v-if="attribute.type === 'file'"
                    v-model="localAttributes[attribute.code]"
                    :required="attribute.required"
                />


                <!-- select -->
                <select
                    v-else-if="attribute.type === 'select'"
                    :id="attribute.code"
                    class="form-select"
                    v-model="localAttributes[attribute.code]"
                    :required="attribute.required"
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
                            :required="attribute.required && !(localAttributes[attribute.code] || []).length"
                        />
                        <label
                            class="form-check-label"
                            :for="attribute.code + '_' + option"
                        >
                            {{ option }}
                        </label>
                    </div>
                </div>

                <!-- блок с описанием поля -->
                <div v-if="attribute.description" class="form-text">
                    {{ attribute.description }}
                </div>
            </div>


        </div>
    </div>
</template>


<script>
import {uploadFile} from "@/api/files_api.js";
import {API_URL} from "@/api/common.js";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import {hasTeacherAccess} from "@/utils/access.js";
import FileUploadField from "@/components/common/FileUploadField.vue"; // Стили для Vue3

export default {
    name: "AttributesEditor",
    components: {
        FileUploadField,
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
            localAttributes: {...this.attributes},
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
        hasTeacherAccess,
        canEditAttribute(attribute) {
            return !attribute.is_hidden && !attribute.is_locked;
        }
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