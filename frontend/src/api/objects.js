// src/api/objects.js
const API_URL = '/api';

export async function fetchObjectTypes(token) {
    const response = await fetch(`${API_URL}/objects`, {
        method: 'GET',
        headers: {Authorization: `Bearer ${token}`},
    });
    if (!response.ok) throw new Error('Failed to fetch object types');
    return response.json();
}