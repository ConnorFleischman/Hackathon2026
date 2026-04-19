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

    function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, (character) => (
            {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;",
            }[character]
        ));
    }

    function getInitials(value) {
        return (value || "CM")
            .split(/\s+/)
            .filter(Boolean)
            .slice(0, 2)
            .map((part) => part[0].toUpperCase())
            .join("") || "CM";
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

    function formatRelativeTime(value) {
        const targetDate = new Date(value);
        const diffMs = targetDate.getTime() - Date.now();
        const absoluteMinutes = Math.round(Math.abs(diffMs) / 60000);

        if (absoluteMinutes < 1) {
            return diffMs >= 0 ? "in a moment" : "just now";
        }

        const units = [
            { limit: 60, divisor: 1, label: "minute" },
            { limit: 1440, divisor: 60, label: "hour" },
            { limit: 10080, divisor: 1440, label: "day" },
        ];

        for (const unit of units) {
            if (absoluteMinutes < unit.limit) {
                const amount = Math.round(absoluteMinutes / unit.divisor);
                return diffMs >= 0
                    ? `in ${amount} ${unit.label}${amount === 1 ? "" : "s"}`
                    : `${amount} ${unit.label}${amount === 1 ? "" : "s"} ago`;
            }
        }

        const amount = Math.round(absoluteMinutes / 10080);
        return diffMs >= 0
            ? `in ${amount} week${amount === 1 ? "" : "s"}`
            : `${amount} week${amount === 1 ? "" : "s"} ago`;
    }

    function setStatus(element, message, tone = "info") {
        if (!element) {
            return;
        }

        element.textContent = message || "";
        element.className = "status-pill";

        if (message) {
            element.classList.add("has-status", `is-${tone}`);
        }
    }

    window.ChatMuch = {
        apiRequest,
        clearAuthSession,
        escapeHtml,
        formatDateTime,
        formatRelativeTime,
        getInitials,
        loadAuthSession,
        requireAuthSession,
        setStatus,
        saveAuthSession,
    };
})();
