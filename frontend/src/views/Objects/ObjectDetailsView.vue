<template>
    <BaseLayout>
        <div class="object-details-page" v-if="object">
            <!-- Блок заголовка, фото и кнопок -->
            <div class="d-flex align-items-start mb-3">
                <!-- Фото слева -->
                <div v-if="object.attributes?.photo" class="me-3">
                    <img
                        :src="object.attributes.photo"
                        alt="Object Photo"
                        style="max-width: 150px;"
                    />
                </div>
                <!-- Заголовок -->
                <div class="flex-grow-1">
                    <h2 class="me-2">
                        {{ capitalize(object_type.name) }}: {{ object.name }}
                    </h2>
                    <div>
                        <AttributePresenter :object="object" :type="object_type"/>
                    </div>
                </div>
                <!-- Блок выпадающего списка -->
                <div>
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
                                    <i class="bi bi-pencil"></i> Редактировать
                                </router-link>
                            </li>
                            <li>
                                <button
                                    class="dropdown-item text-danger"
                                    @click="handleDelete"
                                >
                                    <i class="bi bi-trash"></i> Удалить
                                </button>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-8">
                    <div v-for="type in connectedTypes" :key="type.code">
                        <div v-if="findRelativesByType(type).length" class="mb-3">
                            <h5 class="pb-2">{{ type.name }}</h5>

                            <div class="row">
                                <div class="col-md-6 col-lg-4 col-xl-3 col-xl-2 mb-4 d-flex align-items-stretch"
                                     v-for="child in findRelativesByType(type)" :key="child.id">
                                    <ObjectCard :type="type" :object="store.getObject(type.code, child.id)"/>
                                </div>
                            </div>

                        </div>


                    </div>

                    <div v-for="form_category in object_type.form_categories" :key="form_category.id" class="mb-4">
                        <h5 class="pb-2">{{ form_category.name }}</h5>

                        <div class="row">
                                <div class="col-md-6 col-lg-4 col-xl-3 col-xl-2 mb-4 d-flex align-items-stretch"
                                     v-for="submission in object._submissions.filter(submission => submission.form.category_id === form_category.id)" :key="submission.id">
                                    <SubmissionCard :submission="submission" :object="object"/>
                                </div>
                            </div>

                        <!-- Выпадающий список форм -->
                        <div class="btn-group">
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

                </div>
                <div class="col-md-4">
                    <CommentsPanel
                        :object="object"
                    />
                </div>
            </div>


            <button
                class="btn btn-secondary btn-sm"
                @click="$router.push(`/${object_type.code}`)"
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
import {capitalize} from "../../utils/helpers.js";
import ObjectCard from "@/components/objects/ObjectCard.vue";
import AttributePresenter from "@/components/objects/AttributePresenter.vue";
import CommentsPanel from "@/components/objects/CommentsPanel.vue";
import SubmissionCard from "@/components/submissions/SubmissionCard.vue";

export default {
    methods: {
        capitalize,
        async handleDelete() {
            const confirmed = window.confirm('Вы действительно хотите удалить этот объект?');
            if (confirmed) {
                await deleteObject(this.object.id);
                this.store.objects[this.object.type] = this.store.objects[this.object.type]
                    .filter(obj => obj.id !== this.object.id);
                this.$router.push(`/${this.object.type}`);
            }
        },
        findRelativesByType(type) {
            console.log("findRelativesByType:", type)
            const relatives = [...this.object.children.filter(child => child.type === type.code), ...this.object.parents.filter(parent => parent.type === type.code)]
            console.log("relatives:", relatives)
            return relatives
        },
        goToCreateSubmission(formId) {
            // Переход на страницу создания ответа
            this.$router.push({
                name: 'CreateSubmission',
                params: {
                    object_type: this.object_type.code,
                    object_id: this.object.id,
                    formId: formId
                }
            });
        },
        async load() {
            this.connectedTypes = [];
            let {object_type, object_id} = this.$route.params;
            object_id = parseInt(object_id);
            await this.store.loadObjects();
            this.object_type = this.store.getObjectTypeByCode(object_type);
            this.object = this.store.getObject(object_type, object_id);
            await this.object.loadSubmissions();

            console.log("object:", this.object)

            const unique_children_codes = [...new Set(this.object.children.map(child => child.type))];
            const unique_parents_codes = [...new Set(this.object.parents.map(child => child.type))];

            console.log("unique_children_codes:", unique_children_codes)
            console.log("unique_parents_codes:", unique_parents_codes)

            const unique_type_codes = [...new Set([...unique_children_codes, ...unique_parents_codes])];

            console.log("unique_type_codes:", unique_type_codes)

            for (let type_code of unique_type_codes) {
                this.connectedTypes.push(this.store.getObjectTypeByCode(type_code))
            }

            console.log("connected types:", this.connectedTypes)
        }
    },
    components: {SubmissionCard, AttributePresenter, ObjectCard, Loading, BaseLayout, CommentsPanel},
    data() {
        return {
            object: null,
            object_type: null,
            store: useMainStore(),
            connectedTypes: [],
        };
    },
    watch: {
        $route: {
            immediate: true,
            async handler(to) {
                await this.load();
            },
        },
    },
};
</script>

<style>
.object-details-page {
    padding: 20px;
}
</style>