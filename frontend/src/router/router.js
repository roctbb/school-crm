import {createRouter, createWebHistory} from 'vue-router';
import useMainStore from "@/stores/mainStore.js";
import {finishNavigationLoading, startNavigationLoading} from '@/services/globalLoading.js';

const NO_GROUPING_QUERY_VALUE = '__none__';

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
            grouping: route.query.grouping === NO_GROUPING_QUERY_VALUE ? '' : route.query.grouping || '',
            groupingSpecified: Boolean(route.query.grouping),
            search: route.query.search || '',
            unconfirmed: route.query.unconfirmed === 'true',
            page: Math.max(1, Number.parseInt(route.query.page, 10) || 1)
        })
    },
    {
        path: '/admin/object-types',
        name: 'ObjectTypesAdmin',
        component: () => import('@/views/Admin/ObjectTypesAdminView.vue'),
        meta: {requiresAuth: true, requiresAdmin: true}
    },
    {
        path: '/admin/form-categories',
        name: 'FormCategoriesAdmin',
        component: () => import('@/views/Admin/FormCategoriesAdminView.vue'),
        meta: {requiresAuth: true, requiresAdmin: true}
    },
    {
        path: '/admin/oauth-clients',
        name: 'OAuthClientsAdmin',
        component: () => import('@/views/Admin/OAuthClientsAdminView.vue'),
        meta: {requiresAuth: true, requiresAdmin: true}
    },
    {
        path: '/settings/notifications',
        name: 'NotificationSettings',
        component: () => import('@/views/Settings/NotificationSettingsView.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/oauth/authorize',
        name: 'OAuthAuthorize',
        component: () => import('@/views/Auth/OAuthAuthorizeView.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/oauth/logout',
        name: 'OAuthLogout',
        component: () => import('@/views/Auth/OAuthLogoutView.vue')
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
            grouping: route.query.grouping === NO_GROUPING_QUERY_VALUE ? '' : route.query.grouping || '',
            groupingSpecified: Boolean(route.query.grouping),
            search: route.query.search || '',
            unconfirmed: route.query.unconfirmed === 'true',
            page: Math.max(1, Number.parseInt(route.query.page, 10) || 1)
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

router.beforeEach(async (to) => {
    startNavigationLoading();
    const store = useMainStore();
    const has_auth = await store.checkAuth();
    console.log("Router auth check: ", has_auth ? "OK" : "FAIL");
    if (to.meta.requiresAuth && !has_auth) {
        console.log("Redirecting to login")
        return {name: 'Login', query: {redirect: to.fullPath}};
    }
    if (to.meta.requiresAdmin && store.profile?.role !== 'admin') {
        return {name: 'Objects'};
    }
    if (to.meta.withoutAuth && has_auth) {
        console.log("Redirecting to main")
        const redirect = typeof to.query.redirect === 'string'
            && to.query.redirect.startsWith('/')
            && !to.query.redirect.startsWith('//')
            ? to.query.redirect
            : null;
        return redirect || {name: 'Objects'};
    }
    return true;
});

router.afterEach(() => {
    finishNavigationLoading();
});

router.onError(() => {
    finishNavigationLoading();
});

export default router;
