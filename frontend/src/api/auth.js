// src/api/auth.js
const API_URL = '/api';

export async function login(email, password) {
    const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password}),
    });
    if (!response.ok) throw new Error('Login failed');
    return response.json();
}

export async function register({name, email, password, invite}) {
    const response = await fetch(`${API_URL}/signup`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, password, invite}),
    });
    if (!response.ok) throw new Error('Registration failed');
    return response.json();
}