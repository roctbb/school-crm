import api_client from './client.js';

export async function fetchObjectTypes() {
    return await api_client.fetch(`/objects/types`, {
        method: "GET"
    });
}

export async function fetchObjectsByType(objectTypeCode) {
    return await api_client.fetch(`/objects/${objectTypeCode}`, {
        method: "GET",
    });
}

export async function fetchObjects() {
    return await api_client.fetch(`/objects`, {
        method: "GET",
    });
}

export async function createObject(objectTypeCode, data) {
    return await api_client.fetch(`/objects/${objectTypeCode}/create`, {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function updateObject(objectId, data) {
    return await api_client.fetch(`/objects/${objectId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function updateObjectChildren(objectId, children_ids) {
    return await api_client.fetch(`/objects/${objectId}/children`, {
        method: "PUT",
        body: JSON.stringify({children: children_ids}),
    });
}

export async function deleteObject(objectId) {
    return await api_client.fetch(`/objects/${objectId}`, {
        method: "DELETE",
    });
}

export async function fetchObjectDetails(objectId) {
    return await api_client.fetch(`/objects/${objectId}`, {
        method: "GET",
    });
}

export async function postComment(objectId, comment) {
    return await api_client.fetch(`/objects/${objectId}/comments`, {
        method: "POST",
        body: JSON.stringify({text: comment}),
    });
}

export async function deleteComment(objectId, commentId) {
    return await api_client.fetch(`/objects/${objectId}/comments/${commentId}`, {
        method: "DELETE",
    });
}