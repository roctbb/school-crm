import {defineStore} from "pinia";
import {getProfile} from "@/api/auth.js";
import {fetchObjectTypes, fetchObjectsByType} from "@/api/objects.js";

const useMainStore = defineStore("mainStore", {
    // Состояние
    state: () => ({
        token: null,
        profile: null,
        objects: {}, // Объекты, сгруппированные по типу
        objectTypes: [], // Список типов объектов
        isLoading: false, // Состояние загрузки данных
    }),

    actions: {
        async tryLoadProfile() {
            try {
                console.log("Trying to load profile with token:", this.token);
                this.profile = await getProfile(this.token);
                console.log("Loaded");
                return true;
            } catch (e) {
                return false;
            }
        },

        async checkAuth() {
            if (!this.profile && this.token) await this.tryLoadProfile();
            if (this.profile) return true;
            return false;
        },

        async setToken(new_token) {
            this.token = new_token;
            const isValid = await this.tryLoadProfile();
            if (!isValid) {
                this.logout();
                throw new Error("Failed to set token: " + e.message);
            }
            localStorage.setItem("token", new_token);
        },

        logout() {
            this.token = null;
            this.profile = null;
            this.objects = {};
            this.objectTypes = [];
            localStorage.clear();
        },

        loadStateFromLocalStorage() {
            const token = localStorage.getItem("token");

            if (token) {
                this.token = token;
            }
        },

        /**
         * Загрузка всех типов объектов
         */
        async fetchObjectTypes() {
            try {
                if (!this.token) {
                    throw new Error("Отсутствует токен для авторизации.");
                }
                this.isLoading = true;
                const types = await fetchObjectTypes(this.token);
                this.objectTypes = types;
            } catch (error) {
                console.error("Ошибка при загрузке типов объектов:", error);
            } finally {
                this.isLoading = false;
            }
        },

        /**
         * Загрузка объектов для конкретного типа
         * @param {string} typeCode - Код типа объектов
         */
        async fetchObjectsByType(typeCode) {
            try {
                if (!this.token) {
                    throw new Error("Отсутствует токен для авторизации.");
                }
                if (this.objects[typeCode]) {
                    // Если объекты уже загружены, повторную загрузку не выполняем
                    return;
                }
                this.isLoading = true;
                const objects = await fetchObjectsByType(typeCode, this.token);
                this.objects = {
                    ...this.objects,
                    [typeCode]: objects,
                };
            } catch (error) {
                console.error(`Ошибка при загрузке объектов типа ${typeCode}:`, error);
            } finally {
                this.isLoading = false;
            }
        },
    },

    getters: {
        getObjectsByType: (state) => (typeCode) => {
            return state.objects[typeCode] || [];
        },
    },
});

export default useMainStore;