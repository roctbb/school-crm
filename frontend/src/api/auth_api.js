// src/api/auth_api.js
import {API_URL} from './common.js';
import api_client from './client.js';

export async function login(email, password) {
    return (await api_client.fetch(`/login`, {
        method: 'POST',
        body: JSON.stringify({email, password}),
    })).access_token;
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