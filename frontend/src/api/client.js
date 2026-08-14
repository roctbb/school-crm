import {API_URL, validateResponse} from './common.js';
import {finishRequestLoading, startRequestLoading} from '@/services/globalLoading.js';

class ApiClient {
    constructor(token = null) {
        this.token = token;
        this.refreshSession = null;
        this.onSessionExpired = null;
    }

    setToken(token) {
        this.token = token;
    }

    setSessionHandlers({refreshSession, onSessionExpired}) {
        this.refreshSession = refreshSession;
        this.onSessionExpired = onSessionExpired;
    }

    getAuthorizationHeaders() {
        if (!this.token) {
            throw new Error('Token is not set. Please set the token before calling API methods.');
        }
        return {
            Authorization: `Bearer ${this.token}`,
        };
    }

    async fetch(url, options = {}, contentType = 'application/json') {
        const {
            withAuth = true,
            retryAuth = true,
            ...requestOptions
        } = options;
        const requestToken = withAuth ? this.token : null;
        let headers = requestOptions.headers;

        if (contentType) {
            headers = {
                ...headers,
                'Content-Type': contentType
            }
        }
        if (requestToken) {
            headers = {
                ...headers,
                Authorization: `Bearer ${requestToken}`,
            };
        }

        startRequestLoading();
        try {
            const response = await fetch(API_URL + url, {
                ...requestOptions,
                credentials: requestOptions.credentials || 'same-origin',
                headers,
            });
            if (response.status === 401 && requestToken && retryAuth) {
                const tokenWasAlreadyUpdated = this.token && this.token !== requestToken;
                const refreshed = tokenWasAlreadyUpdated || await this.refreshSession?.();
                if (refreshed) {
                    return await this.fetch(url, {
                        ...requestOptions,
                        withAuth,
                        retryAuth: false,
                    }, contentType);
                }
                this.onSessionExpired?.();
            }
            await validateResponse(response);
            return response.json();
        } finally {
            finishRequestLoading();
        }
    }
}

let api_client = new ApiClient();

export default api_client;
