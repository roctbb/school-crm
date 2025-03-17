// forms_api.js

import api_client from './client.js';

// Получение всех форм
export async function fetchForms() {
    return await api_client.fetch('/forms', {
        method: 'GET',
    });
}

// Получение всех категорий форм
export async function fetchFormCategories() {
    return await api_client.fetch('/forms/categories', {
        method: 'GET',
    });
}

// Создание новой формы в заданной категории
export async function createForm(categoryId, data) {
    return await api_client.fetch(`/forms/categories/${categoryId}`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// Получение подробной информации о форме
export async function fetchFormDetails(formId) {
    return await api_client.fetch(`/forms/${formId}`, {
        method: 'GET',
    });
}

export async function fetchFormSubmissions(formId) {
    return await api_client.fetch(`/forms/${formId}/submissions`, {
        method: 'GET',
    });
}

// Обновление формы
export async function updateForm(formId, data) {
    return await api_client.fetch(`/forms/${formId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

// Удаление формы
export async function deleteForm(formId) {
    return await api_client.fetch(`/forms/${formId}`, {
        method: 'DELETE',
    });
}

