import {defineStore} from "pinia";
import {getProfile} from "@/api/auth_api.js";
import {fetchObjectTypes, fetchObjectsByType, fetchObjects} from "@/api/objects_api.js";
import api_client from "@/api/client.js";
import CrmObject from "@/models/CrmObject.js";
import {fetchFormCategories} from "@/api/forms_api.js";
import Form from "@/models/Form.js";

const useMainStore = defineStore("mainStore", {
    // Состояние
    state: () => ({
        token: null,
        profile: null,
        objects: {}, // Объекты, сгруппированные по типу
        objectTypes: [], // Список типов объектов
        isLoading: false, // Состояние загрузки данных
        objectsLoaded: false,
        forms: {},
        formCategories: []
    }),

    actions: {
        async tryLoadProfile() {
            if (this.profile) return true;

            try {
                this.profile = await getProfile();
                console.log("Loaded");
                return true;
            } catch (e) {
                return false;
            }
        },

        async loadObjects() {
            if (!this.objectTypes.length) {
                await this.fetchObjectTypes();
                await this.fetchObjects();
                await this.fetchFormCategories();
            }
        },

        async checkAuth() {
            return await this.tryLoadProfile();
        },

        async setToken(new_token) {
            api_client.setToken(new_token);

            const isValid = await this.tryLoadProfile();
            if (!isValid) {
                this.logout();
                throw new Error("Failed to set token: " + e.message);
            }
            localStorage.setItem("token", new_token);
        },

        logout() {
            console.log("Logging out");
            api_client.setToken(null);
            this.token = null;
            this.profile = null;
            this.objects = {};
            this.objectTypes = [];
            this.formCategories = [];
            localStorage.clear();
        },

        async loadStateFromLocalStorage() {
            const token = localStorage.getItem("token");
            console.log("Token from localStorage:", token);

            if (token) {
                await this.setToken(token);
            }
        },

        async fetchObjectTypes() {
            try {
                console.log("Loading object types");
                this.isLoading = true;
                this.objectTypes = await fetchObjectTypes();
            } catch (error) {
                console.error("Ошибка при загрузке типов объектов:", error);
            } finally {
                this.isLoading = false;
            }
        },

        async fetchObjects() {
            try {
                this.isLoading = true;
                const objects = await fetchObjects();

                for (const type of this.objectTypes) {
                    this.objects[type.code] = []
                }

                for (const object of objects) {
                    this.objects[object.type].push(new CrmObject(object, this));
                }

                console.log("Loaded objects:", this.objects)
            } catch (error) {
                console.error(`Ошибка при загрузке объектов:`, error);
            } finally {
                this.isLoading = false;
            }
        },

        async fetchFormCategories() {
            try {
                this.isLoading = true;
                this.formCategories = await fetchFormCategories();

                for (const category of this.formCategories) {
                    category.forms = category.forms.map(form => new Form(form, this));
                }
            } catch (error) {
                console.error(`Ошибка при загрузке форм:`, error);
            } finally {
                this.isLoading = false;
            }
        },

        getObject(typeCode, id) {
            if (!id) {
                return Object.values(this.objects).flat().find(obj => obj.type === typeCode);
            }
            return this.objects[typeCode].find(obj => obj.id === id);
        },

        getObjectTypeByCode(code) {
            return this.objectTypes.find(type => type.code === code);
        }
    },

    getters: {
        getObjectsByType: (state) => (typeCode) => {
            return state.objects[typeCode] || [];
        },
    },
});

export default useMainStore;