// src/main.js
import {createApp} from 'vue';
import {createPinia} from "pinia";
import App from './App.vue';
import router from './router/router.js';
import '@/assets/scss/custom-bootstrap.scss';

import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import "bootstrap-icons/font/bootstrap-icons.css";
import '@/assets/styles.css';
import useMainStore from "@/stores/mainStore.js";
import {APP_NAME} from "@/config/app.js";


const app = createApp(App);
const pinia = createPinia();

document.title = APP_NAME;
app.config.globalProperties.$appName = APP_NAME;

app.use(pinia);

useMainStore().loadStateFromLocalStorage().then(() => {
    app.use(router);
    app.mount('#app');
})




