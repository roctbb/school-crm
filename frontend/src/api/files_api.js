// src/api/files_api.js
import api_client from './client.js';
import {API_URL, validateResponse} from "@/api/common.js";

const protectedFileBlobs = new Map();
const MAX_PROTECTED_FILE_BLOBS = 96;

export function normalizeFileUrls(value) {
    if (Array.isArray(value)) {
        return value.filter(url => typeof url === 'string' && url.length > 0);
    }
    return typeof value === 'string' && value.length > 0 ? [value] : [];
}

export function latestFileUrl(value) {
    const urls = normalizeFileUrls(value);
    return urls.length ? urls[urls.length - 1] : null;
}

function isProtectedFileUrl(fileUrl) {
    if (!fileUrl) return false;

    try {
        const target = new URL(fileUrl, window.location.origin);
        const apiBase = new URL(API_URL, window.location.origin);
        const apiPath = apiBase.pathname.replace(/\/$/, '');

        return target.origin === apiBase.origin && target.pathname.startsWith(`${apiPath}/files/`);
    } catch (_error) {
        return false;
    }
}

async function fetchProtectedFile(fileUrl) {
    const authorization = api_client.getAuthorizationHeaders().Authorization;
    const cacheKey = `${authorization}\n${fileUrl}`;
    let pendingBlob = protectedFileBlobs.get(cacheKey);

    if (!pendingBlob) {
        pendingBlob = fetch(fileUrl, {
            headers: {Authorization: authorization},
            cache: 'default',
        }).then(async response => {
            await validateResponse(response);
            return response.blob();
        }).catch(error => {
            protectedFileBlobs.delete(cacheKey);
            throw error;
        });
        protectedFileBlobs.set(cacheKey, pendingBlob);
        if (protectedFileBlobs.size > MAX_PROTECTED_FILE_BLOBS) {
            protectedFileBlobs.delete(protectedFileBlobs.keys().next().value);
        }
    }

    return pendingBlob;
}

export function clearProtectedFileCache() {
    protectedFileBlobs.clear();
}

export async function resolveFileUrl(fileUrl) {
    if (!isProtectedFileUrl(fileUrl)) {
        return fileUrl;
    }

    const blob = await fetchProtectedFile(fileUrl);
    return URL.createObjectURL(blob);
}

export async function openFile(fileUrl) {
    if (!isProtectedFileUrl(fileUrl)) {
        window.open(fileUrl, '_blank', 'noopener,noreferrer');
        return;
    }

    const target = window.open('', '_blank');
    if (target) {
        target.opener = null;
    }

    try {
        const objectUrl = await resolveFileUrl(fileUrl);
        if (target) {
            target.location.href = objectUrl;
        } else {
            const link = document.createElement('a');
            link.href = objectUrl;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.click();
        }
        window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
    } catch (error) {
        if (target) {
            target.close();
        }
        throw error;
    }
}

export async function uploadFile(file) {
    // Готовим FormData для передачи файла
    const formData = new FormData();
    formData.append('file', file);

    // Делаем POST-запрос на /files
    const response = await api_client.fetch(`/files`, {
        method: 'POST',
        body: formData
    }, '');

    return API_URL + response.path;
}
