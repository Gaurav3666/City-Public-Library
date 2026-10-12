
const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(path, options = {}) {
    const headers = { ...(options.headers || {}) };

    if (options.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(API_BASE_URL + path, {
        ...options,
        headers,
        credentials: "include"
    });

    const text = await response.text();
    let data = {};

    try {
        data = text ? JSON.parse(text) : {};
    } catch {
        data = { message: text };
    }

    if (!response.ok) {
        const detail = data.detail;
        const message = typeof detail === "string"
            ? detail
            : detail?.message || data.message || `Request failed (${response.status})`;

        throw new Error(message);
    }

    return data;
}

function showMessage(element, text, type = "error") {
    element.textContent = text;
    element.className = `message ${type}`;
}

function getToken() {
    return sessionStorage.getItem("member_token");
}

function saveToken(token) {
    sessionStorage.setItem("member_token", token);
}

function clearToken() {
    sessionStorage.removeItem("member_token");
}

async function memberRequest(path, options = {}) {
    const token = getToken();

    if (!token) {
        throw new Error("Please log in as a member first.");
    }

    return apiRequest(path, {
        ...options,
        headers: {
            ...(options.headers || {}),
            Authorization: `Bearer ${token}`
        }
    });
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function formatDate(value) {
    if (!value) return "—";

    const date = new Date(`${value.slice(0, 10)}T00:00:00`);

    return Number.isNaN(date.getTime())
        ? value
        : date.toLocaleDateString();
}
