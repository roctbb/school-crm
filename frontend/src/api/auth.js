// src/api/auth.js
import {validateResponse, API_URL} from './common.js';

export async function login(email, password) {
    const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password}),
    });
    await validateResponse(response);
    return (await response.json()).access_token;
}

export async function register({name, email, password, invite}) {
    const response = await fetch(`${API_URL}/signup`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, password, invite}),
    });
    await validateResponse(response);
    console.log(response)
    return response.json();
}

export async function getProfile(token) {
    const response = await fetch(`${API_URL}/me`, {
        method: 'GET',
        headers: {Authorization: `Bearer ${token}`},
    });
    await validateResponse(response);
    return response.json();
}