import {defineStore} from "pinia";
import {getProfile, hasRefreshSession, logoutSession, refreshSession} from "@/api/auth_api.js";
import {fetchObjectTypes, fetchObjectsByType, fetchObjects} from "@/api/objects_api.js";
import api_client from "@/api/client.js";
import CrmObject from "@/models/CrmObject.js";
import {fetchFormCategories} from "@/api/forms_api.js";
import Form from "@/models/Form.js";
import {clearProtectedFileCache} from "@/api/files_api.js";

const ACCESS_TOKEN_KEY = 'crm_access_token';
const REMEMBER_SESSION_KEY = 'crm_remember_session';
const AUTH_MESSAGE_KEY = 'crm_auth_message';
const LEGACY_TOKEN_KEY = 'token';
const SESSION_EXPIRED_MESSAGE = 'Срок действия сессии истёк. Войдите снова.';
const REFRESH_LOCK_NAME = 'crm-session-refresh';

let refreshPromise = null;
let sessionExpirationHandled = false;

async function withRefreshLock(callback) {
    if (typeof navigator !== 'undefined' && navigator.locks?.request) {
        return await navigator.locks.request(REFRESH_LOCK_NAME, callback);
    }
    return await callback();
}

const useMainStore = defineStore("mainStore", {
    // Состояние
    state: () => ({
        token: null,
        profile: null,
        authMessage: "",
        objects: {}, // Объекты, сгруппированные по типу
        objectTypes: [], // Список типов объектов
        isLoading: false, // Состояние загрузки данных
        objectsLoaded: false,
        forms: {},
        formCategories: []
    }),

    actions: {
        configureSessionHandling() {
            api_client.setSessionHandlers({
                refreshSession: () => this.refreshAccessToken(),
                onSessionExpired: () => this.expireSession(),
            });
        },

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

        storeAccessToken(token) {
            api_client.setToken(token);
            this.token = token;
            sessionStorage.setItem(ACCESS_TOKEN_KEY, token);
        },

        async setToken(newToken) {
            localStorage.removeItem(REMEMBER_SESSION_KEY);
            localStorage.removeItem(LEGACY_TOKEN_KEY);
            this.profile = null;
            this.storeAccessToken(newToken);

            const isValid = await this.tryLoadProfile();
            if (!isValid) {
                this.expireSession();
            }
            return isValid;
        },

        async setSession(session, rememberSession = false) {
            if (!session?.access_token) {
                throw new Error('Сервер не вернул токен сессии.');
            }

            sessionExpirationHandled = false;
            this.authMessage = "";
            sessionStorage.removeItem(AUTH_MESSAGE_KEY);
            if (rememberSession && session.persistent) {
                localStorage.setItem(REMEMBER_SESSION_KEY, '1');
            } else {
                localStorage.removeItem(REMEMBER_SESSION_KEY);
            }
            this.profile = null;
            this.storeAccessToken(session.access_token);

            const isValid = await this.tryLoadProfile();
            if (!isValid) {
                this.expireSession();
            }
            return isValid;
        },

        clearSessionState() {
            clearProtectedFileCache();
            api_client.setToken(null);
            this.token = null;
            this.profile = null;
            this.reset();
            sessionStorage.removeItem(ACCESS_TOKEN_KEY);
            localStorage.removeItem(REMEMBER_SESSION_KEY);
            localStorage.removeItem(LEGACY_TOKEN_KEY);
        },

        async logout() {
            try {
                await logoutSession();
            } catch (_error) {
                // Локальный выход должен сработать даже при недоступном сервере.
            } finally {
                this.clearSessionState();
                sessionExpirationHandled = false;
            }
        },

        setAuthMessage(message) {
            this.authMessage = message;
            sessionStorage.setItem(AUTH_MESSAGE_KEY, message);
        },

        consumeAuthMessage() {
            const message = this.authMessage || sessionStorage.getItem(AUTH_MESSAGE_KEY) || "";
            this.authMessage = "";
            sessionStorage.removeItem(AUTH_MESSAGE_KEY);
            return message;
        },

        expireSession(message = SESSION_EXPIRED_MESSAGE) {
            if (sessionExpirationHandled) return;
            sessionExpirationHandled = true;
            const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`;
            this.clearSessionState();
            this.setAuthMessage(message);
            if (window.location.pathname !== '/login') {
                window.location.assign(`/login?redirect=${encodeURIComponent(redirect)}`);
            }
        },

        async refreshAccessToken() {
            if (!hasRefreshSession()) return false;
            if (refreshPromise) return await refreshPromise;

            refreshPromise = withRefreshLock(async () => {
                // Пока вкладка ждала блокировку, другая вкладка могла выйти из системы.
                if (!hasRefreshSession()) return false;
                try {
                    const session = await refreshSession();
                    if (!session?.access_token) return false;
                    this.storeAccessToken(session.access_token);
                    if (session.persistent) {
                        localStorage.setItem(REMEMBER_SESSION_KEY, '1');
                    } else {
                        localStorage.removeItem(REMEMBER_SESSION_KEY);
                    }
                    sessionExpirationHandled = false;
                    return true;
                } catch (_error) {
                    return false;
                }
            });
            try {
                return await refreshPromise;
            } finally {
                refreshPromise = null;
            }
        },

        reset() {
            this.objects = {};
            this.objectTypes = [];
            this.objectsLoaded = false;
            this.forms = {};
            this.formCategories = [];
        },

        async loadStateFromLocalStorage() {
            this.configureSessionHandling();
            let token = sessionStorage.getItem(ACCESS_TOKEN_KEY);
            const legacyToken = localStorage.getItem(LEGACY_TOKEN_KEY);
            if (!token && legacyToken) {
                token = legacyToken;
                sessionStorage.setItem(ACCESS_TOKEN_KEY, legacyToken);
                localStorage.removeItem(LEGACY_TOKEN_KEY);
            }

            if (token) {
                this.storeAccessToken(token);
                try {
                    if (await this.tryLoadProfile()) {
                        sessionExpirationHandled = false;
                        return true;
                    }
                } catch (_error) {
                    this.clearSessionState();
                    this.setAuthMessage('Не удалось проверить сессию. Попробуйте войти снова.');
                    return false;
                }
            }

            if (hasRefreshSession() && await this.refreshAccessToken()) {
                try {
                    if (await this.tryLoadProfile()) return true;
                } catch (_error) {
                    this.clearSessionState();
                    this.setAuthMessage('Не удалось проверить сессию. Попробуйте войти снова.');
                    return false;
                }
            }

            if (token || hasRefreshSession() || localStorage.getItem(REMEMBER_SESSION_KEY)) {
                this.expireSession();
            }
            return false;
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
