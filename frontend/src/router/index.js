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
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Навигационный охранник
router.beforeEach((to, from, next) => {
    const mainStore = useMainStore();
    if (to.meta.requiresAuth && !mainStore.isAuthenticated) {
        next({name: 'Login'});
    } else {
        next();
    }
});


export default router;