import {API_URL, validateResponse} from './common.js';
import {finishRequestLoading, startRequestLoading} from '@/services/globalLoading.js';

class ApiClient {
    constructor(token = null) {
        this.token = token;
    }

    setToken(token) {
        this.token = token;
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
        let headers = options.headers

        if (contentType) {
            headers = {
                ...headers,
                'Content-Type': contentType
            }
        }
        if (this.token) {
            headers = {
                ...headers,
                ...this.getAuthorizationHeaders(),
            };
        }

        startRequestLoading();
        try {
            const response = await fetch(API_URL + url, {...options, headers});
            await validateResponse(response);
            return response.json();
        } finally {
            finishRequestLoading();
        }
    }
}

let api_client = new ApiClient();

export default api_client;
