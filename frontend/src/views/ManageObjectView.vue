<template>
    <BaseLayout>
        <div v-if="object">
            <h3 class="my-3">{{ capitalize(object_type.name) }}:
                {{ isEditMode ? object.name : "добавление записи" }}</h3>

            <form @submit.prevent="handleSave">
                <div class="mb-3">
                    <label class="form-label">Имя</label>
                    <input
                        v-model="object.name"
                        type="text"
                        class="form-control"
                        placeholder="Введите название"
                        required
                    />
                </div>
                <div class="mb-3">
                    <label class="form-label">Параметры объекта (JSON)</label>
                    <textarea
                        v-model="object.params"
                        class="form-control"
                        placeholder='{ "ключ": "значение" }'
                    ></textarea>
                </div>
                <div class="mb-3">
                    <AttributesEditor v-model:attributes="object.attributes"
                                      :available-attributes="object_type.available_attributes"/>
                </div>


                <button type="submit" class="btn btn-success">
                    Сохранить
                </button>
                <button
                    type="button"
                    class="btn btn-secondary ms-2"
                    @click="resetChanges"
                >
                    Назад
                </button>
            </form>
        </div>
        <Loading v-else/>
    </BaseLayout>
</template>

<script>
import useMainStore from "@/stores/mainStore"; // Pinia стейт
import CrmObject from "@/models/CrmObject.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import {capitalize} from "@/utils/helpers.js";
import Loading from "@/components/common/Loading.vue";
import AttributesEditor from "@/components/objects/AttributesEditor.vue";

export default {
    components: {AttributesEditor: AttributesEditor, Loading, BaseLayout},
    props: {
        objectId: {
            type: Number,
            default: null,
        },
        objectTypeCode: {
            type: String,
            required: true,
        },
    },
    computed: {
        isEditMode() {
            return !!this.objectId; // Редактирование, если есть `objectId`
        }
    },
    data() {
        return {
            store: useMainStore(),
            object: null,
            object_type: null,
            error: null,
        }
    },
    async created() {
        if (!this.store.objectTypes.length) {
            await this.store.fetchObjectTypes();
            await this.store.fetchObjects();
        }

        this.object_type = this.store.objectTypes.find(type => type.code === this.objectTypeCode);

        if (this.isEditMode) {
            this.object = this.store.objects[this.objectTypeCode]?.find(obj => obj.id === parseInt(this.objectId));
        } else {
            this.object = new CrmObject({'type': this.objectTypeCode});
        }
    },
    methods: {
        capitalize,
        // Сохранение объекта (создание или редактирование)
        async handleSave() {
            try {
                console.log("saving object", this.object)
                this.error = null;
                this.object = await this.object.save()
                if (!this.isEditMode)
                    this.store.objects[this.object.type].push(this.object);
            } catch (error) {
                console.error("Ошибка сохранения объекта:", error);
                this.error = error.message || "Ошибка при сохранении объекта.";
            }
            this.$router.back();
        },

        resetChanges() {
            if (this.isEditMode) {
                this.object.reset();
            }
            this.$router.back();
        },
    }
};
</script>

<style scoped>
.container {
    margin-top: 20px;
}
</style>