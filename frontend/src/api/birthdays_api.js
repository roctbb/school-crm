import apiClient from './client.js';
import {API_URL, validateResponse} from './common.js';

const photoBlobs = new Map();

export function birthdayDisplaySettings(method = 'GET') {
    return apiClient.fetch('/settings/birthday-display', {method});
}

// A separate client keeps the unattended display independent of CRM sessions
// and avoids the global loading overlay during background updates.
export async function fetchBirthdayResource(path, key, signal, photo = false) {
    const response = await fetch(`${API_URL}${path}`, {
        headers: {'X-Birthday-Key': key},
        credentials: 'omit',
        cache: 'no-store',
        referrerPolicy: 'no-referrer',
        signal,
    });
    await validateResponse(response);
    return photo ? response.blob() : response.json();
}

// Photos are kept in memory only (responses stay no-store), so page turns and
// refreshes reuse them. Photo paths are versioned, a replaced photo is a new entry.
export function fetchBirthdayPhoto(path, key) {
    const cacheKey = `${key}\n${path}`;
    let pendingBlob = photoBlobs.get(cacheKey);

    if (!pendingBlob) {
        const request = new AbortController();
        const timeout = window.setTimeout(() => request.abort(), 15000);
        pendingBlob = fetchBirthdayResource(path, key, request.signal, true).catch(error => {
            if (photoBlobs.get(cacheKey) === pendingBlob) photoBlobs.delete(cacheKey);
            throw error;
        }).finally(() => window.clearTimeout(timeout));
        photoBlobs.set(cacheKey, pendingBlob);
    }

    return pendingBlob;
}

// The display runs unattended for weeks: drop photos of students no longer listed.
export function retainBirthdayPhotos(paths, key) {
    const retained = new Set(paths.map(path => `${key}\n${path}`));
    for (const cacheKey of photoBlobs.keys()) {
        if (!retained.has(cacheKey)) photoBlobs.delete(cacheKey);
    }
}
