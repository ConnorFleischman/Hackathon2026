document.addEventListener("DOMContentLoaded", async () => {
    const session = window.ChatMuch.requireAuthSession();
    if (!session) {
        return;
    }

    const logoutButton = document.getElementById("logoutButton");
    const profileSummary = document.getElementById("profileSummary");
    const profileCard = document.getElementById("profileCard");
    const profileDetails = document.getElementById("profileDetails");
    const myPosts = document.getElementById("myPosts");
    const profilePostsStatus = document.getElementById("profilePostsStatus");
    const profilePostCount = document.getElementById("profilePostCount");
    const profileStatusValue = document.getElementById("profileStatusValue");
    const { escapeHtml, formatDateTime, formatRelativeTime, getInitials } = window.ChatMuch;

    logoutButton.addEventListener("click", () => {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    });

    function renderProfile(user) {
        const displayName = user.display_name || user.username;
        profileSummary.textContent = `${displayName} is signed in and connected to the campus network.`;
        profileStatusValue.textContent = user.status.replace(/_/g, " ");
        profileCard.innerHTML = `
            <div class="user-chip">
                <div class="avatar">${getInitials(displayName)}</div>
                <div>
                    <strong>${escapeHtml(displayName)}</strong>
                    <span class="muted-text">@${escapeHtml(user.username)}</span>
                </div>
            </div>
        `;

        const details = [
            { label: "Email", value: user.email },
            { label: "Username", value: `@${user.username}` },
            { label: "Display name", value: user.display_name || "Not set" },
            { label: "Campus ID", value: user.campus_id || "No campus assigned" },
            { label: "Role", value: user.role.replace(/_/g, " ") },
            { label: "Status", value: user.status.replace(/_/g, " ") },
        ];

        profileDetails.innerHTML = details
            .map((detail) => `
                <div class="detail-row">
                    <span class="detail-label">${escapeHtml(detail.label)}</span>
                    <strong>${escapeHtml(detail.value)}</strong>
                </div>
            `)
            .join("");
    }

    function renderPosts(posts) {
        profilePostCount.textContent = String(posts.length);

        if (!posts.length) {
            myPosts.innerHTML = `
                <div class="feed-empty">
                    You have not published any visible campus posts yet.
                </div>
            `;
            return;
        }

        myPosts.innerHTML = "";
        posts.forEach((post) => {
            const card = document.createElement("article");
            card.className = "feed-card";
            card.innerHTML = `
                <div class="feed-card-header">
                    <div>
                        <strong>Your post</strong>
                        <div class="feed-meta">Posted ${formatRelativeTime(post.created_at)}</div>
                    </div>
                    <span class="feed-badge">Profile view</span>
                </div>
                <p class="feed-body">${escapeHtml(post.body)}</p>
                <div class="feed-card-footer">
                    <span>Created ${formatDateTime(post.created_at)}</span>
                    <span>Expires ${formatRelativeTime(post.expires_at)}</span>
                </div>
            `;
            myPosts.appendChild(card);
        });
    }

    try {
        const user = await window.ChatMuch.apiRequest("/auth/me");
        renderProfile(user);

        const posts = await window.ChatMuch.apiRequest("/feed");
        const myVisiblePosts = posts.filter((post) => post.user_id === user.id);
        renderPosts(myVisiblePosts);
        profilePostsStatus.textContent =
            myVisiblePosts.length === 1 ? "1 visible post" : `${myVisiblePosts.length} visible posts`;
    } catch (error) {
        window.ChatMuch.clearAuthSession();
        window.location.href = "/login.html";
    }
});