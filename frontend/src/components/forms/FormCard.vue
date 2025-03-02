<template>
    <div class="card mb-3" style="width: 18rem;">
        <div class="card-body">
            <!-- Шапка карточки: название формы и кнопка удаления -->
            <div class="d-flex align-items-center">
                <h5 class="card-title flex-grow-1 mb-0">
                    {{ form.name }}
                </h5>
                <button
                    type="button"
                    class="btn btn-light btn-sm text-secondary border-0 position-absolute"
                    style="top: 5px; right: 5px;"
                    @click.stop="deleteForm"
                >
                    <i class="bi bi-x-lg"></i>
                </button>

            </div>


            <!-- Кнопка "Редактировать" -->
            <button
                type="button"
                class="mt-3 btn btn-sm btn-light"
                @click="editForm"
            >
                Редактировать
            </button>
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
/* Пример простых стилей: */

</style>