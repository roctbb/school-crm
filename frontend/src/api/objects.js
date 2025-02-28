// src/api/objects.js
import {validateResponse, API_URL} from './common';

export async function fetchObjectTypes(token) {
    const response = await fetch(`${API_URL}/objects`, {
        method: 'GET',
        headers: {Authorization: `Bearer ${token}`},
    });
    await validateResponse(response);
    return response.json();
}