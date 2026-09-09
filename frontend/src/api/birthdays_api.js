import apiClient from './client.js';
import {API_URL, validateResponse} from './common.js';

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
