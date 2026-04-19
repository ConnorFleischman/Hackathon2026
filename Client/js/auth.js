document.addEventListener("DOMContentLoaded", () => {
    const session = window.ChatMuch.loadAuthSession();
    if (session && session.access_token) {
        window.location.href = "/Homepage.html";
        return;
    }

    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const campusSelect = document.getElementById("registerCampus");
    const loginStatus = document.getElementById("loginStatus");
    const registerStatus = document.getElementById("registerStatus");
    const { setStatus } = window.ChatMuch;

    async function loadCampuses() {
        campusSelect.innerHTML = '<option value="">Loading campuses...</option>';
        setStatus(registerStatus, "Loading campus list...", "info");

        try {
            const campuses = await window.ChatMuch.apiRequest("/campuses");
            campusSelect.innerHTML = '<option value="">Select a campus</option>';

            campuses.forEach((campus) => {
                const option = document.createElement("option");
                option.value = campus.id;
                option.textContent = campus.name;
                campusSelect.appendChild(option);
            });
            setStatus(registerStatus, "", "info");
        } catch (error) {
            campusSelect.innerHTML = '<option value="">Unable to load campuses</option>';
            setStatus(registerStatus, error.message, "error");
        }
    }

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        setStatus(loginStatus, "Signing in...", "info");

        const payload = {
            email: document.getElementById("loginEmail").value,
            password: document.getElementById("loginPassword").value,
        };

        try {
            const sessionData = await window.ChatMuch.apiRequest("/auth/login", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            window.ChatMuch.saveAuthSession(sessionData);
            setStatus(loginStatus, "Signed in. Opening your feed...", "success");
            window.location.href = "/Homepage.html";
        } catch (error) {
            setStatus(loginStatus, error.message, "error");
        }
    });

    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        setStatus(registerStatus, "Creating account...", "info");

        const payload = {
            email: document.getElementById("registerEmail").value,
            username: document.getElementById("registerUsername").value,
            display_name: document.getElementById("registerDisplayName").value,
            campus_id: campusSelect.value,
            password: document.getElementById("registerPassword").value,
        };

        try {
            const sessionData = await window.ChatMuch.apiRequest("/auth/register", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            window.ChatMuch.saveAuthSession(sessionData);
            setStatus(registerStatus, "Account created. Opening your feed...", "success");
            window.location.href = "/Homepage.html";
        } catch (error) {
            setStatus(registerStatus, error.message, "error");
        }
    });

    loadCampuses();
});
