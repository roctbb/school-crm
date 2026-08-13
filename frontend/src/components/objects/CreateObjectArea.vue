<template>
    <div class="create-object-area">
        <button
            v-if="activeTab !== 'portfolio' && activeTab && canCreateByType(getObjectTypeByCode(activeTab))"
            class="btn btn-primary create-object-button ms-2"
            @click="triggerCreateObject(activeTab)"
        >
            <i class="bi bi-plus-lg me-1"></i> Создать
        </button>

        <div v-else-if="activeTab === 'portfolio'" class="dropdown ms-2">
            <button
                class="btn btn-primary create-object-button dropdown-toggle"
                type="button"
                @click="toggleDropdown"
            >
                <i class="bi bi-plus-lg me-1"></i> Создать
            </button>

            <ul v-if="showDropdown" class="dropdown-menu dropdown-menu-end show">
                <li
                    v-for="type in filteredTypes"
                    :key="type.code"
                >
                    <button
                        class="dropdown-item"
                        @click="triggerCreateObject(type.code)"
                    >
                        {{ type.name }}
                    </button>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
    name: "CreateObjectArea",
    props: {
        activeTab: {
            type: String,
            default: "",
        },
        canCreateByType: {
            type: Function,
            default: () => false,
        },
        store: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            showDropdown: false,
        };
    },
    computed: {
        filteredTypes() {
            return this.store.objectTypes.filter((type) =>
                this.canCreateByType(type)
            );
        },
    },
    methods: {
        getObjectTypeByCode(code) {
            return this.store.getObjectTypeByCode(code);
        },
        triggerCreateObject(code) {
            this.$emit("createObject", code);
            // Закрываем дропдаун после создания
            this.showDropdown = false;
        },
        toggleDropdown() {
            // Переключаем состояние дропдауна
            this.showDropdown = !this.showDropdown;
        },
        handleOutsideClick(event) {
            const dropdown = this.$el.querySelector(".dropdown");
            if (dropdown && !dropdown.contains(event.target)) {
                this.showDropdown = false;
            }
        },
    },
    watch: {
        activeTab(newVal) {
            // При переключении вкладки сбрасываем состояние
            this.showDropdown = false;
        },
    },
    mounted() {
        // Обработчик клика "вне" для закрытия меню
        document.addEventListener("click", this.handleOutsideClick);
    },
    beforeUnmount() {
        document.removeEventListener("click", this.handleOutsideClick);
    },
};
</script>

<style scoped>
.create-object-area,
.create-object-button {
    flex: 0 0 auto;
    white-space: nowrap;
}

.create-object-button {
    min-height: 2.45rem;
    padding-inline: 1rem;
    box-shadow: var(--silaeder-shadow-sm);
}
</style>
