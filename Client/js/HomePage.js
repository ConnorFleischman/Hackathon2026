document.addEventListener("DOMContentLoaded", async () => {
    const session = window.ChatMuch.requireAuthSession();
    if (!session) {
        return;
    }

    const userSummary = document.getElementById("userSummary");
    const feedStatus = document.getElementById("feedStatus");
    const feedContainer = document.getElementById("feed");
    const composerStatus = document.getElementById("composerStatus");
    const postForm = document.getElementById("postForm");
    const postBody = document.getElementById("postBody");
    const logoutButton = document.getElementById("logoutButton");

    function renderFeed(posts) {
        feedContainer.innerHTML = "";

        if (!posts.length) {
            feedContainer.innerHTML = "<p>No campus posts yet. Be the first to share something.</p>";
            return;
        }

        posts.forEach((post) => {
            const card = document.createElement("article");
            card.className = "feed-card";
            card.innerHTML = `
                <p>${post.body}</p>
                <small>Posted ${window.ChatMuch.formatDateTime(post.created_at)}</small>
            `;
            feedContainer.appendChild(card);
        });
    }

    async function loadCurrentUser() {
        const user = await window.ChatMuch.apiRequest("/auth/me");
        const displayName = user.display_name || user.username;
        userSummary.textContent = `Signed in as ${displayName} (${user.email})`;

        const updatedSession = window.ChatMuch.loadAuthSession() || {};
        window.ChatMuch.saveAuthSession({
            ...updatedSession,
            user,
        });
    }

    async function loadFeed() {
        feedStatus.textContent = "Loading feed...";
        try {
            const posts = await window.ChatMuch.apiRequest("/feed");
            renderFeed(posts);
            feedStatus.textContent = `${posts.length} post(s) loaded`;
        } catch (error) {
            feedStatus.textContent = error.message;
        }
    }

    postForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        composerStatus.textContent = "Posting...";

        try {
            await window.ChatMuch.apiRequest("/posts", {
                method: "POST",
                body: JSON.stringify({ body: postBody.value }),
            });
            postBody.value = "";
            composerStatus.textContent = "Post published.";
            await loadFeed();
        } catch (error) {
            composerStatus.textContent = error.message;
        }
    });

    logoutButton.addEventListener("click", () => {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    });

    try {
        await loadCurrentUser();
        await loadFeed();
    } catch (error) {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    }
});