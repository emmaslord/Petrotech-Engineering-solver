// ============================================
// ENGINEERING AI â€” MAIN JAVASCRIPT
// Chat, saved history, attachments and sidebar
// ============================================

const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("chatMessages");
const welcome = document.getElementById("welcome");
const sendButton = document.getElementById("sendButton");
const soundButton = document.getElementById("soundButton");
const voiceButton = document.getElementById("voiceButton");
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




const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

let voiceRecognition = null;
let isVoiceRecording = false;

function setVoiceStatus(message) {
    if (statusMessage) {
        statusMessage.textContent = message;
    }
}

if (voiceButton) {
    if (!SpeechRecognition) {
        voiceButton.title =
            "Voice input is not supported in this browser";
        voiceButton.setAttribute(
            "aria-label",
            "Voice input is not supported"
        );
    } else {
        voiceRecognition = new SpeechRecognition();
        voiceRecognition.lang = "en-NG";
        voiceRecognition.continuous = false;
        voiceRecognition.interimResults = true;

        voiceRecognition.onstart = () => {
            isVoiceRecording = true;
            voiceButton.classList.add("recording");
            voiceButton.setAttribute("aria-pressed", "true");
            voiceButton.title = "Stop voice input";
            setVoiceStatus("Listeningâ€¦ Speak now.");
        };

        voiceRecognition.onresult = (event) => {
            let transcript = "";

            for (
                let i = 0;
                i < event.results.length;
                i++
            ) {
                transcript +=
                    event.results[i][0].transcript + " ";
            }

            input.value = transcript.trim();
            input.dispatchEvent(
                new Event("input", { bubbles: true })
            );
        };

        voiceRecognition.onerror = (event) => {
            const messages = {
                "not-allowed":
                    "Microphone permission was denied. Check your browser settings.",
                "no-speech":
                    "No speech detected. Tap the microphone and try again.",
                "audio-capture":
                    "No microphone was detected. Check your microphone connection."
            };

            setVoiceStatus(
                messages[event.error] ||
                "Voice input stopped. Please try again."
            );
        };

        voiceRecognition.onend = () => {
            isVoiceRecording = false;
            voiceButton.classList.remove("recording");
            voiceButton.setAttribute("aria-pressed", "false");
            voiceButton.title = "Voice input";
        };

        voiceButton.addEventListener("click", () => {
            if (isVoiceRecording) {
                voiceRecognition.stop();
                setVoiceStatus("Finishing voice inputâ€¦");
                return;
            }

            try {
                voiceRecognition.start();
            } catch (error) {
                setVoiceStatus(
                    "Could not start voice input. Please try again."
                );
            }
        });
    }
}



// Read-aloud settings for Engineering AI responses.
let soundEnabled = (() => {
    try {
        return localStorage.getItem("engineeringAI_soundEnabled") !== "false";
    } catch (error) {
        return true;
    }
})();


if (soundButton) {
    const updateSoundButton = () => {
        soundButton.textContent = soundEnabled ? "ðŸ”Š" : "ðŸ”‡";

        soundButton.setAttribute(
            "aria-pressed",
            String(soundEnabled)
        );

        soundButton.setAttribute(
            "aria-label",
            soundEnabled ? "Turn speech off" : "Turn speech on"
        );

        soundButton.title = soundEnabled
            ? "Turn speech off"
            : "Turn speech on";
    };

    updateSoundButton();

    soundButton.addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    updateSoundButton();

    try {
        localStorage.setItem(
            "engineeringAI_soundEnabled",
            String(soundEnabled)
        );
    } catch (error) {
        console.warn("Could not save sound preference:", error);
    }

    if (!soundEnabled && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
});
    };



function updateSoundButton() {
    if (!soundButton) return;

    soundButton.textContent = soundEnabled ? "ðŸ”Š" : "ðŸ”‡";
    soundButton.title = soundEnabled
        ? "Turn off spoken responses"
        : "Turn on spoken responses";

    soundButton.setAttribute(
        "aria-label",
        soundButton.title
    );

    soundButton.setAttribute(
        "aria-pressed",
        String(soundEnabled)
    );
}

        if (!soundEnabled && "speechSynthesis" in window) {
            window.speechSynthesis.cancel();
        }

        updateSoundButton();


    updateSoundButton();


// Speak an Engineering AI response when sound is enabled.

function speakAssistantResponse(text) {
    if (!("speechSynthesis" in window)) {
        console.warn("Speech output is not supported in this browser.");
        return;
    }

    if (typeof soundEnabled !== "undefined" && !soundEnabled) {
        console.log("Speech is disabled: soundEnabled is false.");
        return;
    }

    const cleanText = String(text || "")
        .replace(/```[\s\S]*?```/g, " Code block omitted. ")
        .replace(/https?:\/\/\S+/g, " link omitted ")
        .replace(/[`*_>#\[\]()]/g, " ");

    if (!cleanText.trim()) return;

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(cleanText);
   speech.lang = "en-NG";

speech.onstart = () => {
    console.log("Speech started successfully.");
};

speech.onend = () => {
    console.log("Speech finished.");
};

speech.onerror = (event) => {
    console.error("Speech error:", event.error);
};

window.speechSynthesis.speak(speech);
}




// ============================================
// LOAD SAVED CONVERSATIONS
// ============================================

try {
    const saved = localStorage.getItem(CHAT_STORAGE_KEY);
    conversations = saved ? JSON.parse(saved) : [];

    if (!Array.isArray(conversations)) {
        conversations = [];
    }

    conversations = conversations
        .filter(conversation =>
            conversation &&
            typeof conversation.id === "string" &&
            Array.isArray(conversation.messages)
        )
        .map(conversation => ({
            id: conversation.id,
            title: conversation.title || "New chat",
            updatedAt: conversation.updatedAt || new Date().toISOString(),
            messages: conversation.messages
                .filter(message =>
                    message &&
                    ["user", "assistant"].includes(message.role) &&
                    typeof message.content === "string"
                )
                .map(message => ({
                    role: message.role,
                    content: message.content
                }))
        }))
        .sort((a, b) =>
            new Date(b.updatedAt) - new Date(a.updatedAt)
        );
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
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;

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
    label.textContent = role === "user" ? "You" : "Engineering AI";

    const content = document.createElement("div");
    content.className = "message-content";

    if (role === "assistant" && window.marked && window.DOMPurify) {
        const renderedMarkdown = window.marked.parse(String(text ?? ""));

        content.innerHTML = window.DOMPurify.sanitize(renderedMarkdown);

        if (window.hljs) {
            content.querySelectorAll("pre code").forEach(codeBlock => {
                window.hljs.highlightElement(codeBlock);
            });
        }
    } else {
        content.textContent = String(text ?? "");
    }

message.append(label, content);
messages.appendChild(message);

if (role === "assistant") {
    console.log("Assistant speech triggered:", text);
    speakAssistantResponse(text);
}

return message;
}

// ============================================
// SAVE CONVERSATIONS
// ============================================


function saveConversations() {
    if (!Array.isArray(conversations)) {
        console.error("Cannot save: conversations is not an array.");
        return;
    }

    const newestFirst = [...conversations].sort((a, b) => {
        const timeA = Date.parse(a.updatedAt || "") || 0;
        const timeB = Date.parse(b.updatedAt || "") || 0;
        return timeB - timeA;
    });

    const cacheOptions = [
        { chats: 10, messages: 20, content: 4000 },
        { chats: 5, messages: 10, content: 2000 },
        { chats: 3, messages: 5, content: 1000 },
        { chats: 1, messages: 3, content: 500 }
    ];

    for (const option of cacheOptions) {
        try {
            const cache = newestFirst
                .slice(0, option.chats)
                .map(conversation => ({
                    ...conversation,
                    messages: (Array.isArray(conversation.messages)
                        ? conversation.messages
                        : []
                    )
                        .slice(-option.messages)
                        .map(message => ({
                            ...message,
                            content: String(message.content || "")
                                .slice(-option.content)
                        }))
                }));

            localStorage.setItem(
                CHAT_STORAGE_KEY,
                JSON.stringify(cache)
            );

            console.log(
                "Local chat cache saved:",
                cache.length,
                "conversation(s)."
            );
            return;
        } catch (error) {
            if (
                error.name !== "QuotaExceededError" &&
                error.name !== "NS_ERROR_DOM_QUOTA_REACHED"
            ) {
                console.error("Local cache save failed:", error);
                return;
            }
        }
    }

    console.error(
        "Local cache is full. Cloud conversations were not deleted."
    );
}

async function loadConversationsFromCloud() {
    try {
        if (!window.engineeringAIAuth) {
            console.log("Cloud history skipped: authentication is unavailable.");
            return;
        }

        const token = await window.engineeringAIAuth.getAccessToken();

        if (!token) {
            console.log("Cloud history skipped: sign in to load saved chats.");
            return;
        }

        const response = await fetch(
            "https://engineeringai.onrender.com/api/conversations",
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
            console.error(
                "Cloud history failed to load:",
                result.error || response.status
            );
            return;
        }

        const cloudConversations = result.conversations || [];

        if (!Array.isArray(conversations)) {
            console.error("Local conversations are not available.");
            return;
        }

        cloudConversations.forEach(cloud => {
            if (!cloud.id) return;

            const existing = conversations.find(
                local => local.cloudId === cloud.id
            );

            const cloudUpdatedAt =
                cloud.updated_at || cloud.created_at || new Date().toISOString();

            if (existing) {
                // Update a matching local chat only when the cloud copy
                // is at least as recent as the local copy.
                const localTime = Date.parse(existing.updatedAt || "");
                const cloudTime = Date.parse(cloudUpdatedAt);

                if (
                    !Number.isFinite(localTime) ||
                    (Number.isFinite(cloudTime) && cloudTime >= localTime)
                ) {
                    existing.title = cloud.title || existing.title || "New chat";
                    existing.messages = Array.isArray(cloud.messages)
                        ? cloud.messages
                        : [];
                    existing.updatedAt = cloudUpdatedAt;
                }

                return;
            }

            // Add cloud chats that are not already in local history.
            conversations.push({
                id: `cloud-${cloud.id}`,
                cloudId: cloud.id,
                title: cloud.title || "New chat",
                messages: Array.isArray(cloud.messages)
                    ? cloud.messages
                    : [],
                updatedAt: cloudUpdatedAt
            });
        });

        conversations.sort(
            (a, b) =>
                new Date(b.updatedAt || 0) -
                new Date(a.updatedAt || 0)
        );

        saveConversations();
        renderChatHistory();

        console.log(
            `Cloud history loaded: ${cloudConversations.length} conversation(s).`
        );
    } catch (error) {
        console.error("Could not load cloud history:", error.message);
    }
}

function createConversation() {
    const conversation = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        title: "New chat",
        updatedAt: new Date().toISOString(),
        messages: []
    };

    conversations.unshift(conversation);
    activeConversationId = conversation.id;
    conversationHistory = [];

    saveConversations();
    renderChatHistory();

    messages.replaceChildren();
    welcome.hidden = false;

    if (statusMessage) {
        statusMessage.textContent = "";
    }

    input.value = "";
    input.style.height = "auto";
    sendButton.classList.remove("visible");

    return conversation;
}

function getActiveConversation() {
    return conversations.find(
        conversation => conversation.id === activeConversationId
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
            (title.length > 45 ? "â€¦" : "");
    }

    conversation.updatedAt = new Date().toISOString();

    conversations.sort(
        (a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)
    );


    saveConversations();
    renderChatHistory();

    console.log("DEBUG: saveCurrentMessages reached cloud-save call");
    void saveConversationToCloud(conversation);
}


async function saveConversationToCloud(conversation) {
    try {


       console.log("DEBUG: saveConversationToCloud started", conversation);

        if (!conversation || !window.engineeringAIAuth) {
            return;
        }

        const token = await window.engineeringAIAuth.getAccessToken();

        const payload = {
            title: conversation.title || "New chat",
            messages: (conversation.messages || []).map(message => ({
                role: message.role,
                content: message.content
            }))
        };

        const isCloudConversation =
            typeof conversation.cloudId === "string" &&
            conversation.cloudId.length > 0;

        const url = isCloudConversation
            ? `https://engineeringai.onrender.com/api/conversations/${encodeURIComponent(conversation.cloudId)}`
            : "https://engineeringai.onrender.com/api/conversations";

        const response = await fetch(url, {
            method: isCloudConversation ? "PUT" : "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            console.error("Cloud save failed:", result.error || response.status);
            return;
        }

        const saved = result.conversation;

        if (saved && saved.id) {
            conversation.cloudId = saved.id;
            saveConversations();
        }

        console.log("Conversation saved to cloud.");
    } catch (error) {
        console.error("Cloud save failed:", error.message);
    }
}


// ============================================
// RENDER CHAT HISTORY
// ============================================

function renderChatHistory() {
    const historyList = document.getElementById("chatHistoryList");

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
        empty.textContent = "Your saved chats will appear here.";
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
        openButton.textContent = conversation.title || "New chat";
        openButton.title = conversation.title || "New chat";

        openButton.addEventListener("click", () => {
            openConversation(conversation.id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "history-delete";
        deleteButton.textContent = "Ã—";
        deleteButton.title = "Delete this chat";
        deleteButton.setAttribute("aria-label", "Delete this chat");

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
    const conversation = conversations.find(item => item.id === id);

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
    const conversation = conversations.find(item => item.id === id);

    if (!conversation) return;

    const confirmed = window.confirm(
        `Delete "${conversation.title || "New chat"}"? ` +
        "This cannot be undone."
    );

    if (!confirmed) return;

    conversations = conversations.filter(item => item.id !== id);

    if (activeConversationId === id) {
        activeConversationId = null;
        conversationHistory = [];
        messages.replaceChildren();
        welcome.hidden = false;
    }

    saveConversations();
    renderChatHistory();
}
function saveConversations() {
    if (!Array.isArray(conversations)) {
        console.error("Cannot save history: conversations is not an array.");
        return;
    }

    // Keep the full conversations in memory.
    // Only a smaller cache is written to browser storage.
    const newestFirst = [...conversations].sort(
        (a, b) =>
            Date.parse(b.updatedAt || 0) -
            Date.parse(a.updatedAt || 0)
    );

    const cacheOptions = [
        { chats: 10, messages: 20, content: 4000 },
        { chats: 5, messages: 10, content: 2000 },
        { chats: 3, messages: 5, content: 1000 },
        { chats: 1, messages: 3, content: 500 }
    ];

    for (const option of cacheOptions) {
        try {
            const cache = newestFirst
                .slice(0, option.chats)
                .map(conversation => ({
                    ...conversation,
                    messages: (conversation.messages || [])
                        .slice(-option.messages)
                        .map(message => ({
                            ...message,
                            content: String(message.content || "")
                                .slice(-option.content)
                        }))
                }));

            localStorage.setItem(
                CHAT_STORAGE_KEY,
                JSON.stringify(cache)
            );

            if (option.chats < 10) {
                console.warn(
                    "Browser storage was limited. A smaller local cache was saved."
                );
            }

            return;
        } catch (error) {
            if (
                error.name !== "QuotaExceededError" &&
                error.name !== "NS_ERROR_DOM_QUOTA_REACHED" &&
                error.name !== "SecurityError"
            ) {
                console.error("Could not save local chat cache:", error);
                return;
            }
        }
    }

    console.error(
        "Could not save the local chat cache. " +
        "Existing browser data was left untouched."
    );
}

renderChatHistory();


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


console.log("DEBUG: saveCurrentMessages ENTERED");

saveCurrentMessages();

// Create a placeholder for the assistant's response.
const waitingMessage = addMessage("assistant", "");
const waitingContent = waitingMessage.querySelector("div");
waitingContent.textContent = "Thinking...";

    let effectiveQuestion = question;

    try {
        // Upload and extract any attached files before asking the AI.
        if (selectedAttachments.length > 0) {
            if (statusMessage) {
                statusMessage.textContent = "Reading your attachments...";
            }

            const uploadResult = await uploadAttachments(
                [...selectedAttachments],
                question
            );

            const extractedText = uploadResult.combined_text || "";

            effectiveQuestion =
                `${question || "Please analyze the attached files."}\n\n` +
                `Extracted attachment text:\n${extractedText}`;

            const filenames = uploadResult.files
                .map(file => file.name)
                .join(", ");

            userMessage.content =
                `${question ? question + "\n" : ""}Attached files: ${filenames}`;

            selectedAttachments = [];
            renderAttachments();
            saveCurrentMessages();

            if (statusMessage) {
                statusMessage.textContent = "Preparing your answer...";
            }
        }

        // Keep calculation requests on the existing, tested endpoint.
        const calculatorTerms =
            /\b(hydrostatic pressure|formation pressure|mud weight|mudweight|api gravity|specific gravity|formation volume factor|reservoir)\b/i;

        const calculationActions =
            /\b(calculate|compute|determine|work out|solve|convert)\b/i;

        const hasEngineeringInputs =
            /\d+(?:\.\d+)?\s*(?:ppg|psi|ft|feet|sg|Â°?\s*api)\b/i.test(question);

        const useStreaming =
            !(calculatorTerms.test(question) &&
              (calculationActions.test(question) ||
               hasEngineeringInputs));

        let answer = "";

        if (useStreaming) {
            // Stream general AI responses progressively.
            const response = await fetch(
                "https://engineeringai.onrender.com/api/assistant/stream",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        question: effectiveQuestion,
                        conversation_history: previousHistory,
                        mode: document.getElementById("aiModeSelect").value
                    })
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Streaming request failed (HTTP ${response.status}).`
                );
            }

            if (!response.body) {
                throw new Error(
                    "Your browser does not support response streaming."
                );
            }

            waitingContent.textContent = "";

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            let finished = false;

            while (!finished) {
                const { value, done } = await reader.read();

                if (done) {
                    buffer += decoder.decode();
                    finished = true;
                } else {
                    buffer += decoder.decode(value, {
                        stream: true
                    });
                }

                const events = buffer.split("\n\n");
                buffer = events.pop() || "";

                for (const eventText of events) {
                    const dataLine = eventText
                        .split("\n")
                        .find(line => line.startsWith("data: "));

                    if (!dataLine) continue;

                    const event = JSON.parse(dataLine.slice(6));

                    if (event.error) {
                        throw new Error(event.error);
                    }

                    if (typeof event.chunk === "string") {
    answer += event.chunk;

    if (window.marked && window.DOMPurify) {
        const renderedMarkdown = window.marked.parse(answer);
        waitingContent.innerHTML =
            window.DOMPurify.sanitize(renderedMarkdown);
    } else {
        waitingContent.textContent = answer;
    }
}

                    if (event.done) {
                        finished = true;
                        break;
                    }
                }
            }

            if (!answer.trim()) {
                throw new Error(
                    "The assistant returned an empty response."
                );
            }

speakAssistantResponse(answer);

        if (window.hljs) {
    waitingContent.querySelectorAll("pre code").forEach(codeBlock => {
        window.hljs.highlightElement(codeBlock);
    });
}




        } else {
            // Preserve existing engineering calculation behavior.
            const response = await fetch(
                "https://engineeringai.onrender.com/api/assistant",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        question: question,
                        conversation_history: previousHistory,
                        mode: document.getElementById("aiModeSelect").value
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

            answer = result.answer;

            if (
                result.calculation === "Hydrostatic Pressure" &&
                result.pressure_psi !== undefined
            ) {
                answer =
                    `HYDROSTATIC PRESSURE\n\n` +
                    `Mud weight: ${result.mud_weight_ppg} ppg\n` +
                    `True vertical depth (TVD): ${result.tvd_ft} ft\n` +
                    `Calculated pressure: ${result.pressure_psi} psi\n\n` +
                    `Formula: ${result.formula || "P = 0.052 Ã— MW Ã— TVD"}`;
            } else if (
                result.calculation === "API Gravity" &&
                result.api_gravity !== undefined
            ) {
                answer =
                    `API GRAVITY\n\n` +
                    `Specific gravity: ${result.specific_gravity}\n` +
                    `API gravity: ${result.api_gravity}Â° API\n` +
                    `Formula: Â°API = (141.5 / SG) - 131.5`;
            } else if (result.pressure_psi !== undefined) {
                answer =
                    `Hydrostatic pressure: ${result.pressure_psi} psi`;
            } else if (!answer && result.message) {
                answer = result.message;
            } else if (!answer) {
                answer = JSON.stringify(result, null, 2);
            }

            if (window.marked && window.DOMPurify) {
    const renderedMarkdown = window.marked.parse(String(answer || ""));
    waitingContent.innerHTML =
        window.DOMPurify.sanitize(renderedMarkdown);

    if (window.hljs) {
        waitingContent.querySelectorAll("pre code").forEach(codeBlock => {
            window.hljs.highlightElement(codeBlock);
        });
    }
} else {
    waitingContent.textContent = String(answer || "");
}
        }

        // Preserve the existing conversation and cloud-save workflow.
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
            icon.textContent = "ðŸ“„";
            item.appendChild(icon);
        }

        const name = document.createElement("span");
        name.textContent = file.name;
        item.appendChild(name);

        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "attachment-remove";
        remove.textContent = "Ã—";
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


async function uploadAttachments(files, question = "") {
    const token = await window.engineeringAIAuth?.getAccessToken?.();

    if (!token) {
        throw new Error("Please sign in before uploading files.");
    }

    const formData = new FormData();

    for (const file of files) {
        formData.append("files", file);
    }

    formData.append("question", question);

    const response = await fetch(
        "https://engineeringai.onrender.com/api/upload",
        {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`
            },
            body: formData
        }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
        throw new Error(
            data.error || "The files could not be processed."
        );
    }

    return data;
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
 // SIDEBAR TOGGLE â€” MOBILE-FRIENDLY
 // ============================================

const sidebarBackdrop = document.getElementById("sidebarBackdrop");

function closeSidebar() {
    if (sidebar) {
        sidebar.hidden = true;
        sidebar.classList.remove("open");
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.hidden = true;
    }

    if (menuButton) {
        menuButton.setAttribute("aria-expanded", "false");
    }
}

function openSidebar() {
    if (sidebar) {
        sidebar.hidden = false;
        sidebar.classList.add("open");
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.hidden = false;
    }

    if (menuButton) {
        menuButton.setAttribute("aria-expanded", "true");
    }
}

if (menuButton && sidebar) {
    menuButton.setAttribute("aria-controls", "sidebar");

    menuButton.addEventListener("click", () => {
        if (sidebar.hidden) {
            openSidebar();
        } else {
            closeSidebar();
        }
    });

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", closeSidebar);
    }

    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && !sidebar.hidden) {
            closeSidebar();
        }
    });

    menuButton.setAttribute(
        "aria-expanded",
        String(!sidebar.hidden)
    );
}



 // ============================================
 // ENGINEERING AI PAGE NAVIGATION
 // ============================================

const chatView = document.getElementById("chatView");
const aboutPage = document.getElementById("aboutPage");
const settingsPage = document.getElementById("settingsPage");


function closeNavigationSidebar() {
    if (sidebar) {
        sidebar.hidden = true;
        sidebar.classList.remove("open");
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.hidden = true;
    }

    if (menuButton) {
        menuButton.setAttribute("aria-expanded", "false");
    }
}



function showEngineeringAIView(view) {
    const mainContent = document.querySelector(".main-content");
    const aboutPage = document.getElementById("aboutPage");
    const welcome = document.getElementById("welcome");
    const workspaceHeading = document.querySelector(".workspace-heading");
    const chatMessages = document.getElementById("chatMessages");
    const statusMessage = document.getElementById("statusMessage");
    const composerArea = document.querySelector(".composer-area");
    const showAbout = view === "about";
    const showSettings = view === "settings";

   const showChat = view === "chat";
const showCalculators = view === "calculators";
const showWorkspace = showChat || showCalculators;
const showWelcome = showChat && conversationHistory.length === 0;


if (mainContent) mainContent.hidden = !showWorkspace;
if (aboutPage) aboutPage.hidden = !showAbout;
if (settingsPage) settingsPage.hidden = !showSettings;
if (welcome) welcome.hidden = !showWelcome;
if (workspaceHeading) workspaceHeading.hidden = !showChat;
if (chatMessages) chatMessages.hidden = !showChat;
if (statusMessage) statusMessage.hidden = !showWorkspace;
if (composerArea) composerArea.hidden = !showChat;
    document.body.classList.toggle("about-view", showAbout);

    closeNavigationSidebar();
}


 // ABOUT
document.querySelectorAll('[data-action="about"]').forEach(link => {
    link.addEventListener("click", event => {
        event.preventDefault();
        showEngineeringAIView("about");
    });
});



// NEW CHAT
document.querySelectorAll('[data-action="new-chat"]').forEach(link => {
    link.addEventListener("click", event => {
        event.preventDefault();

        showEngineeringAIView("chat");
        resetChat();
    });
});

// CALCULATORS
document.querySelectorAll('[data-action="calculators"]').forEach(link => {
    link.addEventListener("click", event => {
        event.preventDefault();

        showEngineeringAIView("calculators");

        if (statusMessage) {
            statusMessage.textContent =
                "Engineering calculators are available through the chat. Ask a calculation question to get started.";
        }
    });
});

// SETTINGS
document.querySelectorAll('[data-action="settings"]').forEach(link => {
    link.addEventListener("click", event => {
        event.preventDefault();
        showEngineeringAIView("settings");
    });
});

// Keep the existing chat visible when the app starts.
showEngineeringAIView("chat");



// ============================================
// INITIALIZE CHAT HISTORY
// ============================================

renderChatHistory();


/* ==========================================
   ENGINEERING AI â€” SUPABASE AUTHENTICATION
   Add this block at the end of app.js
   ========================================== */

(async function initializeEngineeringAIAuth() {
    const authPanel = document.getElementById("authPanel");
    const authForm = document.getElementById("authForm");

    const createAccountForm =
    document.getElementById("createAccountForm");

const backToSignInButton =
    document.getElementById("backToSignInButton");

const signupMessage =
    document.getElementById("signupMessage");


    const authEmail = document.getElementById("authEmail");
    const authDisplayName = document.getElementById("authDisplayName");
    const authPassword = document.getElementById("authPassword");
    const authMessage = document.getElementById("authMessage");
    const signInButton = document.getElementById("signInButton");
    const signUpButton = document.getElementById("signUpButton");
    const accountBar = document.getElementById("accountBar");
    const accountEmail = document.getElementById("accountEmail");
    const signOutButton = document.getElementById("signOutButton");
    const googleSignInButton = document.getElementById("googleSignInButton");

    if (
        !authPanel || !authForm || !authEmail || !authDisplayName ||
        !authPassword || !authMessage || !signInButton ||
        !signUpButton || !accountBar || !accountEmail ||
        !signOutButton
    ) {
        console.error(
            "Authentication HTML is missing. Check index.html."
        );
        return;
    }


const protectedElements = [
    document.querySelector(".topbar"),
    document.querySelector(".main-content"),
    document.querySelector(".composer-area"),
    document.getElementById("sidebar"),
    document.querySelector(".chat-history-section")
].filter(Boolean);


    let authClient = null;
    let currentSession = null;
    let busy = false;

    function showMessage(message, isError = false) {
        authMessage.textContent = message;
        authMessage.style.color = isError ? "#b42318" : "";
    }

    function setBusy(value) {
        busy = value;
        signInButton.disabled = value;
        signUpButton.disabled = value;
        signOutButton.disabled = value;
        if (googleSignInButton) googleSignInButton.disabled = value;
    }


function updateAuthUI(session) {
    currentSession = session;

    const signedIn = Boolean(session?.user);
    const mainContent = document.querySelector(".main-content");
    const aboutPage = document.getElementById("aboutPage");
    const composerArea = document.querySelector(".composer-area");

    authPanel.hidden = signedIn;
    accountBar.hidden = !signedIn;

    protectedElements.forEach(element => {
        element.hidden = !signedIn;
    });

    // Keep the workspace and its welcome screen hidden until sign-in.
    if (mainContent) {
        mainContent.hidden = !signedIn;
    }

    if (!signedIn) {
        if (aboutPage) aboutPage.hidden = true;
        if (composerArea) composerArea.hidden = true;
    }


const savedDisplayName = (() => {
    try {
        return localStorage.getItem("engineeringAI_displayName")?.trim() || "";
    } catch (error) {
        return "";
    }
})();

const accountDisplayName =
    session?.user?.user_metadata?.display_name?.trim() ||
    savedDisplayName;

              accountEmail.textContent = signedIn
    ? accountDisplayName || session.user.email || "Signed in"
    : "";

          if (!signedIn) {
    showMessage("");
    authPassword.value = "";
              }

}

    try {
        if (!window.supabase?.createClient) {
            throw new Error(
                "Supabase JavaScript library did not load. " +
                "Check your internet connection and index.html."
            );
        }

        const configResponse = await fetch(
            "https://engineeringai.onrender.com/api/config"
        );

        const config = await configResponse.json();

        if (
            !configResponse.ok ||
            !config.success ||
            !config.supabaseUrl ||
            !config.supabaseKey
        ) {
            throw new Error(
                config.error || "Could not load Supabase configuration."
            );
        }

        authClient = window.supabase.createClient(
            config.supabaseUrl,
            config.supabaseKey
        );



window.engineeringAIAuth = {
    async getAccessToken() {
        if (!authClient) {
            throw new Error("Authentication is not initialized.");
        }

        const { data, error } = await authClient.auth.getSession();

        if (error) {
            throw error;
        }

        if (!data.session?.access_token) {
            throw new Error("Please sign in again.");
        }

        return data.session.access_token;
    }
};


        const { data, error } = await authClient.auth.getSession();

        if (error) throw error;

        updateAuthUI(data.session);

        if (data.session) {
    void loadConversationsFromCloud();
}


        authClient.auth.onAuthStateChange((_event, session) => {
            updateAuthUI(session);
        });


if (signOutButton) {
    signOutButton.addEventListener("click", async () => {
        if (busy || !authClient) return;

        setBusy(true);
        showMessage("Signing out...");

        try {
            const { error } = await authClient.auth.signOut();

            if (error) throw error;

            updateAuthUI(null);
            showMessage("");
            console.log("Signed out successfully.");
        } catch (error) {
            showMessage(
                error.message || "Sign out failed. Please try again.",
                true
            );
        } finally {
            setBusy(false);
        }
    });
}



if (googleSignInButton) {
    googleSignInButton.addEventListener("click", async () => {
        if (busy) return;

        setBusy(true);
        showMessage("Connecting to Google...");

        try {
            const { error } = await authClient.auth.signInWithOAuth({
                provider: "google",
                options: {
                    redirectTo: window.location.origin + window.location.pathname
                }
            });

            if (error) throw error;
        } catch (error) {
            showMessage(
                error.message || "Google sign-in failed.",
                true
            );
            setBusy(false);
        }
    });
}

if (createAccountForm) {
    createAccountForm.addEventListener("submit", async event => {
        event.preventDefault();

        if (busy) return;

        const displayName =
            document.getElementById("signupDisplayName").value.trim();
        const email =
            document.getElementById("signupEmail").value.trim();
        const password =
            document.getElementById("signupPassword").value;

        if (!displayName) {
            signupMessage.textContent = "Please enter a display name.";
            return;
        }

        if (password.length < 6) {
            signupMessage.textContent =
                "Your password must contain at least 6 characters.";
            return;
        }

        setBusy(true);
        signupMessage.textContent = "Creating your account...";

        try {
            const { data, error } = await authClient.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        display_name: displayName
                    }
                }
            });

            if (error) throw error;

            localStorage.setItem("engineeringAI_displayName", displayName);

            if (data.session) {
                updateAuthUI(data.session);
                updateWelcomeName(displayName);
                signupMessage.textContent = "Account created successfully.";
            } else {
                signupMessage.textContent =
                    "Account created. Check your email to confirm your account.";
            }
        } catch (error) {
            signupMessage.textContent =
                error.message || "Account creation failed.";
        } finally {
            setBusy(false);
        }
    });
}

// Sign-in form handler
if (signInButton) {
    signInButton.addEventListener("click", async () => {
        if (busy) return;

        const email = authEmail.value.trim();
        const password = authPassword.value;
        const displayName = authDisplayName
            ? authDisplayName.value.trim()
            : "";

        if (!email || !authEmail.checkValidity()) {
            showMessage("Enter a valid email address.", true);
            authEmail.focus();
            return;
        }

        if (password.length < 6) {
            showMessage(
                "Enter a password with at least 6 characters.",
                true
            );
            authPassword.focus();
            return;
        }

        setBusy(true);
        showMessage("Signing in...");

        try {
            const { data, error } = await authClient.auth.signInWithPassword({
                email,
                password
            });

            if (error) throw error;

            if (displayName) {
                try {
                    localStorage.setItem("engineeringAI_displayName", displayName);
                } catch (storageError) {
                    console.warn("Could not save display name locally:", storageError);
                }
            }

            updateAuthUI(data.session);
            updateWelcomeName(
                displayName ||
                data.user?.user_metadata?.display_name ||
                data.user?.email?.split("@")[0] ||
                "there"
            );

            showMessage("Signed in successfully.");
            void loadConversationsFromCloud();
        } catch (error) {
            showMessage(
                error.message || "Sign in failed. Please check your details.",
                true
            );
        } finally {
            setBusy(false);
        }
    });
}

    } catch (error) {
        showMessage(
            error.message || "Authentication initialization failed.",
            true
        );
    }
})();



/* ===== Sign In / Create Account Screens ===== */

const showSignInScreen = () => {
    authForm.hidden = false;
    createAccountForm.hidden = true;

    showMessage("");
    if (signupMessage) signupMessage.textContent = "";
};

const showCreateAccountScreen = () => {
    authForm.hidden = true;
    createAccountForm.hidden = false;

    showMessage("");
    if (signupMessage) signupMessage.textContent = "";
};

// Existing Create Account button opens the separate registration screen.
if (signUpButton) {
    signUpButton.addEventListener("click", showCreateAccountScreen);
}

// Return to the sign-in screen.
if (backToSignInButton) {
    backToSignInButton.addEventListener("click", showSignInScreen);
}



/* ===== Personalized Welcome ===== */

function updateWelcomeName(displayName) {
    const welcomeHeading = document.getElementById("welcomeHeading");

    if (!welcomeHeading) return;

    const name = displayName.trim();

    welcomeHeading.textContent = name
        ? `Welcome, ${name}! What are we working on today?`
        : "What are we working on today?";
}

// Restore the saved display name when the page loads.
try {
    const savedName =
        localStorage.getItem("engineeringAI_displayName") || "";

    updateWelcomeName(savedName);
} catch (error) {
    updateWelcomeName("");
}



/* ===== Engineering AI Settings ===== */

(function initializeEngineeringAISettings() {
    const themeSelect = document.getElementById("themeSelect");
    const usernameInput = document.getElementById("usernameInput");
    const saveProfileButton = document.getElementById("saveProfileButton");
    const settingsMessage = document.getElementById("settingsMessage");

    const THEME_KEY = "engineeringAI_theme";
    const PROFILE_KEY = "engineeringAI_displayName";

    // Apply the selected theme.
    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
    }

    // Load saved settings.
    try {
        applyTheme(localStorage.getItem(THEME_KEY) || "light");

        const savedName = localStorage.getItem(PROFILE_KEY) || "";

        if (usernameInput) {
            usernameInput.value = savedName;
        }
    } catch (error) {
        applyTheme("light");
    }

    // Change theme immediately when the selection changes.
    if (themeSelect) {
        themeSelect.addEventListener("change", () => {
            applyTheme(themeSelect.value);
        });
    }

    // Save the display name.
    if (saveProfileButton) {
        saveProfileButton.addEventListener("click", () => {
            const displayName = usernameInput
                ? usernameInput.value.trim()
                : "";

            if (!displayName) {
                if (settingsMessage) {
                    settingsMessage.textContent =
                        "Please enter a display name first.";
                }
                return;
            }

            try {
                localStorage.setItem(PROFILE_KEY, displayName);

                if (settingsMessage) {
                    settingsMessage.textContent =
                        "Profile saved successfully.";
                }

                updateWelcomeName(displayName);

            } catch (error) {
                if (settingsMessage) {
                    settingsMessage.textContent =
                        "Could not save settings in this browser.";
                }
            }
        });
    }
})();
