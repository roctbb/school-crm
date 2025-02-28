import {defineStore} from "pinia";
import {getProfile} from "@/api/auth.js";

// Создаём хранилище
const useMainStore = defineStore("mainStore", {
    // Состояние
    state: () => ({
        token: null,
        profile: null,
        objects: [],
    }),

    actions: {
        async tryLoadProfile() {
            try {
                console.log("Trying to load profile with token:", this.token)
                this.profile = await getProfile(this.token)
                console.log("Loaded")
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
            localStorage.clear();
        },

        loadStateFromLocalStorage() {
            const token = localStorage.getItem("token");

            if (token) {
                this.token = token;
            }
        },

    },
});

export default useMainStore;