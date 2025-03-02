// src/router/index.js
import {createRouter, createWebHistory} from 'vue-router';
import LoginView from '../views/Auth/LoginView.vue';
import RegisterView from '../views/Auth/RegisterView.vue';
import ObjectsView from '../views/Objects/ObjectsView.vue';
import useMainStore from "@/stores/mainStore.js";
import ObjectDetailsView from "@/views/Objects/ObjectDetailsView.vue";
import ManageObjectView from "@/views/Objects/ManageObjectView.vue";
import FormCategoriesView from "@/views/Forms/FormCategoriesView.vue";
import ManageFormView from "@/views/Forms/ManageFormView.vue";

const routes = [
    {path: '/login', name: 'Login', component: LoginView, meta: {withoutAuth: true}},
    {path: '/register', name: 'Register', component: RegisterView, meta: {withoutAuth: true}},
    {path: '/', name: 'Objects', component: ObjectsView, meta: {requiresAuth: true}},
    {
        path: '/:object_type',
        name: 'ObjectType',
        component: ObjectsView,
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type
        })
    },
    {
        path: '/:object_type/:object_id',
        name: 'ObjectDetails',
        component: ObjectDetailsView,
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: route.params.object_id
        })
    },
    {
        path: '/:object_type/create',
        name: 'CreateObject',
        component: ManageObjectView,
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type
        })

    },
    {
        path: '/:object_type/:object_id/edit',
        name: 'EditObject',
        component: ManageObjectView,
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: route.params.object_id
        })
    },
    {
        path: '/forms',
        name: 'Forms',
        component: () => FormCategoriesView,
        meta: {requiresAuth: true},
    },
    {
        path: '/forms/:categoryId/create',
        name: 'CreateForm',
        component: () => ManageFormView,
        meta: {requiresAuth: true},
        props: true
    },
    {
        path: '/forms/:categoryId/:formId/edit',
        name: 'EditForm',
        component: () => ManageFormView,
        meta: {requiresAuth: true},
        props: true
    },


];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Навигационный охранник
router.beforeEach(async (to, from, next) => {
    const has_auth = await useMainStore().checkAuth();
    console.log("Router auth check: ", has_auth ? "OK" : "FAIL")
    if (to.meta.requiresAuth && !has_auth) {
        next({name: 'Login'});
    } else if (to.meta.withoutAuth && has_auth) {
        next({name: 'Objects'});
    } else {
        next();
    }


});


export default router;