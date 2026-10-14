// ============================================
// ENGINEERING AI — MAIN JAVASCRIPT
// Chat, saved history, attachments and sidebar
// ============================================

const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("chatMessages");
const welcome = document.getElementById("welcome");
const sendButton = document.getElementById("sendButton");
const statusMessage = document.getElementById("statusMessage");

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
let selectedAttachments = [];

const CHAT_STORAGE_KEY = "engineeringAI_conversations_v1";

let conversations = [];
let activeConversationId = null;
let conversationHistory = [];

// ============================================
// LOAD SAVED CONVERSATIONS
// ============================================

try {
    const saved = localStorage.getItem(CHAT_STORAGE_KEY);
    conversations = saved ? JSON.parse(saved) : [];

    if (!Array.isArray(conversations)) {
        conversations = [];
    }
} catch (error) {
    console.error("Could not load saved chats:", error);
    conversations = [];
}

// ============================================
// MODE SELECTION
// ============================================

function selectMode(mode) {
    selectedMode = mode;

    thinkButton.classList.toggle("active", mode === "think");
    searchButton.classList.toggle("active", mode === "search");

    thinkButton.setAttribute("aria-pressed", String(mode === "think"));
    searchButton.setAttribute("aria-pressed", String(mode === "search"));
}

thinkButton.addEventListener("click", () => selectMode("think"));
searchButton.addEventListener("click", () => selectMode("search"));

// ============================================
// MESSAGE INPUT
// ============================================

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height =
        `${Math.min(input.scrollHeight, 180)}px`;

    sendButton.classList.toggle(
        "visible",
        input.value.trim().length > 0
    );
});

// ============================================
// DISPLAY A MESSAGE
// ============================================

function addMessage(role, text) {
    const message = document.createElement("article");
    message.className = `chat-message ${role}`;

    const label = document.createElement("span");
    label.className = "message-role";
    label.textContent =
        role === "user" ? "You" : "Engineering AI";

    const content = document.createElement("div");
    content.textContent = text;

    message.append(label, content);
    messages.appendChild(message);

    return message;
}

// ============================================
// SAVE CONVERSATIONS
// ============================================

function saveConversations() {
    try {
        localStorage.setItem(
            CHAT_STORAGE_KEY,
            JSON.stringify(conversations)
        );
    } catch (error) {
        console.error("Could not save chat history:", error);
        alert(
            "Chat history could not be saved. " +
            "Check your browser storage."
        );
    }
}

function createConversation() {
    const conversation = {
        id: `${Date.now()}-${Math.random()
            .toString(36).slice(2, 9)}`,
        title: "New chat",
        updatedAt: new Date().toISOString(),
        messages: []
    };

    conversations.unshift(conversation);
    activeConversationId = conversation.id;
    conversationHistory = [];

    saveConversations();
    renderChatHistory();

    return conversation;
}

function getActiveConversation() {
    return conversations.find(
        conversation =>
            conversation.id === activeConversationId
    );
}

function saveCurrentMessages() {
    const conversation = getActiveConversation();

    if (!conversation) return;

    conversation.messages = conversationHistory.map(message => ({
        role: message.role,
        content: message.content
    }));

    const firstUserMessage = conversationHistory.find(
        message => message.role === "user"
    );

    if (firstUserMessage) {
        const title = firstUserMessage.content;
        conversation.title =
            title.slice(0, 45) +
            (title.length > 45 ? "…" : "");
    }

    conversation.updatedAt = new Date().toISOString();

    conversations.sort(
        (a, b) =>
            new Date(b.updatedAt) - new Date(a.updatedAt)
    );

    saveConversations();
    renderChatHistory();
}

// ============================================
// RENDER CHAT HISTORY
// ============================================

function renderChatHistory() {
    const historyList =
        document.getElementById("chatHistoryList");

    if (!historyList) {
        console.warn(
            'Add id="chatHistoryList" to your sidebar in index.html.'
        );
        return;
    }

    historyList.replaceChildren();

    if (conversations.length === 0) {
        const empty = document.createElement("p");
        empty.className = "history-empty";
        empty.textContent =
            "Your saved chats will appear here.";

        historyList.appendChild(empty);
        return;
    }

    conversations.forEach(conversation => {
        const item = document.createElement("div");
        item.className = "history-item";

        if (conversation.id === activeConversationId) {
            item.classList.add("active");
        }

        const openButton = document.createElement("button");
        openButton.type = "button";
        openButton.className = "history-open";
        openButton.textContent =
            conversation.title || "New chat";
        openButton.title =
            conversation.title || "New chat";

        openButton.addEventListener("click", () => {
            openConversation(conversation.id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "history-delete";
        deleteButton.textContent = "×";
        deleteButton.title = "Delete this chat";
        deleteButton.setAttribute(
            "aria-label",
            "Delete this chat"
        );

        deleteButton.addEventListener("click", () => {
            deleteConversation(conversation.id);
        });

        item.append(openButton, deleteButton);
        historyList.appendChild(item);
    });
}

// ============================================
// OPEN A SAVED CONVERSATION
// ============================================

function openConversation(id) {
    const conversation = conversations.find(
        item => item.id === id
    );

    if (!conversation) return;

    activeConversationId = id;

    conversationHistory = conversation.messages.map(message => ({
        role: message.role,
        content: message.content
    }));

    messages.replaceChildren();

    welcome.hidden = conversationHistory.length > 0;

    conversationHistory.forEach(message => {
        addMessage(message.role, message.content);
    });

    input.value = "";
    input.style.height = "auto";
    sendButton.classList.remove("visible");

    if (statusMessage) {
        statusMessage.textContent = "";
    }

    renderChatHistory();
    input.focus();
}

// ============================================
// DELETE A CONVERSATION
// ============================================

function deleteConversation(id) {
    const conversation = conversations.find(
        item => item.id === id
    );

    if (!conversation) return;

    const confirmed = window.confirm(
        `Delete "${conversation.title || "New chat"}"? ` +
        "This cannot be undone."
    );

    if (!confirmed) return;

    conversations = conversations.filter(
        item => item.id !== id
    );

    if (activeConversationId === id) {
        activeConversationId = null;
        conversationHistory = [];
        messages.replaceChildren();
        welcome.hidden = false;
    }

    saveConversations();
    renderChatHistory();
}

// ============================================
// SEND A MESSAGE TO THE FLASK API
// ============================================

form.addEventListener("submit", async event => {
    event.preventDefault();

    const question = input.value.trim();

    if (!question && selectedAttachments.length === 0) {
        return;
    }

    if (!activeConversationId) {
        createConversation();
    }

    const userMessage = {
        role: "user",
        content: question || "Attached file(s)"
    };

    conversationHistory.push(userMessage);
    addMessage("user", userMessage.content);

    input.value = "";
    input.style.height = "auto";
    sendButton.classList.remove("visible");
    welcome.hidden = true;
    sendButton.disabled = true;

    const previousHistory = conversationHistory
        .slice(0, -1)
        .map(({ role, content }) => ({ role, content }));

    // Save the question immediately.
    saveCurrentMessages();

    // Show a temporary message while waiting for the API.
    const waitingMessage = addMessage(
        "assistant",
        selectedMode === "search"
            ? "Preparing your search request..."
            : "Engineering AI is thinking..."
    );

    const waitingContent = waitingMessage.querySelector("div");

    if (statusMessage) {
        statusMessage.textContent = "Thinking...";
    }

    try {
        const response = await fetch(
            "http://127.0.0.1:5001/api/assistant",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question,
                    conversation_history: previousHistory
                })
            }
        );

        const result = await response.json();

        if (!response.ok || result.success === false) {
            throw new Error(
                result.error ||
                result.message ||
                "The request failed."
            );
        }

        let answer = result.answer;

        // Hydrostatic pressure result formatting.
        if (
            result.calculation === "Hydrostatic Pressure" &&
            result.pressure_psi !== undefined
        ) {
            answer =
                `HYDROSTATIC PRESSURE\n\n` +
                `Mud weight: ${result.mud_weight_ppg} ppg\n` +
                `True vertical depth (TVD): ${result.tvd_ft} ft\n` +
                `Calculated pressure: ${result.pressure_psi} psi\n\n` +
                `Formula: ${
                    result.formula ||
                    "P = 0.052 × MW × TVD"
                }`;
        }

        // API gravity result formatting.
        else if (
            result.calculation === "API Gravity" &&
            result.api_gravity !== undefined
        ) {
            answer =
                `API GRAVITY\n\n` +
                `Specific gravity: ${result.specific_gravity}\n` +
                `API gravity: ${result.api_gravity}° API\n` +
                `Formula: °API = (141.5 / SG) - 131.5`;
        }

        else if (result.pressure_psi !== undefined) {
            answer =
                `Hydrostatic pressure: ${result.pressure_psi} psi`;
        }

        else if (!answer && result.message) {
            answer = result.message;
        }

        else if (!answer) {
            answer = JSON.stringify(result, null, 2);
        }

        waitingContent.textContent = answer;

        conversationHistory.push({
            role: "assistant",
            content: answer
        });

        saveCurrentMessages();

        if (statusMessage) {
            statusMessage.textContent = "";
        }

    } catch (error) {
        waitingContent.textContent =
            `Unable to reach Engineering AI: ${error.message}. ` +
            "Check that the Flask API is running.";

        // Remove the failed question from saved conversation history.
        if (
            conversationHistory.length > 0 &&
            conversationHistory[conversationHistory.length - 1].role === "user"
        ) {
            conversationHistory.pop();
        }

        saveCurrentMessages();

        if (statusMessage) {
            statusMessage.textContent = "";
        }

    } finally {
        sendButton.disabled = false;
        input.focus();
    }
});

// ============================================
// START A NEW CHAT
// ============================================

newChatButton.addEventListener("click", resetChat);

function resetChat() {
    activeConversationId = null;
    conversationHistory = [];

    messages.replaceChildren();
    welcome.hidden = false;

    input.value = "";
    input.style.height = "auto";
    sendButton.classList.remove("visible");

    selectedAttachments = [];
    renderAttachments();

    if (statusMessage) {
        statusMessage.textContent = "";
    }

    renderChatHistory();
    input.focus();
}

// ============================================
// ATTACHMENT MENU
// ============================================

if (cameraInput) {
    document.getElementById("cameraOption")
        .addEventListener("click", () => {
            attachmentMenu.hidden = true;
            cameraInput.click();
        });
}

if (imageInput) {
    document.getElementById("photoOption")
        .addEventListener("click", () => {
            attachmentMenu.hidden = true;
            imageInput.click();
        });
}

if (documentInput) {
    document.getElementById("documentOption")
        .addEventListener("click", () => {
            attachmentMenu.hidden = true;
            documentInput.click();
        });
}

if (attachButton && attachmentMenu) {
    attachButton.addEventListener("click", () => {
        attachmentMenu.hidden = !attachmentMenu.hidden;
    });

    document.addEventListener("click", event => {
        if (
            !attachmentMenu.contains(event.target) &&
            !attachButton.contains(event.target)
        ) {
            attachmentMenu.hidden = true;
        }
    });
}

// ============================================
// ATTACHMENT PREVIEW
// ============================================

function renderAttachments() {
    if (!attachmentPreview) return;

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
        remove.setAttribute(
            "aria-label",
            `Remove ${file.name}`
        );

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

if (imageInput) {
    imageInput.addEventListener("change", handleSelectedFiles);
}

if (cameraInput) {
    cameraInput.addEventListener("change", handleSelectedFiles);
}

if (documentInput) {
    documentInput.addEventListener("change", handleSelectedFiles);
}

// ============================================
// SIDEBAR TOGGLE — ONE CLICK HANDLER ONLY
// ============================================

if (menuButton && sidebar) {
    menuButton.setAttribute("aria-controls", "sidebar");

    menuButton.addEventListener("click", () => {
        sidebar.hidden = !sidebar.hidden;
        sidebar.classList.toggle("open", !sidebar.hidden);

        menuButton.setAttribute(
            "aria-expanded",
            String(!sidebar.hidden)
        );
    });

    menuButton.setAttribute(
        "aria-expanded",
        String(!sidebar.hidden)
    );
}

// ============================================
// INITIALIZE CHAT HISTORY
// ============================================

renderChatHistory();
renderAttachments();