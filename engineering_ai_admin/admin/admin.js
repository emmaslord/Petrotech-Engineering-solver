
"use strict";

(async function initializeAdminDashboard() {
   const API_BASE_URL_URL = "https://engineeringai.onrender.com";
   const API_BASE_URL = API_BASE_URL_URL;
    
    const notice = document.getElementById("admin-notice");
    const usersBody = document.getElementById("users-table-body");
    const usersCount = document.getElementById("users-count");
    const refreshButton = document.getElementById("refresh-users");
    const usersMessage = document.getElementById("users-message");

   const activityBody = document.getElementById("activity-table-body");
   const activityMessage = document.getElementById("activity-message");
   const refreshActivityButton = document.getElementById("refresh-activity");
   
    const apiStatus = document.getElementById("api-status");
    const databaseStatus = document.getElementById("database-status");
    const healthApiStatus = document.getElementById("health-api-status");
    const healthDatabaseStatus = document.getElementById("health-database-status");

    
    function showNotice(message, isError = false) {
        if (!notice) return;
        notice.hidden = false;
        notice.textContent = message;
        notice.dataset.type = isError ? "error" : "info";
    }

    function showUsersMessage(message) {
        if (usersMessage) usersMessage.textContent = message;
    }

    function addCell(row, value) {
        const cell = document.createElement("td");
        cell.textContent = value || "—";
        row.appendChild(cell);
    }

    function formatDate(value) {
        if (!value) return "Never";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "—";
        return date.toLocaleString();
    }

    function renderUsers(users) {
        if (!usersBody) return;
        usersBody.replaceChildren();

        if (!Array.isArray(users) || users.length === 0) {
            showUsersMessage("No registered users found.");
            return;
        }

        showUsersMessage("");

        for (const user of users) {
            const row = document.createElement("tr");
            addCell(row, user.email);
            addCell(row, formatDate(user.created_at));
            addCell(row, formatDate(user.last_sign_in_at));
            addCell(row, user.email_confirmed_at ? "Confirmed" : "Not confirmed");
            usersBody.appendChild(row);
        }
    }

    function setStatus(element, value) {
        if (!element) return;
        element.textContent = value;
        element.className = value === "Online" ? "online" : "pending";
    }

    try {
        showNotice("Checking administrator access…");

        const configResponse = await fetch(`${API_BASE_URL_URL}/api/config`);
        if (!configResponse.ok) {
            throw new Error("Could not load application configuration.");
        }

        const config = await configResponse.json();
        if (!config.success || !config.supabaseUrl || !config.supabaseKey) {
            throw new Error("Supabase configuration is unavailable.");
        }

        if (!window.supabase?.createClient) {
            throw new Error("Supabase browser library is not loaded.");
        }

        const supabase = window.supabase.createClient(
            config.supabaseUrl,
            config.supabaseKey
        );

        async function getAccessToken() {
            const { data, error } = await supabase.auth.getSession();
            if (error) throw error;
            return data?.session?.access_token || null;
        }

        async function loadUsers() {
            if (refreshButton) refreshButton.disabled = true;
            showUsersMessage("Loading registered users…");

            try {
                const token = await getAccessToken();

                if (!token) {
                    showNotice(
                        "Please sign in through the main Engineering AI app, then return here.",
                        true
                    );
                    showUsersMessage("Sign-in required.");
                    return;
                }

                const response = await fetch(`${API_BASE_URL_URL}/api/admin/users`, {
                    headers: { Authorization: `Bearer ${token}` }
                });

                const result = await response.json();

                if (response.status === 401) {
                    throw new Error("Your session expired. Sign in again.");
                }
                if (response.status === 403) {
                    throw new Error("This account does not have administrator permission.");
                }
                if (!response.ok || !result.success) {
                    throw new Error(result.error || "Unable to load users.");
                }

                renderUsers(result.users);

                if (usersCount) {
                    usersCount.textContent = String(
                        result.count ?? result.users.length
                    );
                }

const overviewUsersCount = document.getElementById(
    "overview-users-count"
);

if (overviewUsersCount) {
    overviewUsersCount.textContent = String(
        result.count ?? result.users.length
    );
}



                showNotice("Administrator access verified. User list loaded.");
            } catch (error) {
                showNotice(error.message || "Unable to load users.", true);
                showUsersMessage("User list unavailable.");
            } finally {
                if (refreshButton) refreshButton.disabled = false;
            }
        }

        async function loadSystemHealth() {
            try {
                const token = await getAccessToken();

                if (!token) {
                    ["Sign in required"].forEach(value => {
                        setStatus(apiStatus, value);
                        setStatus(healthApiStatus, value);
                    });
                    setStatus(databaseStatus, "Unknown");
                    setStatus(healthDatabaseStatus, "Unknown");
                    return;
                }

                const response = await fetch(`${API_BASE_URL}/api/admin/health`, {
                    headers: { Authorization: `Bearer ${token}` }
                });

                const result = await response.json();

                if (response.status === 401) {
                    throw new Error("Please sign in again to check system health.");
                }
                if (response.status === 403) {
                    throw new Error("Administrator permission is required for health checks.");
                }
                if (!response.ok || !result.success) {
                    throw new Error(result.error || "Health check failed.");
                }

                const api = result.api === "online" ? "Online" : "Unavailable";

                let database = "Unavailable";
                if (result.database === "online") {
                    database = "Online";
                } else if (result.database === "not_configured") {
                    database = "Not configured";
                }

                setStatus(apiStatus, api);
                setStatus(healthApiStatus, api);
                setStatus(databaseStatus, database);
                setStatus(healthDatabaseStatus, database);
            } catch (error) {
                setStatus(apiStatus, "Unavailable");
                setStatus(healthApiStatus, "Unavailable");
                setStatus(databaseStatus, "Unavailable");
                setStatus(healthDatabaseStatus, "Unavailable");
                console.error("System health check failed:", error);
            }
        }

        if (refreshButton) {
            refreshButton.addEventListener("click", loadUsers);
        }

if (refreshActivityButton) {
    refreshActivityButton.addEventListener("click", loadSystemActivity);
}

async function loadSystemActivity() {
    if (refreshActivityButton) {
        refreshActivityButton.disabled = true;
    }

    if (activityMessage) {
        activityMessage.textContent = "Loading recent activity…";
    }

    try {
        const token = await getAccessToken();

        if (!token) {
            throw new Error("Sign in to view system activity.");
        }

        
const response = await fetch(`${API_BASE_URL_URL}/api/admin/activity`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
        const result = await response.json();

        if (response.status === 401) {
            throw new Error("Your session expired. Please sign in again.");
        }

        if (response.status === 403) {
            throw new Error("Administrator permission is required.");
        }

        if (!response.ok || !result.success) {
            throw new Error(result.error || "Unable to load system activity.");
        }

        if (!activityBody) return;

        activityBody.replaceChildren();

        const events = Array.isArray(result.activity) ? result.activity : [];

        if (events.length === 0) {
            if (activityMessage) {
                activityMessage.textContent = "No activity records found yet.";
            }
            return;
        }

        for (const event of events) {
            const row = document.createElement("tr");

            const metadata = event.metadata &&
                typeof event.metadata === "object"
                ? event.metadata
                : {};

            const details = Object.entries(metadata)
                .map(([key, value]) => `${key}: ${String(value)}`)
                .join(" · ");

            addCell(row, event.event_type);
            addCell(row, event.actor_user_id);
            addCell(row, details || "—");
            addCell(row, formatDate(event.created_at));

            activityBody.appendChild(row);
        }

        if (activityMessage) {
            activityMessage.textContent =
                `Loaded ${events.length} recent activity event(s).`;
        }
    } catch (error) {
        if (activityBody) activityBody.replaceChildren();

        if (activityMessage) {
            activityMessage.textContent =
                error.message || "Unable to load system activity.";
        }

        console.error("System activity loading failed:", error);
    } finally {
        if (refreshActivityButton) {
            refreshActivityButton.disabled = false;
        }
    }
}

        await loadUsers();
        await loadSystemHealth();
        await loadSystemActivity();
    
    
    } catch (error) {
        showNotice(error.message || "Dashboard initialization failed.", true);
        showUsersMessage("User list unavailable.");
        console.error("Admin dashboard initialization failed:", error);
    }
})();
