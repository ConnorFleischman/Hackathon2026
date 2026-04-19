document.addEventListener("DOMContentLoaded", async () => {
    const session = window.ChatMuch.requireAuthSession();
    if (!session) {
        return;
    }

    const logoutButton = document.getElementById("logoutButton");
    const profileSummary = document.getElementById("profileSummary");
    const messagesStatus = document.getElementById("messagesStatus");
    const { setStatus } = window.ChatMuch;

    logoutButton.addEventListener("click", () => {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    });

    try {
        const user = await window.ChatMuch.apiRequest("/auth/me");
        profileSummary.textContent = `${user.display_name || user.username} is connected and ready for future inbox features.`;
        setStatus(
            messagesStatus,
            "Direct messaging is not implemented in the backend yet, so this page stays polished without making a broken API request.",
            "info",
        );
    } catch (error) {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    }
});