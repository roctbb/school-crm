// src/router/index.js
import {createRouter, createWebHistory} from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ObjectsView from '../views/ObjectsView.vue';
import useMainStore from "@/stores/mainStore.js";

const routes = [
    {path: '/login', name: 'Login', component: LoginView},
    {path: '/register', name: 'Register', component: RegisterView},
    {path: '/', name: 'Objects', component: ObjectsView, meta: {requiresAuth: true}},
    {
        path: '/objects/:object_type/:object_id',
        name: 'ObjectDetails',
        component: () => import('../views/ObjectDetailsView.vue'),
        meta: {requiresAuth: true}
    },


];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Навигационный охранник
router.beforeEach(async (to, from, next) => {
    const mainStore = useMainStore();
    if (to.meta.requiresAuth && !(await mainStore.checkAuth())) {
        next({name: 'Login'});
    } else {
        next();
    }
});


export default router;