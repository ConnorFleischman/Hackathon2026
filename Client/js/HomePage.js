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
    const profileChip = document.getElementById("profileChip");
    const feedCount = document.getElementById("feedCount");
    const { escapeHtml, formatDateTime, formatRelativeTime, getInitials, setStatus } = window.ChatMuch;

    function renderFeed(posts) {
        feedContainer.innerHTML = "";
        feedCount.textContent = String(posts.length);

        if (!posts.length) {
            feedContainer.innerHTML = `
                <div class="feed-empty">
                    No campus posts yet. Be the first person to start the conversation.
                </div>
            `;
            return;
        }

        posts.forEach((post) => {
            const card = document.createElement("article");
            card.className = "feed-card";
            card.innerHTML = `
                <div class="feed-card-header">
                    <div class="user-chip">
                        <div class="avatar">${getInitials("Campus Member")}</div>
                        <div>
                            <strong>Campus member</strong>
                            <div class="feed-meta">Posted ${formatRelativeTime(post.created_at)}</div>
                        </div>
                    </div>
                    <span class="feed-badge">Live feed</span>
                </div>
                <p class="feed-body">${escapeHtml(post.body)}</p>
                <div class="feed-card-footer">
                    <span>Created ${formatDateTime(post.created_at)}</span>
                    <span>Expires ${formatRelativeTime(post.expires_at)}</span>
                </div>
            `;
            feedContainer.appendChild(card);
        });
    }

    async function loadCurrentUser() {
        const user = await window.ChatMuch.apiRequest("/auth/me");
        const displayName = user.display_name || user.username;
        userSummary.textContent = `Signed in as ${displayName} (${user.email})`;
        profileChip.innerHTML = `
            <div class="avatar">${getInitials(displayName)}</div>
            <div>
                <strong>${escapeHtml(displayName)}</strong>
                <span class="muted-text">${escapeHtml(user.email)}</span>
            </div>
        `;

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
            feedStatus.textContent = posts.length === 1 ? "1 post loaded" : `${posts.length} posts loaded`;
        } catch (error) {
            feedStatus.textContent = error.message;
            feedCount.textContent = "0";
        }
    }

    postForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        setStatus(composerStatus, "Publishing your post...", "info");

        try {
            await window.ChatMuch.apiRequest("/posts", {
                method: "POST",
                body: JSON.stringify({ body: postBody.value }),
            });
            postBody.value = "";
            setStatus(composerStatus, "Post published.", "success");
            await loadFeed();
        } catch (error) {
            setStatus(composerStatus, error.message, "error");
        }
    });

    logoutButton.addEventListener("click", () => {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    });

    try {
        await loadCurrentUser();
        await loadFeed();
        setStatus(composerStatus, "", "info");
    } catch (error) {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    }
});