<template>
    <BaseLayout>
        <div v-if="object">
            <h3 class="my-3">{{ capitalize(object_type.name) }}:
                {{ isEditMode ? object.name : "добавление записи" }}</h3>

            <form @submit.prevent="handleSave">
                <!-- Поле для имени -->
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
                    <AttributesEditor
                        v-model:attributes="object.attributes"
                        :available-attributes="object_type.available_attributes"
                    />
                </div>

                <!-- Редакторы для групп детей -->
                <div class="mb-3" v-if="childrenOptions.length">
                    <div
                        v-for="group in childrenOptions"
                        :key="group.code"
                        class="mb-4"
                    >
                        <ChildrenFilterEditor
                            v-model:children="object.children"
                            :group="group"
                        />
                    </div>
                </div>

                <button type="submit" class="btn btn-success">
                    <i class="bi bi-save me-1"></i> Сохранить
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
import useMainStore from "@/stores/mainStore.js"; // Pinia стейт
import CrmObject from "@/models/CrmObject.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import {capitalize} from "@/utils/helpers.js";
import Loading from "@/components/common/Loading.vue";
import AttributesEditor from "@/components/objects/AttributesEditor.vue";
import ChildrenFilterEditor from "@/components/objects/ChildrenFilterEditor.vue";

export default {
    components: {
        ChildrenFilterEditor,
        AttributesEditor,
        Loading,
        BaseLayout,
    },
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
            return !!this.objectId; // Режим редактирования, если указан `objectId`
        },
    },
    data() {
        return {
            store: useMainStore(),
            object: null,
            object_type: null,
            error: null,
            childrenOptions: [], // Группированные дети по типам
        };
    },
    async created() {
        if (!this.store.objectTypes.length) {
            await this.store.loadObjects()
        }

        // Установить тип объекта
        this.object_type = this.store.getObjectTypeByCode(this.objectTypeCode)

        // Установить сам объект
        if (this.isEditMode) {
            this.object = this.store.objects[this.objectTypeCode]?.find(
                (obj) => obj.id === parseInt(this.objectId)
            );
        } else {
            this.object = new CrmObject({type: this.objectTypeCode}, this.store);
        }

        // Формируем группы детей (доступные для каждой категории)
        if (this.object_type.params?.possible_children?.length) {
            const possibleChildrenCodes = this.object_type.params?.possible_children;

            if (possibleChildrenCodes) {
                this.childrenOptions = possibleChildrenCodes.map((type_code) => this.store.getObjectTypeByCode(type_code))
            }
        }
    },
    methods: {
        capitalize,
        async handleSave() {
            try {
                this.error = null;

                // Сохраняем объект
                await this.object.save();

                if (!this.isEditMode) {
                    this.store.objects[this.object.type].push(this.object);
                }

                this.$router.back();
            } catch (error) {
                console.error("Ошибка сохранения объекта:", error);
                this.error =
                    error.message || "Ошибка при сохранении объекта.";
            }
        },

        resetChanges() {
            if (this.isEditMode) {
                this.object.reset();
            }
            this.$router.back();
        },
    },
};
</script>

<style scoped>
.container {
    margin-top: 20px;
}
</style>