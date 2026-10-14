
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("chatMessages");
const welcome = document.getElementById("welcome");
const sendButton = document.getElementById("sendButton");

const thinkButton = document.getElementById("thinkButton");
const searchButton = document.getElementById("searchButton");
const menuButton = document.getElementById("menuButton");
const sidebar = document.getElementById("sidebar");
const newChatButton = document.getElementById("newChatButton");

const attachButton = document.getElementById("attachButton");
const attachmentMenu = document.getElementById("attachmentMenu");
const attachmentPreview = document.getElementById("attachmentPreview");

const imageInput = document.getElementById("imageInput");
const cameraInput = document.getElementById("cameraInput");
const documentInput = document.getElementById("documentInput");

let selectedMode = "think";
let conversationHistory = [];
let selectedAttachments = [];
let currentConversationId = null;
let requestInProgress = false;

const STORAGE_KEY = "engineeringAI_conversations_v1";
let savedConversations = loadConversations();

/* -----------------------------
   Conversation storage
------------------------------ */

function loadConversations() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        const parsed = stored ? JSON.parse(stored) : [];

        if (!Array.isArray(parsed)) return [];

        return parsed.filter(conversation =>
            conversation &&
            typeof conversation.id === "string" &&
            Array.isArray(conversation.messages)
        );
    } catch (error) {
        console.warn("Could not load saved conversations:", error);
        return [];
    }
}

function saveConversations() {
    try {
        localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify(savedConversations)
        );
        return true;
    } catch (error) {
        console.error("Could not save conversations:", error);
        return false;
    }
}

function createConversation() {
    const conversation = {
        id: (crypto.randomUUID
            ? crypto.randomUUID()
            : `${Date.now()}-${Math.random().toString(36).slice(2)}`),
        title: "New conversation",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messages: []
    };

    savedConversations.unshift(conversation);
    currentConversationId = conversation.id;
    conversationHistory = [];

    saveConversations();
    renderHistory();

    return conversation;
}

function getCurrentConversation() {
    return savedConversations.find(
        conversation => conversation.id === currentConversationId
    );
}

function addToConversation(role, content) {
    let conversation = getCurrentConversation();

    if (!conversation) {
        conversation = createConversation();
    }

    conversation.messages.push({
        role,
        content,
        createdAt: new Date().toISOString()
    });

    if (role === "user" && conversation.title === "New conversation") {
        conversation.title = content.trim().slice(0, 45) ||
            "New conversation";
    }

    conversation.updatedAt = new Date().toISOString();

    // Keep the newest conversation at the top.
    savedConversations = [
        conversation,
        ...savedConversations.filter(item => item.id !== conversation.id)
    ];

    saveConversations();
    renderHistory();
}

function deleteConversation(id) {
    savedConversations = savedConversations.filter(
        conversation => conversation.id !== id
    );

    if (currentConversationId === id) {
        currentConversationId = null;
        conversationHistory = [];
        messages.replaceChildren();
        welcome.hidden = false;
    }

    saveConversations();
    renderHistory();
}

function openConversation(id) {
    const conversation = savedConversations.find(
        item => item.id === id
    );

    if (!conversation) return;

    currentConversationId = conversation.id;

    conversationHistory = conversation.messages
        .filter(message =>
            (message.role === "user" || message.role === "assistant") &&
            typeof message.content === "string"
        )
        .map(message => ({
            role: message.role,
            content: message.content
        }));

    messages.replaceChildren();
    welcome.hidden = conversationHistory.length > 0;

    conversationHistory.forEach(message => {
        addMessage(message.role, message.content);
    });

    sidebar.hidden = true;
    sidebar.classList.remove("open");
    menuButton.setAttribute("aria-expanded", "false");

    renderHistory();
    input.focus();
}

/* -----------------------------
   History sidebar
------------------------------ */

let historyList = document.getElementById("conversationHistoryList");

if (!historyList && sidebar) {
    const historySection = document.createElement("section");
    historySection.className = "conversation-history-section";

    const heading = document.createElement("h3");
    heading.textContent = "History";

    historyList = document.createElement("div");
    historyList.id = "conversationHistoryList";
    historyList.className = "conversation-history-list";

    historySection.append(heading, historyList);
    sidebar.appendChild(historySection);
}

function renderHistory() {
    if (!historyList) return;

    historyList.replaceChildren();

    if (savedConversations.length === 0) {
        const empty = document.createElement("p");
        empty.className = "history-empty";
        empty.textContent = "Your conversations will appear here.";
        historyList.appendChild(empty);
        return;
    }

    savedConversations.forEach(conversation => {
        const item = document.createElement("div");
        item.className = "history-item";

        if (conversation.id === currentConversationId) {
            item.classList.add("selected");
        }

        const openButton = document.createElement("button");
        openButton.type = "button";
        openButton.className = "history-open-button";
        openButton.textContent = conversation.title || "New conversation";
        openButton.title = conversation.title || "New conversation";
        openButton.addEventListener("click", () => {
            openConversation(conversation.id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "history-delete-button";
        deleteButton.textContent = "×";
        deleteButton.setAttribute(
            "aria-label",
            `Delete ${conversation.title || "conversation"}`
        );
        deleteButton.title = "Delete conversation";
        deleteButton.addEventListener("click", () => {
            if (confirm("Delete this saved conversation?")) {
                deleteConversation(conversation.id);
            }
        });

        item.append(openButton, deleteButton);
        historyList.appendChild(item);
    });
}

/* -----------------------------
   Think / Search modes
------------------------------ */

function selectMode(mode) {
    selectedMode = mode;

    thinkButton.classList.toggle("active", mode === "think");
    searchButton.classList.toggle("active", mode === "search");

    thinkButton.setAttribute("aria-pressed", String(mode === "think"));
    searchButton.setAttribute("aria-pressed", String(mode === "search"));
}

thinkButton.addEventListener("click", () => selectMode("think"));
searchButton.addEventListener("click", () => selectMode("search"));

/* -----------------------------
   Message display
------------------------------ */

function addMessage(role, text) {
    const message = document.createElement("article");
    message.className = `chat-message ${role}`;

    const label = document.createElement("span");
    label.className = "message-role";
    label.textContent = role === "user" ? "You" : "Engineering AI";

    const content = document.createElement("div");
    content.textContent = text;

    message.append(label, content);
    messages.appendChild(message);

    return message;
}

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;

    sendButton.classList.toggle(
        "visible",
        input.value.trim().length > 0
    );
});

/* -----------------------------
   Send messages to Flask API
------------------------------ */

form.addEventListener("submit", async event => {
    event.preventDefault();

    const question = input.value.trim();
    if (!question || requestInProgress) return;

    if (!getCurrentConversation()) {
        createConversation();
    }

    const requestConversationId = currentConversationId;

    welcome.hidden = true;

    addMessage("user", question);
    addToConversation("user", question);

    // Send the previous messages as context.
    const previousHistory = conversationHistory.slice(-8);

    conversationHistory.push({
        role: "user",
        content: question
    });

    input.value = "";
    input.style.height = "auto";
    sendButton.classList.remove("visible");
    sendButton.disabled = true;
    requestInProgress = true;

    const statusMessage = addMessage(
        "assistant",
        selectedMode === "search"
            ? "Preparing your search request..."
            : "Engineering AI is thinking..."
    );

    try {
        const response = await fetch(
            "http://127.0.0.1:5001/api/assistant",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question,
                    conversation_history: previousHistory,
                    mode: selectedMode
                })
            }
        );

        let result;

        try {
            result = await response.json();
        } catch {
            throw new Error("The server returned an invalid response.");
        }

        if (!response.ok || result.success === false) {
            throw new Error(
                result.error || result.message || "The request failed."
            );
        }

        let answer = result.answer;

        if (!answer && result.calculation) {
            answer = JSON.stringify(result.calculation, null, 2);
        }

        if (!answer && result.message) {
            answer = result.message;
        }

        if (result.pressure_psi !== undefined && !answer) {
            answer = `Hydrostatic pressure: ${result.pressure_psi} psi`;
        }

        if (!answer) {
            answer = JSON.stringify(result, null, 2);
        }

        statusMessage.querySelector("div").textContent = answer;

        // Save the reply to the conversation that sent the request,
        // even if the user has switched to another conversation.
        const conversation = savedConversations.find(
            item => item.id === requestConversationId
        );

        if (conversation) {
            conversation.messages.push({
                role: "assistant",
                content: answer,
                createdAt: new Date().toISOString()
            });

            conversation.updatedAt = new Date().toISOString();

            savedConversations = [
                conversation,
                ...savedConversations.filter(
                    item => item.id !== conversation.id
                )
            ];

            saveConversations();
            renderHistory();
        }

        if (currentConversationId === requestConversationId) {
            conversationHistory.push({
                role: "assistant",
                content: answer
            });
        }
    } catch (error) {
        const errorMessage =
            `Unable to reach Engineering AI: ${error.message}. ` +
            "Check that the Flask API is running.";

        statusMessage.querySelector("div").textContent = errorMessage;

        // The failed user question remains visible but is removed
        // from saved chat context so it isn't treated as answered.
        const conversation = savedConversations.find(
            item => item.id === requestConversationId
        );

        if (conversation) {
            const lastMessage = conversation.messages.at(-1);

            if (
                lastMessage &&
                lastMessage.role === "user" &&
                lastMessage.content === question
            ) {
                conversation.messages.pop();
                saveConversations();
                renderHistory();
            }
        }

        if (currentConversationId === requestConversationId) {
            conversationHistory = conversationHistory.filter(
                (message, index) =>
                    !(index === conversationHistory.length - 1 &&
                      message.role === "user" &&
                      message.content === question)
            );
        }
    } finally {
        requestInProgress = false;
        sendButton.disabled = false;
        input.focus();
    }
});

/* -----------------------------
   New conversation
------------------------------ */

function resetChat() {
    currentConversationId = null;
    conversationHistory = [];

    messages.replaceChildren();
    welcome.hidden = false;

    input.value = "";
    input.style.height = "auto";
    sendButton.classList.remove("visible");

    selectedAttachments = [];
    renderAttachments();

    if (imageInput) imageInput.value = "";
    if (cameraInput) cameraInput.value = "";
    if (documentInput) documentInput.value = "";

    sidebar.hidden = true;
    sidebar.classList.remove("open");
    menuButton.setAttribute("aria-expanded", "false");

    renderHistory();
    input.focus();
}

newChatButton.addEventListener("click", resetChat);

/* -----------------------------
   Attachments menu and preview
------------------------------ */

document.getElementById("cameraOption").addEventListener("click", () => {
    attachmentMenu.hidden = true;
    cameraInput.click();
});

document.getElementById("photoOption").addEventListener("click", () => {
    attachmentMenu.hidden = true;
    imageInput.click();
});

document.getElementById("documentOption").addEventListener("click", () => {
    attachmentMenu.hidden = true;
    documentInput.click();
});

attachButton.addEventListener("click", () => {
    attachmentMenu.hidden = !attachmentMenu.hidden;
});

document.addEventListener("click", event => {
    if (
        attachmentMenu &&
        attachButton &&
        !attachmentMenu.contains(event.target) &&
        !attachButton.contains(event.target)
    ) {
        attachmentMenu.hidden = true;
    }
});

function renderAttachments() {
    attachmentPreview.replaceChildren();
    attachmentPreview.hidden = selectedAttachments.length === 0;

    selectedAttachments.forEach((file, index) => {
        const item = document.createElement("div");
        item.className = "attachment-item";

        if (file.type.startsWith("image/")) {
            const thumbnail = document.createElement("img");
            thumbnail.alt = "";
            thumbnail.src = URL.createObjectURL(file);
            item.appendChild(thumbnail);
        } else {
            const icon = document.createElement("span");
            icon.textContent = "📄";
            item.appendChild(icon);
        }

        const name = document.createElement("span");
        name.textContent = file.name;
        item.appendChild(name);

        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "attachment-remove";
        remove.textContent = "×";
        remove.setAttribute("aria-label", `Remove ${file.name}`);

        remove.addEventListener("click", () => {
            selectedAttachments.splice(index, 1);
            renderAttachments();
        });

        item.appendChild(remove);
        attachmentPreview.appendChild(item);
    });
}

function handleSelectedFiles(event) {
    const files = Array.from(event.target.files || []);

    for (const file of files) {
        if (selectedAttachments.length >= 5) {
            alert("You can attach up to 5 files at a time.");
            break;
        }

        const allowed =
            file.type.startsWith("image/") ||
            file.type === "application/pdf" ||
            file.type.startsWith("text/") ||
            /\.(pdf|txt|csv|doc|docx|xls|xlsx)$/i.test(file.name);

        if (!allowed) {
            alert(`Unsupported file: ${file.name}`);
            continue;
        }

        const duplicate = selectedAttachments.some(
            existing =>
                existing.name === file.name &&
                existing.size === file.size
        );

        if (!duplicate) {
            selectedAttachments.push(file);
        }
    }

    renderAttachments();
    event.target.value = "";
}

imageInput.addEventListener("change", handleSelectedFiles);
cameraInput.addEventListener("change", handleSelectedFiles);
documentInput.addEventListener("change", handleSelectedFiles);

/* -----------------------------
   Sidebar toggle — one handler
------------------------------ */

if (menuButton && sidebar) {
    menuButton.addEventListener("click", () => {
        sidebar.hidden = !sidebar.hidden;
        sidebar.classList.toggle("open", !sidebar.hidden);

        menuButton.setAttribute(
            "aria-expanded",
            String(!sidebar.hidden)
        );
    });

    menuButton.setAttribute("aria-controls", "sidebar");
    menuButton.setAttribute("aria-expanded", String(!sidebar.hidden));
}

/* Load saved history when the page opens. */
renderHistory();
