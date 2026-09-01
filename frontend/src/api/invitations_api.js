// src/api/invitations_api.js
import api_client from "@/api/client.js";

/**
 * Получение списка инвайтов
 */
export async function getInvitations() {
  return await api_client.fetch("/invitations", {
      method: "GET"
    });
}

/**
 * Создание инвайтов
 * @param {string} typeCode - тип создаваемых инвайтов (например, "generic")
 * @param {string} role - роль, которую привязываем к инвайтам
 */
export async function createInvitations(typeCode, role) {
    // Формируем данные для POST-запроса
    const payload = {
        role: role,
    };

  return await api_client.fetch(`/invitations/${typeCode}/create`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
}

export async function createInvitationForObject(objectId) {
    return await api_client.fetch(`/invitations/objects/${objectId}`, {
        method: "POST",
    });
}

export async function deleteInvitation(invitationId) {
    return await api_client.fetch(`/invitations/${invitationId}`, {
        method: "DELETE",
    });
}

export async function deleteAllInvitations() {
    return await api_client.fetch("/invitations", {
        method: "DELETE",
    });
}
