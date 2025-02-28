// src/api/objects.js
import {validateResponse, API_URL} from './common'; // Utility helpers (например, validateResponse)


export async function fetchObjectTypes(token) {
    const response = await fetch(`${API_URL}/objects/`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    await validateResponse(response); // Проверяем ответ через общую функцию в common.js
    return await response.json();
}

export async function fetchObjectsByType(objectTypeCode, token) {
    const response = await fetch(`${API_URL}/objects/${objectTypeCode}/`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    await validateResponse(response);
    return await response.json();
}

export async function createNewObject(data, objectTypeCode, token) {
    const response = await fetch(`${API_URL}/objects/${objectTypeCode}/create`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
    });
    await validateResponse(response);
    return await response.json();
}

export async function fetchObjectDetails(objectType, objectId, token) {
    const response = await fetch(`${API_URL}/objects/${objectType}/${objectId}`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    await validateResponse(response);
    return await response.json();
}