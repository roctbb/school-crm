<template>
    <BaseLayout>
        <div class="container py-4">
            <div class="row justify-content-center">
                <div class="col-md-10">
                    <div class="card mb-3">
                        <div class="card-header">
                            <h3 class="m-0">Список инвайтов</h3>
                        </div>
                        <div class="card-body">
                            <div v-if="isLoading" class="text-center my-3">
                                <Loading/>
                            </div>
                            <div v-else>
                                <table class="table table-bordered table-striped">
                                    <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Код приглашения</th>
                                        <th>Роль</th>
                                        <th>Объект</th>
                                        <th>Дата создания</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    <tr v-for="inv in invitations" :key="inv.id">
                                        <td>{{ inv.id }}</td>
                                        <td>
                                            <a href="#" @click.prevent="copyInviteUrl(inv.key)">
                                                {{ inv.key }}
                                            </a>
                                            <!-- Выводим сообщение, если только что скопировался этот ключ -->
                                            <small
                                                v-if="copiedKey === inv.key"
                                                class="text-success ms-2"
                                            >
                                                Скопировано!
                                            </small>
                                        </td>

                                        <td>{{ inv.role }}</td>
                                        <td>{{ store.getObject(inv.object_id)?.name }}</td>
                                        <td>{{ formatDateTime(new Date(inv.created_at)) }}</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <!-- Создание инвайтов -->
                    <div class="card">
                        <div class="card-header">
                            <h3 class="m-0">Создать новые инвайты</h3>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="handleCreateInvitations" class="row g-3">
                                <!-- Выбор типа из доступных -->
                                <div class="col-md-6">
                                    <label for="typeCode" class="form-label">Тип инвайтов</label>
                                    <select
                                        id="typeCode"
                                        v-model="typeCode"
                                        class="form-select"
                                    >
                                        <option value="">Выберите тип</option>
                                        <!-- Если храните типы в массиве availableTypes -->
                                        <option
                                            v-for="item in availableTypes"
                                            :key="item.code"
                                            :value="item.code"
                                        >
                                            {{ item.name }}
                                        </option>
                                    </select>
                                </div>

                                <!-- Выбор роли: student, teacher, admin -->
                                <div class="col-md-6">
                                    <label for="role" class="form-label">Роль</label>
                                    <select
                                        id="role"
                                        v-model="role"
                                        class="form-select"
                                    >
                                        <option value="">Выберите роль</option>
                                        <option value="student">Студент</option>
                                        <option value="teacher">Преподаватель</option>
                                        <option value="admin">Админ</option>
                                    </select>
                                </div>

                                <div class="col-12 mt-3">
                                    <button
                                        type="submit"
                                        class="btn btn-primary"
                                        :disabled="isCreating"
                                    >
                                        Создать
                                    </button>
                                </div>
                            </form>

                            <div
                                v-if="createMessage"
                                class="alert mt-3"
                                :class="isCreateSuccess ? 'alert-success' : 'alert-danger'"
                            >
                                {{ createMessage }}
                            </div>
                        </div>
                    </div>


                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script>
import {getInvitations, createInvitations} from "@/api/invitations_api.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import {formatDateTime} from "../../utils/helpers.js";
import useMainStore from "@/stores/mainStore.js";

export default {
    name: "InvitationsView",
    components: {
        BaseLayout,
        Loading,
    },
    data() {
        return {
            invitations: [],
            isLoading: false,
            typeCode: "",
            role: "",
            isCreating: false,
            createMessage: "",
            copiedKey: null,
            isCreateSuccess: false,
            store: useMainStore()
        };
    },
    async created() {
        await this.store.loadObjects()
        await this.loadInvitations();
    },
    methods: {
        formatDateTime,
        copyInviteUrl(invKey) {
            // Формируем полную ссылку для копирования (если нужно абсолютный адрес с доменом,
            // можно вместо window.location.origin указать свой домен)
            const linkToCopy = `${window.location.origin}/register?invite=${invKey}`;

            // Копируем в буфер обмена
            navigator.clipboard.writeText(linkToCopy)
                .then(() => {
                    // Показываем «Скопировано!» только для выбранного key
                    this.copiedKey = invKey;
                    // Через пару секунд скрываем надпись
                    setTimeout(() => {
                        this.copiedKey = null;
                    }, 2000);
                })
                .catch(err => {
                    console.error("Ошибка при копировании:", err);
                });
        },

        async loadInvitations() {
            try {
                this.isLoading = true;
                const data = await getInvitations();
                // Ожидаем, что ответ — это массив приглашений
                this.invitations = data;
                this.availableTypes = this.store.objectTypes
            } catch (error) {
                console.error("Ошибка при загрузке инвайтов:", error);
            } finally {
                this.isLoading = false;
            }
        },
        async handleCreateInvitations() {
            if (!this.typeCode || !this.role) {
                this.createMessage = "Укажите и тип, и роль.";
                this.isCreateSuccess = false;
                return;
            }
            this.isCreating = true;
            this.createMessage = "";
            try {
                const created = await createInvitations(this.typeCode, this.role);
                // Ожидается массив созданных инвайтов
                // Можно объединить новый список с существующим, если нужно
                this.invitations.push(...created);
                this.createMessage = "Инвайты успешно созданы!";
                this.isCreateSuccess = true;
            } catch (error) {
                this.createMessage = "Ошибка при создании инвайтов.";
                this.isCreateSuccess = false;
                console.error("Ошибка:", error);
            } finally {
                this.isCreating = false;
            }
        },
    },
};
</script>

<style scoped>
/* При желании можно добавить стили */
</style>