// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ObjectsView from '../views/ObjectsView.vue';

const routes = [
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/objects', name: 'Objects', component: ObjectsView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;