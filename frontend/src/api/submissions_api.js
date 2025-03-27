// submissions.js

import api_client from './client.js';

export async function createSubmission(objectId, formId, data) {
    return await api_client.fetch(`/objects/${objectId}/forms/${formId}`, {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function updateSubmission(objectId, submissionId, data) {
    return await api_client.fetch(`/objects/${objectId}/submissions/${submissionId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function deleteSubmission(objectId, submissionId) {
    return await api_client.fetch(`/objects/${objectId}/submissions/${submissionId}`, {
        method: "DELETE",
    });
}

export async function fetchObjectSubmissions(objectId) {
    return await api_client.fetch(`/objects/${objectId}/submissions`, {
        method: "GET"
    });
}

export async function approveSubmission(objectId, submissionId) {
    return await api_client.fetch(`/objects/${objectId}/submissions/${submissionId}/approve`, {
        method: "POST"
    });
}

export async function restoreSubmission(objectId, submissionId) {
    return await api_client.fetch(`/objects/${objectId}/submissions/${submissionId}/restore`, {
        method: "POST"
    });
}