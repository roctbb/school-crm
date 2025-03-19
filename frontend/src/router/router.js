import {createRouter, createWebHistory} from 'vue-router';
import useMainStore from "@/stores/mainStore.js";

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Auth/LoginView.vue'),
        meta: {withoutAuth: true}
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/Auth/RegisterView.vue'),
        meta: {withoutAuth: true}
    },
    {
        path: '/password/email',
        name: 'ForgotPassword',
        component: () => import('@/views/Auth/ForgotPasswordView.vue'),
        meta: {withoutAuth: true} // Для гостей, чтобы не требовал авторизации
    },
    {
        path: '/password/reset',
        name: 'ResetPassword',
        component: () => import('@/views/Auth/ResetPasswordView.vue'),
        meta: {withoutAuth: true} // Для гостей, чтобы не требовал авторизации
    },
    {
        path: '/',
        name: 'Objects',
        component: () => import('@/views/Objects/ObjectsView.vue'),
        meta: {requiresAuth: true},
        // Передаём параметры через query
        props: route => ({
            view: route.query.view || 'cards',
            grouping: route.query.grouping || '',
            search: route.query.search || '',
            unconfirmed: route.query.unconfirmed === 'true'
        })
    },
    {
        path: '/:object_type',
        name: 'ObjectType',
        component: () => import('@/views/Objects/ObjectsView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            // Аналогично, вытягиваем нужные параметры из query
            view: route.query.view || 'cards',
            grouping: route.query.grouping || '',
            search: route.query.search || '',
            unconfirmed: route.query.unconfirmed === 'true'
        })
    },
    {
        path: '/:object_type/:object_id',
        name: 'ObjectDetails',
        component: () => import('@/views/Objects/ObjectDetailsView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: Number(route.params.object_id)
        })
    },
    {
        path: '/:object_type/create',
        name: 'CreateObject',
        component: () => import('@/views/Objects/ManageObjectView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type
        })
    },
    {
        path: '/:object_type/:object_id/edit',
        name: 'EditObject',
        component: () => import('@/views/Objects/ManageObjectView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: Number(route.params.object_id)
        })
    },
    {
        path: '/forms',
        name: 'Forms',
        component: () => import('@/views/Forms/FormCategoriesView.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/forms/:categoryId/create',
        name: 'CreateForm',
        component: () => import('@/views/Forms/ManageFormView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            categoryId: Number(route.params.categoryId)
        })
    },
    {
        path: '/forms/:categoryId/:formId/edit',
        name: 'EditForm',
        component: () => import('@/views/Forms/ManageFormView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            categoryId: Number(route.params.categoryId),
            formId: Number(route.params.formId)
        })
    },
    {
        path: '/:object_type/:object_id/forms/:formId/submissions/create',
        name: 'CreateSubmission',
        component: () => import('@/views/Submissions/ManageSubmissionView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: Number(route.params.object_id),
            formId: Number(route.params.formId)
        })
    },
    {
        path: '/:object_type/:object_id/submissions/:submissionId/edit',
        name: 'EditSubmission',
        component: () => import('@/views/Submissions/ManageSubmissionView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: Number(route.params.object_id),
            submissionId: Number(route.params.submissionId)
        })
    },
    {
        path: '/:object_type/:object_id/submissions/:submissionId',
        name: 'SubmissionDetails',
        component: () => import('@/views/Submissions/SubmissionDetailsView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            objectTypeCode: route.params.object_type,
            objectId: Number(route.params.object_id),
            submissionId: Number(route.params.submissionId)
        })
    },
    {
        path: '/import',
        name: 'Import',
        component: () => import('@/views/Import/ImportView.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/invitations',
        name: 'Invitations',
        component: () => import('@/views/Invitations/InvitationsView.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/forms/:formId/submissions',
        name: 'FormSubmissions',
        component: () => import('@/views/Forms/FormSubmissionsView.vue'),
        meta: {requiresAuth: true},
        props: route => ({
            formId: Number(route.params.formId)
        })
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// Пример проверки аутентификации
router.beforeEach(async (to, from, next) => {
    const has_auth = await useMainStore().checkAuth();
    console.log("Router auth check: ", has_auth ? "OK" : "FAIL");
    if (to.meta.requiresAuth && !has_auth) {
        console.log("Redirecting to login")
        next({name: 'Login'});
    } else if (to.meta.withoutAuth && has_auth) {
        console.log("Redirecting to main")
        next({name: 'Objects'});
    } else {
        next();
    }
});

export default router;