// src/api/files_api.js
import api_client from './client.js';
import {API_URL} from "@/api/common.js";  // предполагается, что client.js уже есть

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