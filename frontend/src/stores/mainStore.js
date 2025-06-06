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
            if (!api_client.token) return false;
            if (this.profile) return true;
            try {
                this.profile = await getProfile();
                return true;
            } catch (e) {
                if (e.code === 401) {
                    return false;
                } else {
                    throw e;
                }
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
            } else {
                localStorage.setItem("token", new_token);
            }
        },

        logout() {
            console.log("Logging out");
            api_client.setToken(null);
            this.token = null;
            this.profile = null;
            this.reset()
            localStorage.clear();
        },

        reset() {
            this.objects = {};
            this.objectTypes = [];
            this.formCategories = [];
        },

        async loadStateFromLocalStorage() {
            const token = localStorage.getItem("token");

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
                    category.forms = category.forms.map(form => new Form(form, this, category.id));
                }
            } catch (error) {
                console.error(`Ошибка при загрузке форм:`, error);
            } finally {
                this.isLoading = false;
            }
        },

        getForm(id) {
            return this.formCategories.map(category => category.forms).flat().find(form => form.id === parseInt(id));
        },

        getFormCategory(id) {
            return this.formCategories.find(category => category.id === parseInt(id));
        },

        allObjects() {
            return Object.values(this.objects).flat()
        },

        getObject(typeCode, id) {
            if (!id) {
                return this.allObjects().find(obj => obj.id === typeCode);
            }
            return this.objects[typeCode].find(obj => obj.id === parseInt(id));
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