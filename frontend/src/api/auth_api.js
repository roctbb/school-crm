// src/api/auth_api.js
import {API_URL, validateResponse} from './common.js';
import api_client from './client.js';

const REFRESH_CSRF_COOKIE = 'crm_refresh_csrf';

function getCookie(name) {
    const prefix = `${encodeURIComponent(name)}=`;
    const item = document.cookie.split('; ').find(cookie => cookie.startsWith(prefix));
    return item ? decodeURIComponent(item.slice(prefix.length)) : null;
}

async function sessionRequest(path) {
    const csrfToken = getCookie(REFRESH_CSRF_COOKIE);
    const headers = csrfToken ? {'X-CSRF-TOKEN': csrfToken} : {};
    const response = await fetch(API_URL + path, {
        method: 'POST',
        credentials: 'include',
        headers,
    });
    await validateResponse(response);
    return response.json();
}

export async function login(email, password, rememberMe = false) {
    return await api_client.fetch(`/login`, {
        method: 'POST',
        body: JSON.stringify({email, password, remember_me: rememberMe}),
        withAuth: false,
        retryAuth: false,
        credentials: 'include',
    });
}

export async function refreshSession() {
    return await sessionRequest('/refresh');
}

export async function logoutSession() {
    return await sessionRequest('/logout');
}

export async function register({name, email, password, invite}) {
    return await api_client.fetch(`/signup`, {
        method: 'POST',
        body: JSON.stringify({name, email, password, invite}),
    });
}

export async function getProfile(token) {
    return await api_client.fetch(`/me`, {
        method: 'GET'
    });
}

export async function sendPasswordResetEmail(email) {
    return await api_client.fetch(`/password/email`, {
        method: 'POST',
        body: JSON.stringify({email: email}),
    });
}

export async function resetPassword({token, password}) {
    return await api_client.fetch(`/password/reset`, {
        method: 'POST',
        body: JSON.stringify({reset_token: token, password: password}),
    });
}
