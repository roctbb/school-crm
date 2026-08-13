<template>
    <div class="card form-card h-100 w-100">
        <div class="card-body">
            <!-- Шапка карточки: название формы и кнопка удаления -->
            <div class="d-flex align-items-center">
                <h5 class="card-title flex-grow-1 mb-0">
                    {{ form.name }}
                </h5>
                <button
                    type="button"
                    class="btn btn-sm text-secondary border-0 position-absolute icon-button delete-button"
                    @click.stop="deleteForm"
                    aria-label="Удалить форму"
                    title="Удалить форму"
                >
                    <i class="bi bi-x-lg"></i>
                </button>

            </div>

            <div class="mt-3">
                <button
                    type="button"
                    class="my-1 btn btn-sm btn-outline-primary"
                    @click="editForm"
                >
                    Редактировать
                </button>
                <router-link
                    :to="`/forms/${this.form.id}/submissions`" class="my-1 btn btn-sm btn-light ms-1"
                >
                    Ответы
                </router-link>
            </div>
            <!-- Кнопка "Редактировать" -->

        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";

export default {
    name: "FormCard",
    props: {
        category: {
            type: Object,
            required: true,
        },
        form: {
            type: Object,
            required: true,
        },
    },
    methods: {
        editForm() {
            // Переход к редактированию формы
            this.$router.push(`/forms/${this.category.id}/${this.form.id}/edit`);
        },

        deleteForm() {
            // Подтверждение удаления
            if (!confirm("Вы действительно хотите удалить эту форму?")) {
                return;
            }
            this.form.delete();
            this.category.forms = this.category.forms.filter(form => form.id !== this.form.id);
        },
    },
};
</script>

<style scoped>
.form-card {
    min-height: 9.5rem;
}

.delete-button {
    top: 0.45rem;
    right: 0.45rem;
}
</style>
