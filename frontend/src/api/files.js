// src/api/files.js
import api_client from './client.js';  // предполагается, что client.js уже есть
import {API_URL} from './common.js';  // для удобства, если нужно

export async function uploadFile(file) {
    // Готовим FormData для передачи файла
    const formData = new FormData();
    formData.append('file', file);

    // Делаем POST-запрос на /files
    const response = await api_client.fetch(`/files`, {
        method: 'POST',
        body: formData
    }, '');

    return response.path;
}