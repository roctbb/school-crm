import api_client from '@/api/client.js';


export async function fetchUsers() {
    return api_client.fetch('/users', {method: 'GET'});
}


export async function generatePasswordResetLink(userId) {
    return api_client.fetch(`/users/${userId}/password-reset-link`, {method: 'POST'});
}
