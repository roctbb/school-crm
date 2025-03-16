<template>
    <BaseLayout>
        <div class="object-details-page" v-if="object">
            <!-- Блок заголовка, фото и кнопок -->
            <div class="d-flex align-items-start mb-3">
                <!-- Фото слева -->
                <div v-if="object.attributes?.photo" class="me-3">
                    <img
                        :src="object.attributes.photo"
                        alt="Object Photo" class="rounded-1"
                        style="max-width: 150px;"
                    />
                </div>
                <!-- Заголовок -->
                <div class="flex-grow-1">
                    <h2 class="me-2">
                        <small class="text-muted">{{ capitalize(object_type.name) }}:</small> {{ object.name }} <i
                        class="bi bi-check-lg" v-if="object.hasStudentOwner()"></i>
                    </h2>
                    <div>
                        <div class="badge bg-warning mb-2" v-if="!object.is_approved">Не подтвержден</div>
                        <AttributePresenter :object="object" :type="object_type"/>
                        <DetailsWidgetBar :object="object" :type="object_type"/>
                    </div>
                </div>
                <!-- Блок выпадающего списка -->
                <div v-if="canModifyObject(object)">
                    <div class="dropdown">
                        <button
                            class="btn btn-light dropdown-toggle"
                            type="button"
                            id="actionsMenu"
                            data-bs-toggle="dropdown"
                            aria-expanded="false"
                        >
                            Действия
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="actionsMenu">
                            <li>
                                <router-link
                                    :to="`/${object_type.code}/${object.id}/edit`"
                                    class="dropdown-item"
                                >
                                    <i class="bi bi-pencil me-1"></i> Редактировать
                                </router-link>
                            </li>
                            <li v-if="!object.is_approved && hasTeacherAccess()">
                                <button class="dropdown-item" @click="handleApprove">
                                    <i class="bi bi-check-circle text-success me-1"></i> Утвердить
                                </button>
                            </li>

                            <li v-if="canDeleteObject(object)">
                                <button
                                    class="dropdown-item text-danger"
                                    @click="handleDelete"
                                >
                                    <i class="bi bi-trash me-1"></i> Удалить
                                </button>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-8">
                    <!-- Отображение связанных объектов по типам -->
                    <div
                        v-for="type in connectedTypes"
                        :key="type.code"
                        class="mb-4"
                    >
                        <div v-if="findRelativesByType(type).length">
                            <!-- Заголовок c переключателем и бейджем -->
                            <h5 class="pb-2 d-flex justify-content-between align-items-center">
                                <span>
                                    {{ type.name }}
                                    <span
                                        class="badge bg-secondary rounded-pill py-1 px-2"
                                        style="font-size: 0.75rem;"
                                    >{{ findRelativesByType(type).length }}</span>
                                </span>
                                <button
                                    class="btn btn-outline-secondary btn-sm ms-2"
                                    @click="toggleTypeView(type)"
                                >
                                    <i v-if="viewModes[type.code] === 'table'" class="bi bi-grid"></i>
                                    <i v-else class="bi bi-list"></i>
                                </button>
                            </h5>

                            <!-- Если включен табличный вид, рендерим TableView -->
                            <TableView
                                v-if="viewModes[type.code] === 'table'"
                                :data="findRelativesByType(type)"
                                :attributes="type.available_attributes.filter(a => a.show_off)"
                                :sortKey.sync="sortKey"
                                :sortDirection.sync="sortDirection"
                            />
                            <!-- Иначе – карточный вид -->
                            <CardView
                                v-else
                                :objects="findRelativesByType(type)"
                                :objectType="type"
                            />
                        </div>
                    </div>

                    <!-- Отображение форм по категориям -->
                    <div
                        v-for="form_category in object_type.form_categories"
                        :key="form_category.id"
                        class="mb-4"
                    >
                        <h5 class="pb-2">{{ form_category.name }}</h5>

                        <div class="row">
                            <div
                                class="col-md-6 col-lg-4 col-xl-3 col-xl-2 mb-4 d-flex align-items-stretch"
                                v-for="submission in object._submissions.filter(
                  (submission) =>
                    submission._form.category_id === form_category.id
                )"
                                :key="submission.id"
                            >
                                <SubmissionCard
                                    :submission="submission"
                                    :object="object"
                                />
                            </div>
                        </div>

                        <!-- Выпадающий список форм -->
                        <div class="btn-group" v-if="canFillInCategory(form_category) && canModifyObject(object)">
                            <button
                                class="btn btn-sm btn-light dropdown-toggle"
                                type="button"
                                data-bs-toggle="dropdown"
                                aria-expanded="false"
                            >
                                Добавить
                            </button>
                            <ul class="dropdown-menu">
                                <li
                                    v-for="form in store.getFormCategory(form_category.id).forms"
                                    :key="form.id"
                                >
                                    <a
                                        class="dropdown-item"
                                        href="#"
                                        @click.prevent="goToCreateSubmission(form.id)"
                                    >
                                        {{ form.name }}
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>

                    <!-- Отображение внешних категорий (is_external) -->
                    <div
                        v-for="(category_name, i) in externalCategories"
                        :key="i"
                        class="mb-4"
                    >
                        <h5 class="pb-2">{{ category_name }}</h5>
                        <div class="row">
                            <div
                                class="col-md-6 col-lg-4 col-xl-3 col-xl-2 mb-4 d-flex align-items-stretch"
                                v-for="submission in object._submissions.filter(
                  (submission) =>
                    submission.form.category === category_name
                )"
                                :key="submission.id"
                            >
                                <SubmissionCard
                                    :submission="submission"
                                    :object="object"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Панель комментариев -->
                <div class="col-md-4" v-if="object.comment || canCommentObject(object)">
                    <CommentsPanel :object="object"/>
                </div>
            </div>

            <button
                class="btn btn-secondary btn-sm"
                @click="$router.push(`/`)"
            >
                Назад
            </button>
        </div>
        <Loading v-else/>
    </BaseLayout>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import {deleteObject} from "@/api/objects_api.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import {capitalize} from "@/utils/helpers.js";
import ObjectCard from "@/components/objects/ObjectCard.vue";
import AttributePresenter from "@/components/objects/AttributePresenter.vue";
import CommentsPanel from "@/components/objects/CommentsPanel.vue";
import SubmissionCard from "@/components/submissions/SubmissionCard.vue";
import TableView from "@/components/objects/TableView.vue";
import CardView from "@/components/objects/CardView.vue";
import DetailsWidgetBar from "@/components/objects/DetailsWidgetBar.vue";
import {
    canCommentObject,
    canDeleteObject,
    canFillInCategory,
    canModifyObject,
    hasTeacherAccess
} from "@/utils/access.js";

export default {
    name: "ObjectDetailsView",
    components: {
        DetailsWidgetBar,
        BaseLayout,
        Loading,
        ObjectCard,
        AttributePresenter,
        CommentsPanel,
        SubmissionCard,
        TableView,
        CardView
    },
    data() {
        return {
            object: null,
            object_type: null,
            store: useMainStore(),
            connectedTypes: [],
            sortKey: "name",
            sortDirection: "asc",

            // Каждому типу будем задавать свой режим: 'table' или 'card'
            viewModes: {}
        };
    },
    methods: {
        hasTeacherAccess,
        canCommentObject,
        canFillInCategory,
        canModifyObject,
        canDeleteObject,
        capitalize,
        async handleDelete() {
            const confirmed = window.confirm("Вы действительно хотите удалить этот объект?");
            if (confirmed) {
                await deleteObject(this.object.id);
                this.store.objects[this.object.type] = this.store.objects[
                    this.object.type
                    ].filter((obj) => obj.id !== this.object.id);
                this.$router.push(`/${this.object.type}`);
            }
        },
        async handleApprove() {
            const confirmed = window.confirm("Вы действительно хотите утвердить этот объект?");
            if (confirmed) {
                await this.object.approve();
            }
        },
        /**
         * Находит связанные объекты определённого типа:
         * children + parents того же типа, отсортированные по имени.
         */
        findRelativesByType(type) {
            const relatives = [
                ...this.object.children.filter((child) => child.type === type.code),
                ...this.object.parents.filter((parent) => parent.type === type.code)
            ].map(relative => this.store.getObject(relative.type, relative.id));

            return relatives.sort((a, b) => a.name.localeCompare(b.name));
        },
        /**
         * Переключает вид (табличный/карточный) для конкретного типа
         */
        toggleTypeView(type) {
            this.viewModes[type.code] =
                this.viewModes[type.code] === "table" ? "card" : "table";
        },
        /**
         * Переход на страницу создания ответа для формы
         */
        goToCreateSubmission(formId) {
            this.$router.push({
                name: "CreateSubmission",
                params: {
                    object_type: this.object_type.code,
                    object_id: this.object.id,
                    formId: formId
                }
            });
        },
        /**
         * Загрузка данных компонентов при открытии
         */
        async load() {
            this.connectedTypes = [];
            let {object_type, object_id} = this.$route.params;
            object_id = parseInt(object_id);
            await this.store.loadObjects();
            this.object_type = this.store.getObjectTypeByCode(object_type);
            this.object = this.store.getObject(object_type, object_id);
            await this.object.loadSubmissions();

            const unique_children_codes = [
                ...new Set(this.object.children.map((child) => child.type))
            ];
            const unique_parents_codes = [
                ...new Set(this.object.parents.map((parent) => parent.type))
            ];

            const unique_type_codes = [
                ...new Set([...unique_children_codes, ...unique_parents_codes])
            ];

            for (let type_code of unique_type_codes) {
                this.connectedTypes.push(this.store.getObjectTypeByCode(type_code));
            }

            this.connectedTypes = this.connectedTypes.filter(Boolean)

            // Инициализация viewModes для каждого найденного типа
            this.connectedTypes.forEach((t) => {
                // По умолчанию - 'table'
                this.viewModes[t.code] = "table";
            });
        },
        canFillCategory(category) {
            if (hasAdminAccess()) return true;
            if (category.params && category.params.can_fill && category.params.can_fill.includes(this.store.profile.role)) {
                return true;
            }
            return false;
        }
    },
    computed: {
        /**
         * Собираем все внешние категории у сабмишенов, где is_external = true
         */
        externalCategories() {
            return [
                ...new Set(
                    this.object._submissions
                        .filter((submission) => submission.form.is_external)
                        .map((submission) => submission.form.category)
                )
            ];
        }
    },
    watch: {
        $route: {
            immediate: true,
            async handler() {
                await this.load();
            }
        }
    }
};
</script>

<style scoped>
.object-details-page {
    padding: 20px;
}
</style>