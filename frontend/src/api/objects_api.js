import api_client from './client.js';

export async function fetchObjectTypes() {
    return await api_client.fetch(`/objects/types`, {
        method: "GET"
    });
}

export async function createObjectType(data) {
    return await api_client.fetch('/objects/types', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function updateObjectType(objectTypeId, data) {
    return await api_client.fetch(`/objects/types/${objectTypeId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

export async function fetchObjectTypeUsage(objectTypeId) {
    return await api_client.fetch(`/objects/types/${objectTypeId}/usage`, {
        method: 'GET',
    });
}

export async function fetchObjectTypeRevisions(objectTypeId) {
    return await api_client.fetch(`/objects/types/${objectTypeId}/revisions`, {
        method: 'GET',
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

export async function deleteObjectChild(objectId, childId) {
    return await api_client.fetch(`/objects/${objectId}/children/${childId}`, {
        method: "DELETE",
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

export async function approveObject(objectId) {
    return await api_client.fetch(`/objects/${objectId}/approve`, {
        method: "POST"
    });
}

export async function restoreObject(objectId) {
    return await api_client.fetch(`/objects/${objectId}/restore`, {
        method: "POST"
    });
}
