<template>
    <BaseLayout>
        <div v-if="object">
            <div class="page-header">
                <div>
                    <h2>{{ isEditMode ? object.name : `Новая запись: ${capitalize(object_type.name)}` }}</h2>
                    <p>{{ isEditMode ? `Редактирование записи типа «${object_type.name}»` : 'Заполните основные данные и связи.' }}</p>
                </div>
            </div>

            <div v-if="error" class="alert alert-danger">{{ error }}</div>

            <div
                v-if="object_type.params.edit_description"
                v-html="object_type.params.edit_description"
                class="alert alert-warning"
            ></div>

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

                <div v-if="hasAdminAccess()" class="visibility-settings mb-4">
                    <div class="form-check mb-1">
                        <input id="object-is-hidden" v-model="object.is_hidden" class="form-check-input" type="checkbox" aria-describedby="visibility-help" />
                        <label class="form-check-label fw-semibold" for="object-is-hidden">Скрыть запись</label>
                    </div>
                    <p id="visibility-help" class="small text-muted mb-0">Запись будет доступна администратору при включённом фильтре «Показывать скрытые». Скрытые ученики не показываются на экране дней рождения.</p>
                </div>

                <!-- Редактор атрибутов -->
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
                            :group="group"
                            :children="object.children"
                            @update-children="updateGroupChildren"
                        />
                    </div>
                </div>

                <div class="editor-save-bar">
                    <button type="button" class="btn btn-light" @click="resetChanges">
                        Назад
                    </button>
                    <div class="d-flex align-items-center gap-3">
                        <span v-if="hasUnsavedChanges" class="small text-warning-emphasis d-none d-sm-inline">
                            Есть несохранённые изменения
                        </span>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save me-1"></i> Сохранить
                        </button>
                    </div>
                </div>
            </form>
        </div>
        <div v-else-if="notFound" class="alert alert-secondary">Запись не найдена или недоступна.</div>
        <Loading v-else/>
    </BaseLayout>
</template>

<script>
// Подключаем нужные объекты
import {hasAdminAccess} from "@/utils/access.js";
import useMainStore from "@/stores/mainStore.js";
import CrmObject from "@/models/CrmObject.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import {capitalize} from "@/utils/helpers.js";
import Loading from "@/components/common/Loading.vue";
import AttributesEditor from "@/components/objects/AttributesEditor.vue";
import ChildrenFilterEditor from "@/components/objects/ChildrenFilterEditor.vue";
import unsavedChangesMixin from "@/mixins/unsavedChangesMixin.js";

export default {
    mixins: [unsavedChangesMixin],
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
            return !!this.objectId; // Режим редактирования, если задан objectId
        },
        hasUnsavedChanges() {
            return Boolean(this.object && this.initialSnapshot && this.objectSnapshot() !== this.initialSnapshot);
        },
    },
    data() {
        return {
            store: useMainStore(),
            object: null,
            notFound: false,
            object_type: null,
            error: null,
            childrenOptions: [], // Группированные варианты детей по типам
            initialSnapshot: "",
        };
    },
    async created() {
        // Подгружаем типы и объекты, если их ещё нет
        if (!this.store.objectTypes.length) {
            await this.store.loadObjects();
        }

        // Устанавливаем тип объекта
        this.object_type = this.store.getObjectTypeByCode(this.objectTypeCode);

        // Устанавливаем сам объект (редактирование или новый экземпляр)
        if (this.isEditMode) {
            const storedObject = this.store.objects[this.objectTypeCode]?.find(
                (obj) => obj.id === parseInt(this.objectId)
            );
            this.object = storedObject ? new CrmObject(JSON.parse(JSON.stringify({
                ...storedObject._present(), children: storedObject.children,
            })), this.store) : null;
        } else {
            this.object = new CrmObject({type: this.objectTypeCode}, this.store);
        }

        // Подготавливаем список групп возможных детей
        if (this.object_type?.params?.possible_children?.length) {
            const possibleChildrenCodes = this.object_type.params?.possible_children;
            // Можно сгруппировать по коду или создавать объекты с дополнительными параметрами
            this.childrenOptions = possibleChildrenCodes.map((code) =>
                this.store.getObjectTypeByCode(code)
            ).filter(Boolean);
        }
        this.initialSnapshot = this.objectSnapshot();
        this.notFound = !this.object;
    },
    methods: {
        capitalize,
        hasAdminAccess,
        objectSnapshot() {
            return JSON.stringify({
                name: this.object?.name || "",
                is_hidden: Boolean(this.object?.is_hidden),
                attributes: this.object?.attributes || {},
                children: this.object?.children || [],
            });
        },
        // При обновлении детей для конкретной группы
        updateGroupChildren({groupCode, childrenItems}) {
            // Удаляем из объекта всех детей данной группы
            this.object.children = this.object.children.filter(
                (ch) => ch.type !== groupCode
            );
            // Добавляем обновлённый список
            this.object.children.push(...childrenItems);
        },

        async handleSave() {
            try {
                this.error = null;

                // Сохраняем объект
                await this.object.save();

                if (!this.isEditMode) {
                    this.store.objects[this.object.type].push(this.object);
                } else {
                    const objects = this.store.objects[this.object.type];
                    const index = objects.findIndex(item => item.id === this.object.id);
                    if (index >= 0) objects.splice(index, 1, this.object);
                }

                this.initialSnapshot = this.objectSnapshot();
                this.$router.back();
            } catch (error) {
                console.error("Ошибка сохранения объекта:", error);
                this.error =
                    error.message || "Ошибка при сохранении объекта.";
            }
        },

        // Сброс изменений/возврат
        resetChanges() {
            // Можно либо просто вернуться назад, либо восстановить исходные данные
            this.$router.back();
        },
    },
};
</script>

<style scoped>
.visibility-settings {
    padding: 1rem 1.1rem;
    border: 1px solid var(--silaeder-border);
    border-radius: 0.75rem;
    background: var(--silaeder-primary-soft);
}
.visibility-settings p { max-width: 48rem; padding-left: 1.5rem; }
</style>
