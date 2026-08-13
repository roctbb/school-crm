<template>
    <div>
        <draggable
            v-model="fields"
            tag="div"
            :item-key="fieldKey"
            ghost-class="drag-ghost"
            handle=".drag-handle"
        >
            <template #item="{element: field, index}">
                <div class="border rounded p-3 mb-3 field-card">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="drag-handle mb-0">
                            <i class="bi bi-grip-vertical text-muted"></i> Поле {{ index + 1 }}
                        </h6>
                        <div class="d-flex gap-1">
                            <button
                                class="btn btn-outline-secondary btn-sm"
                                type="button"
                                :disabled="index === 0"
                                title="Поднять"
                                @click="moveField(index, -1)"
                            >
                                <i class="bi bi-arrow-up"></i>
                            </button>
                            <button
                                class="btn btn-outline-secondary btn-sm"
                                type="button"
                                :disabled="index === fields.length - 1"
                                title="Опустить"
                                @click="moveField(index, 1)"
                            >
                                <i class="bi bi-arrow-down"></i>
                            </button>
                            <button
                                class="btn btn-outline-danger btn-sm"
                                type="button"
                                title="Удалить поле"
                                @click="removeField(index)"
                            >
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>

                    <div class="row g-3 mb-2">
                        <div class="col-md-8">
                            <label class="form-label">Название</label>
                            <input v-model.trim="field.name" class="form-control" maxlength="256" required />
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Тип</label>
                            <select v-model="field.type" class="form-select" required @change="ensureOptions(field)">
                                <option v-for="type in fieldTypes" :key="type.value" :value="type.value">
                                    {{ type.label }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="d-flex flex-wrap gap-4 mb-2">
                        <label class="form-check form-switch">
                            <input v-model="field.required" class="form-check-input" type="checkbox" />
                            <span class="form-check-label">Обязательное поле</span>
                        </label>
                        <label class="form-check form-switch">
                            <input v-model="field.showoff" class="form-check-input" type="checkbox" />
                            <span class="form-check-label">Закрепить на карточке</span>
                        </label>
                    </div>

                    <div v-if="hasOptions(field)">
                        <label class="form-label">Варианты</label>
                        <draggable
                            v-model="field.options"
                            tag="div"
                            ghost-class="drag-ghost"
                            handle=".option-handle"
                        >
                            <template #item="{index: optionIndex}">
                                <div class="input-group input-group-sm mb-2">
                                    <span class="option-handle input-group-text" title="Перетащить">
                                        <i class="bi bi-grip-horizontal"></i>
                                    </span>
                                    <input v-model="field.options[optionIndex]" class="form-control" required />
                                    <button
                                        class="btn btn-outline-secondary"
                                        type="button"
                                        :disabled="optionIndex === 0"
                                        title="Поднять"
                                        @click="moveOption(field, optionIndex, -1)"
                                    >
                                        <i class="bi bi-arrow-up"></i>
                                    </button>
                                    <button
                                        class="btn btn-outline-secondary"
                                        type="button"
                                        :disabled="optionIndex === field.options.length - 1"
                                        title="Опустить"
                                        @click="moveOption(field, optionIndex, 1)"
                                    >
                                        <i class="bi bi-arrow-down"></i>
                                    </button>
                                    <button
                                        class="btn btn-outline-danger"
                                        type="button"
                                        title="Удалить вариант"
                                        @click="removeOption(field, optionIndex)"
                                    >
                                        <i class="bi bi-x-lg"></i>
                                    </button>
                                </div>
                            </template>
                        </draggable>

                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-outline-primary" type="button" @click="addOption(field)">
                                <i class="bi bi-plus-lg me-1"></i> Вариант
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" type="button" @click="sortOptions(field)">
                                <i class="bi bi-sort-alpha-down me-1"></i> По алфавиту
                            </button>
                        </div>
                    </div>
                </div>
            </template>
        </draggable>

        <button class="btn btn-sm btn-outline-primary" type="button" @click="addField">
            <i class="bi bi-plus-circle me-1"></i> Добавить поле
        </button>
    </div>
</template>

<script>
import draggable from 'vuedraggable';

export default {
    name: 'FormFieldsEditor',
    components: {draggable},
    props: {
        modelValue: {
            type: Array,
            required: true,
        },
    },
    emits: ['update:modelValue'],
    data() {
        return {
            keys: new WeakMap(),
            nextKey: 1,
            fieldTypes: [
                {value: 'string', label: 'Строка'},
                {value: 'text', label: 'Текст'},
                {value: 'number', label: 'Число'},
                {value: 'date', label: 'Дата'},
                {value: 'datetime', label: 'Дата и время'},
                {value: 'select', label: 'Один вариант'},
                {value: 'checkboxes', label: 'Несколько вариантов'},
                {value: 'checkbox', label: 'Флажок'},
                {value: 'file', label: 'Файл'},
            ],
        };
    },
    computed: {
        fields: {
            get() {
                return this.modelValue;
            },
            set(value) {
                this.$emit('update:modelValue', value);
            },
        },
    },
    methods: {
        fieldKey(field) {
            if (!this.keys.has(field)) this.keys.set(field, this.nextKey++);
            return this.keys.get(field);
        },
        hasOptions(field) {
            return field.type === 'select' || field.type === 'checkboxes';
        },
        ensureOptions(field) {
            if (!Array.isArray(field.options)) field.options = [];
        },
        addField() {
            this.fields.push({
                name: '',
                type: 'text',
                required: false,
                showoff: false,
                options: [],
            });
        },
        removeField(index) {
            if (window.confirm('Удалить это поле?')) this.fields.splice(index, 1);
        },
        moveField(index, offset) {
            const target = index + offset;
            if (target < 0 || target >= this.fields.length) return;
            const [field] = this.fields.splice(index, 1);
            this.fields.splice(target, 0, field);
        },
        addOption(field) {
            this.ensureOptions(field);
            field.options.push('');
        },
        removeOption(field, index) {
            if (window.confirm('Удалить этот вариант?')) field.options.splice(index, 1);
        },
        moveOption(field, index, offset) {
            const target = index + offset;
            if (target < 0 || target >= field.options.length) return;
            const [option] = field.options.splice(index, 1);
            field.options.splice(target, 0, option);
        },
        sortOptions(field) {
            field.options = [...field.options].sort((a, b) => (
                (a || '').trim().localeCompare((b || '').trim(), 'ru')
            ));
        },
    },
};
</script>

<style scoped>
.field-card {
    background: var(--silaeder-surface-subtle);
}

.drag-handle,
.option-handle {
    cursor: grab;
    user-select: none;
}

.drag-ghost {
    background-color: var(--silaeder-primary-soft);
    opacity: 0.7;
}
</style>
