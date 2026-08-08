import api_client from '@/api/client.js';


function queryString(params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (typeof value === 'string' && value.length) query.set(key, value);
    });
    return query.toString();
}


export async function fetchAuthorizationRequest(params) {
    return api_client.fetch(`/oauth/authorize/request?${queryString(params)}`, {method: 'GET'});
}


export async function submitAuthorizationDecision(params, decision) {
    return api_client.fetch('/oauth/authorize', {
        method: 'POST',
        body: JSON.stringify({...params, decision}),
    });
}


export async function fetchOAuthClients() {
    return api_client.fetch('/oauth/clients', {method: 'GET'});
}


export async function createOAuthClient(payload) {
    return api_client.fetch('/oauth/clients', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}


export async function updateOAuthClient(id, payload) {
    return api_client.fetch(`/oauth/clients/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
    });
}


export async function rotateOAuthClientSecret(id) {
    return api_client.fetch(`/oauth/clients/${id}/rotate-secret`, {method: 'POST'});
}


export async function fetchLogoutRedirect(params) {
    return api_client.fetch(`/oauth/logout/request?${queryString(params)}`, {method: 'GET'});
}
