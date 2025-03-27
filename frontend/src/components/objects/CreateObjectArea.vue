<template>
    <!-- Если вкладка не "portfolio" -->
    <div v-if="activeTab !== 'portfolio'">
        <button
            v-if="activeTab && canCreateByType(getObjectTypeByCode(activeTab))"
            class="btn btn-success btn-sm ms-1"
            @click="triggerCreateObject(activeTab)"
        >
            <i class="bi bi-plus me-1"></i> Создать
        </button>
    </div>

    <!-- Если вкладка — "portfolio" -->
    <div v-else>
        <div class="dropdown">
            <button
                class="btn btn-success btn-sm dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
            >
                <i class="bi bi-plus me-1"></i> Создать
            </button>

            <!-- Добавляем плавное появление/скрытие списка типов объектов -->
            <transition name="dropdown-fade">
                <ul
                    v-if="showDropdown"
                    class="dropdown-menu show"
                >
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
            </transition>
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
    methods: {
        // Объединяем методы здесь
        getObjectTypeByCode(code) {
            return this.store.getObjectTypeByCode(code);
        },
        triggerCreateObject(code) {
            this.$emit("createObject", code);
            this.showDropdown = false;
        },
        handleOutsideClick(event) {
            const dropdown = this.$el.querySelector(".dropdown");
            if (dropdown && !dropdown.contains(event.target)) {
                this.showDropdown = false;
            }
        },
    },
};
</script>

<style scoped>
/* Небольшая анимация исчезновения/появления меню */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
    transition: opacity 0.2s ease;
}

.dropdown-fade-enter,
.dropdown-fade-leave-to {
    opacity: 0;
}
</style>