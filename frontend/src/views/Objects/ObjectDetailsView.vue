<template>
    <BaseLayout>
        <div class="object-details-page" v-if="object">
            <!-- Заголовок с фото, названием и действиями -->
            <ObjectHeader
                :object="object"
                :object_type="object_type"
                @delete="handleDelete"
                @approve="handleApprove"
                @restore="handleRestore"
            />

            <DetailsWidgetBar :object="object" :type="object_type" />

            <div class="row">
                <div class="col-md-8">
                    <!-- Блок связанных объектов -->
                    <ConnectedTypes
                        :object="object"
                        :connectedTypes="connectedTypes"
                        :viewModes="viewModes"
                        :sortKey.sync="sortKey"
                        :sortDirection.sync="sortDirection"
                        @toggle-view="handleToggleView"
                    />

                    <!-- Блок форм и сабмишенов -->
                    <FormsSubmissions
                        :object="object"
                        :object_type="object_type"
                        @create-submission="goToCreateSubmission"
                    />
                </div>
                <!-- Панель комментариев -->
                <div class="col-md-4" v-if="object.comments.length || canCommentObject(object)">
                    <CommentsPanel :object="object" />
                </div>
            </div>

            <button class="btn btn-light btn-sm" @click="$router.back()">Назад</button>
        </div>
        <Loading v-else />
    </BaseLayout>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import { deleteObject } from "@/api/objects_api.js";
import BaseLayout from "@/components/layouts/BaseLayout.vue";
import Loading from "@/components/common/Loading.vue";
import DetailsWidgetBar from "@/components/objects/DetailsWidgetBar.vue";
import CommentsPanel from "@/components/objects/CommentsPanel.vue";
import ObjectHeader from "@/components/objects/ObjectHeader.vue";
import ConnectedTypes from "@/components/objects/ConnectedTypes.vue";
import FormsSubmissions from "@/components/objects/FormsSubmissions.vue";
import { capitalize } from "@/utils/helpers.js";
import { canCommentObject, canModifyObject, hasTeacherAccess } from "@/utils/access.js";

export default {
    name: "ObjectDetailsView",
    components: {
        BaseLayout,
        Loading,
        DetailsWidgetBar,
        CommentsPanel,
        ObjectHeader,
        ConnectedTypes,
        FormsSubmissions
    },
    data() {
        return {
            object: null,
            object_type: null,
            store: useMainStore(),
            connectedTypes: [],
            sortKey: "name",
            sortDirection: "asc",
            // Для каждого типа задаём режим отображения: table или card
            viewModes: {}
        };
    },
    methods: {
        canCommentObject,
        async handleDelete() {
            const confirmed = window.confirm("Вы действительно хотите удалить этот объект?");
            if (confirmed) {
                await deleteObject(this.object.id);
                this.store.objects[this.object.type] = this.store.objects[this.object.type].filter(
                    (obj) => obj.id !== this.object.id
                );
                this.$router.push(`/${this.object.type}`);
            }
        },
        async handleApprove() {
            const confirmed = window.confirm("Вы действительно хотите утвердить этот объект?");
            if (confirmed) {
                await this.object.approve();
            }
        },
        async handleRestore() {
            const confirmed = window.confirm("Вы действительно хотите откатить изменения для этого объекта?");
            if (confirmed) {
                await this.object.restore();
            }
        },
        async load() {
            this.connectedTypes = [];
            let { object_type, object_id } = this.$route.params;
            object_id = parseInt(object_id);
            await this.store.loadObjects();
            this.object_type = this.store.getObjectTypeByCode(object_type);
            this.object = this.store.getObject(object_type, object_id);
            await this.object.loadSubmissions();

            const unique_children_codes = [
                ...new Set(this.object.children.map(child => child.type))
            ];
            const unique_parents_codes = [
                ...new Set(this.object.parents.map(parent => parent.type))
            ];
            const unique_type_codes = [
                ...new Set([...unique_children_codes, ...unique_parents_codes])
            ];

            for (let type_code of unique_type_codes) {
                this.connectedTypes.push(this.store.getObjectTypeByCode(type_code));
            }
            this.connectedTypes = this.connectedTypes.filter(Boolean);

            // Инициализация режима просмотра для каждого найденного типа
            this.connectedTypes.forEach(t => {
                this.viewModes[t.code] = "table";
            });
        },
        handleToggleView(type) {
            this.viewModes[type.code] =
                this.viewModes[type.code] === "table" ? "card" : "table";
        },
        goToCreateSubmission(formId) {
            this.$router.push({
                name: "CreateSubmission",
                params: {
                    object_type: this.object_type.code,
                    object_id: this.object.id,
                    formId: formId
                }
            });
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