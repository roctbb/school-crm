import api_client from '@/api/client.js';


export async function fetchTelegramSettings() {
    return api_client.fetch('/settings/notifications/telegram', {method: 'GET'});
}


export async function createTelegramLink() {
    return api_client.fetch('/settings/notifications/telegram/link', {method: 'POST'});
}


export async function disconnectTelegram() {
    return api_client.fetch('/settings/notifications/telegram', {method: 'DELETE'});
}
