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

    async function loadCampuses() {
        campusSelect.innerHTML = '<option value="">Loading campuses...</option>';

        try {
            const campuses = await window.ChatMuch.apiRequest("/campuses");
            campusSelect.innerHTML = '<option value="">Select a campus</option>';

            campuses.forEach((campus) => {
                const option = document.createElement("option");
                option.value = campus.id;
                option.textContent = campus.name;
                campusSelect.appendChild(option);
            });
        } catch (error) {
            campusSelect.innerHTML = '<option value="">Unable to load campuses</option>';
            registerStatus.textContent = error.message;
        }
    }

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        loginStatus.textContent = "Signing in...";

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
            window.location.href = "/Homepage.html";
        } catch (error) {
            loginStatus.textContent = error.message;
        }
    });

    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        registerStatus.textContent = "Creating account...";

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
            window.location.href = "/Homepage.html";
        } catch (error) {
            registerStatus.textContent = error.message;
        }
    });

    loadCampuses();
});
