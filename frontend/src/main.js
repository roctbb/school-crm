// src/main.js
import {createApp} from 'vue';
import {createPinia} from "pinia";
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import useMainStore from "@/stores/mainStore.js";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

const mainStore = useMainStore(); // Подключаем хранилище
mainStore.loadStateFromLocalStorage();

app.mount('#app');
