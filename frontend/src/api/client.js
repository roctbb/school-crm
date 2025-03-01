import {API_URL, validateResponse} from './common.js';

class ApiClient {
    constructor(token = null) {
        this.token = token;
    }

    setToken(token) {
        console.log("setting token to ", token);
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

    async fetch(url, options = {}) {
        let headers = {
            ...options.headers,
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers = {
                ...headers,
                ...this.getAuthorizationHeaders(),
            };
        }

        console.log("running request to ", url , " with ", headers, " and ", options);
        const response = await fetch(API_URL + url, {...options, headers});
        await validateResponse(response);
        return response.json();
    }
}

let api_client = new ApiClient();

export default api_client;