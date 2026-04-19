(() => {
    const STORAGE_KEY = "chatmuch.auth";

    function resolveApiBase() {
        return `${window.location.origin}/api/v1`;
    }

    function loadAuthSession() {
        const raw = window.localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            return null;
        }

        try {
            return JSON.parse(raw);
        } catch (error) {
            window.localStorage.removeItem(STORAGE_KEY);
            return null;
        }
    }

    function saveAuthSession(session) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    }

    function clearAuthSession() {
        window.localStorage.removeItem(STORAGE_KEY);
    }

    function requireAuthSession() {
        const session = loadAuthSession();
        if (!session || !session.access_token) {
            clearAuthSession();
            window.location.href = "/login.html";
            return null;
        }

        return session;
    }

    async function parseResponse(response) {
        const contentType = response.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
            return null;
        }

        return response.json();
    }

    async function apiRequest(path, options = {}) {
        const headers = new Headers(options.headers || {});
        const session = loadAuthSession();

        if (session && session.access_token && !headers.has("Authorization")) {
            headers.set("Authorization", `Bearer ${session.access_token}`);
        }

        if (options.body && !headers.has("Content-Type")) {
            headers.set("Content-Type", "application/json");
        }

        const response = await fetch(`${resolveApiBase()}${path}`, {
            ...options,
            headers,
        });

        const payload = await parseResponse(response);
        if (!response.ok) {
            const message =
                (payload && typeof payload.detail === "string" && payload.detail) ||
                `Request failed with status ${response.status}`;
            throw new Error(message);
        }

        return payload;
    }

    function formatDateTime(value) {
        return new Date(value).toLocaleString();
    }

    window.ChatMuch = {
        apiRequest,
        clearAuthSession,
        formatDateTime,
        loadAuthSession,
        requireAuthSession,
        saveAuthSession,
    };
})();
