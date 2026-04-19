document.addEventListener("DOMContentLoaded", async () => {
    const session = window.ChatMuch.requireAuthSession();
    if (!session) {
        return;
    }

    const logoutButton = document.getElementById("logoutButton");
    const profileSummary = document.getElementById("profileSummary");
    const messagesStatus = document.getElementById("messagesStatus");

    logoutButton.addEventListener("click", () => {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    });

    try {
        const user = await window.ChatMuch.apiRequest("/auth/me");
        profileSummary.textContent = `${user.display_name || user.username} is connected to the backend.`;
        messagesStatus.textContent =
            "Direct messaging is not implemented in the current backend yet, so this page is a safe placeholder instead of a broken API call.";
    } catch (error) {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    }
});