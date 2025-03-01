const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8081/api";

class ApiError extends Error {
    constructor(message, code, field) {
        super(message);

        this.name = 'ApiError';
        this.code = code
        this.field = field;

        if (!this.code) {
            this.code = 500;
        }
    }
}

async function validateResponse(response) {
    if (!response.ok) {
        let message = 'Unknown error';
        let code = response.status;
        let field = null;

        try {
            let data = await response.json(); // Используем await для получения данных
            message = data.message || message; // Безопасно проверяем message
            field = data.field || field; // Безопасно проверяем field
        } catch (e) {
            console.error('Ошибка парсинга JSON:', e); // Логируем ошибку
        }
        throw new ApiError(message, code, field);
    }
}

export {ApiError, validateResponse, API_URL};