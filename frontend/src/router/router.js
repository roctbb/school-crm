// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import useMainStore from "@/stores/mainStore.js";

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Auth/LoginView.vue'),
        meta: { withoutAuth: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/Auth/RegisterView.vue'),
        meta: { withoutAuth: true }
    },
    {
        path: '/',
        name: 'Objects',
        component: () => import('@/views/Objects/ObjectsView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/:object_type',
        name: 'ObjectType',
        component: () => import('@/views/Objects/ObjectsView.vue'),
        meta: { requiresAuth: true },
        props: route => ({
            objectTypeCode: route.params.object_type
        })
    },
    {
        path: '/:object_type/:object_id',
        name: 'ObjectDetails',
        component: () => import('@/views/Objects/ObjectDetailsView.vue'),
        meta: { requiresAuth: true },
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: route.params.object_id
        })
    },
    {
        path: '/:object_type/create',
        name: 'CreateObject',
        component: () => import('@/views/Objects/ManageObjectView.vue'),
        meta: { requiresAuth: true },
        props: route => ({
            objectTypeCode: route.params.object_type
        })
    },
    {
        path: '/:object_type/:object_id/edit',
        name: 'EditObject',
        component: () => import('@/views/Objects/ManageObjectView.vue'),
        meta: { requiresAuth: true },
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: route.params.object_id
        })
    },
    {
        path: '/forms',
        name: 'Forms',
        component: () => import('@/views/Forms/FormCategoriesView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/forms/:categoryId/create',
        name: 'CreateForm',
        component: () => import('@/views/Forms/ManageFormView.vue'),
        meta: { requiresAuth: true },
        props: true
    },
    {
        path: '/forms/:categoryId/:formId/edit',
        name: 'EditForm',
        component: () => import('@/views/Forms/ManageFormView.vue'),
        meta: { requiresAuth: true },
        props: true
    },
    {
        path: '/:object_type/:object_id/forms/:formId/submissions/create',
        name: 'CreateSubmission',
        component: () => import('@/views/Submissions/ManageSubmissionView.vue'),
        meta: { requiresAuth: true },
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: route.params.object_id,
            formId: route.params.formId
        })
    },
    {
        path: '/:object_type/:object_id/submissions/:submissionId/edit',
        name: 'EditSubmission',
        component: () => import('@/views/Submissions/ManageSubmissionView.vue'),
        meta: { requiresAuth: true },
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: route.params.object_id,
            submissionId: route.params.submissionId
        })
    },
    {
        path: '/:object_type/:object_id/submissions/:submissionId',
        name: 'SubmissionDetails',
        component: () => import('@/views/Submissions/SubmissionDetailsView.vue'),
        meta: { requiresAuth: true },
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: route.params.object_id,
            submissionId: route.params.submissionId
        })
    },
    {
        path: '/import',
        name: 'Import',
        component: () => import('@/views/Import/ImportView.vue'),
        meta: { requiresAuth: true }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// Навигационный охранник
router.beforeEach(async (to, from, next) => {
    const has_auth = await useMainStore().checkAuth();
    console.log("Router auth check: ", has_auth ? "OK" : "FAIL");
    if (to.meta.requiresAuth && !has_auth) {
        console.log("Redirecting to login")
        next({ name: 'Login' });
    } else if (to.meta.withoutAuth && has_auth) {
        console.log("Redirecting to main")
        next({ name: 'Objects' });
    } else {
        next();
    }
});

export default router;