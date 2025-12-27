"""
Tesla Car Chat Application
A simple two-user chat app deployed on Modal for Tesla web browsers.
"""

import modal
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from typing import List, Dict
import json
import pathlib

# Create Modal app
app = modal.App("tesla-car-chat")

# Create Modal image with required dependencies
image = modal.Image.debian_slim().pip_install("fastapi[standard]")

# Create Volume for persistent storage
volume = modal.Volume.from_name("chat-history", create_if_missing=True, version=2)
VOLUME_PATH = "/data"
MESSAGES_FILE = pathlib.Path(VOLUME_PATH) / "messages.json"

# In-memory storage for messages (module-level for persistence)
messages: List[Dict] = []
MAX_MESSAGES = 100  # Keep only last 100 messages

# Create FastAPI app
web_app = FastAPI()

@web_app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the main chat interface."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Tesla Chat">
    <link rel="manifest" href="/manifest.json">
    <title>Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #667eea;
            height: 100vh;
            overflow: hidden;
        }

        .chat-container {
            background: white;
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .username-section {
            padding: 8px;
            background: #667eea;
            display: flex;
            gap: 6px;
            align-items: center;
        }

        .username-section input {
            flex: 1;
            padding: 12px 14px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
        }

        .username-section button {
            padding: 12px 20px;
            background: white;
            color: #667eea;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
        }

        .current-user {
            padding: 4px 8px;
            background: #667eea;
            color: white;
            font-size: 12px;
            text-align: center;
            font-weight: 600;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
            background: #fafafa;
            display: flex;
            flex-direction: column;
        }

        .message {
            margin-bottom: 6px;
            animation: slideIn 0.2s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-header {
            font-size: 11px;
            color: #666;
            margin-bottom: 3px;
        }

        .message-username {
            font-weight: bold;
            color: #667eea;
        }

        .message-time {
            color: #999;
            margin-left: 8px;
        }

        .message-content {
            background: white;
            padding: 8px 12px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            word-wrap: break-word;
            font-size: 16px;
            line-height: 1.3;
        }

        .message.own .message-content {
            background: #667eea;
            color: white;
            margin-left: auto;
        }

        .message.own .message-username {
            color: #667eea;
        }

        .input-section {
            padding: 6px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 6px;
        }

        .input-section input {
            flex: 1;
            padding: 10px 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 18px;
        }

        .input-section input:focus {
            outline: none;
            border-color: #667eea;
        }

        .input-section button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            transition: background 0.2s;
        }

        .input-section button:hover {
            background: #5568d3;
        }

        .input-section button:active {
            transform: scale(0.95);
        }

        .status {
            display: none;
        }

        .system-message {
            text-align: center;
            margin: 8px 0;
            font-size: 13px;
            color: #999;
            font-style: italic;
        }

        .system-message-content {
            background: rgba(0,0,0,0.05);
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
        }

        /* iPhone-specific styles - portrait mode, smaller screens */
        @media (max-width: 768px) and (orientation: portrait) {
            body {
                background: #f5f5f5;
            }

            .chat-container {
                border-radius: 0;
                background: #f5f5f5;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }

            .username-section {
                padding: 12px 16px;
                padding-top: calc(12px + env(safe-area-inset-top));
                background: #fff;
                border-bottom: 1px solid #e5e5e5;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                order: 0;
            }

            .username-section input {
                padding: 14px 16px;
                border-radius: 12px;
                font-size: 17px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                background: #f7f7f7;
            }

            .username-section button {
                padding: 14px 24px;
                border-radius: 12px;
                font-size: 17px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                background: #007AFF;
                color: white;
            }

            .current-user {
                padding: 8px 16px;
                background: #007AFF;
                border-bottom: 1px solid #0051D5;
                font-size: 15px;
                color: #fff;
                order: 1;
                text-align: center;
                font-weight: 600;
                flex: 0 0 auto;
            }

            .messages-container {
                padding: 16px;
                padding-bottom: 8px;
                background: #f5f5f5;
                flex-direction: column-reverse;
                justify-content: flex-start;
                order: 2;
                flex: 1 1 auto;
                overflow-y: auto;
                min-height: 0;
            }

            .message {
                margin-top: 12px;
                margin-bottom: 0;
                max-width: 75%;
            }

            .message-header {
                font-size: 12px;
                margin-bottom: 4px;
            }

            .message-content {
                padding: 10px 14px;
                border-radius: 18px;
                font-size: 17px;
                line-height: 1.35;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                background: #fff;
            }

            .message.own {
                align-self: flex-end;
            }

            .message.own .message-content {
                background: #007AFF;
                color: white;
                margin-left: 0;
            }

            .message.own .message-header {
                text-align: right;
            }

            .input-section {
                padding: 12px 16px;
                padding-bottom: calc(80px + env(safe-area-inset-bottom));
                background: #fff;
                border-top: 1px solid #e5e5e5;
                box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
                order: 3;
                flex: 0 0 auto;
                display: flex;
                gap: 8px;
                position: relative;
                z-index: 1000;
            }

            .input-section input {
                flex: 1;
                padding: 12px 16px;
                border-radius: 20px;
                font-size: 17px;
                border: 1px solid #e5e5e5;
                background: #f7f7f7;
            }

            .input-section button {
                padding: 12px 24px;
                border-radius: 20px;
                font-size: 17px;
                background: #007AFF;
                color: white;
                border: none;
                font-weight: 600;
            }

            .input-section button:hover {
                background: #0051D5;
            }

            .input-section button:active {
                background: #0051D5;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="username-section" id="usernameSection">
            <input type="text" id="usernameInput" placeholder="Your name..." maxlength="20">
            <button onclick="setUsername()">Start</button>
        </div>

        <div class="current-user" id="currentUser" style="display: none; cursor: pointer;" onclick="changeUsername()" title="Click to change username">
            <strong id="displayUsername"></strong>
        </div>

        <div class="input-section">
            <input type="text" id="messageInput" placeholder="Type a message..." disabled>
            <button id="sendButton" onclick="sendMessage()" disabled>Send</button>
        </div>

        <div class="status" id="status">Connected</div>

        <div class="messages-container" id="messagesContainer">
            <div style="text-align: center; color: #999; padding: 20px;">
                <p>Enter your name to start chatting</p>
            </div>
        </div>
    </div>

    <script>
        let username = '';
        let lastMessageId = 0;
        let pollInterval;

        async function setUsername() {
            const input = document.getElementById('usernameInput');
            const newUsername = input.value.trim();

            if (newUsername.length < 1) {
                alert('Please enter a username');
                return;
            }

            username = newUsername;

            // Save username to localStorage for future visits
            localStorage.setItem('chatUsername', username);

            activateChat();
        }

        async function activateChat() {
            document.getElementById('displayUsername').textContent = username;
            document.getElementById('currentUser').style.display = 'block';
            document.getElementById('usernameSection').style.display = 'none';
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendButton').disabled = false;
            document.getElementById('messageInput').focus();

            // Send join system message
            await fetch('/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: 'SYSTEM',
                    message: `${username} joined the chat`,
                    type: 'system'
                })
            });

            // Request notification permission
            requestNotificationPermission();

            // Start polling for messages
            loadMessages();
            pollInterval = setInterval(loadMessages, 2000); // Poll every 2 seconds
        }

        function changeUsername() {
            // Allow user to change their username by clicking on it
            const newName = prompt('Enter new username:', username);
            if (newName && newName.trim()) {
                username = newName.trim();
                localStorage.setItem('chatUsername', username);
                document.getElementById('displayUsername').textContent = username;
            }
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message || !username) return;

            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username,
                        message: message
                    })
                });

                if (response.ok) {
                    input.value = '';
                    input.focus(); // Keep keyboard open for next message
                    loadMessages(); // Immediately load messages after sending
                }
            } catch (error) {
                console.error('Error sending message:', error);
                updateStatus('Error sending message', true);
            }
        }

        async function loadMessages() {
            try {
                const response = await fetch(`/messages?since=${lastMessageId}`);
                const data = await response.json();

                if (data.messages && data.messages.length > 0) {
                    const container = document.getElementById('messagesContainer');

                    // Clear welcome message if it exists
                    if (container.children.length === 1 && container.children[0].style.textAlign === 'center') {
                        container.innerHTML = '';
                    }

                    data.messages.forEach(msg => {
                        if (msg.id > lastMessageId) {
                            appendMessage(msg);
                            lastMessageId = msg.id;

                            // Show notification if window not focused and message is from another user
                            if (!isWindowFocused && notificationsEnabled && msg.username !== username && msg.type !== 'system') {
                                showNotification(msg);
                            }
                        }
                    });
                }

                updateStatus('Connected', false);
            } catch (error) {
                console.error('Error loading messages:', error);
                updateStatus('Connection error', true);
            }
        }

        function appendMessage(msg) {
            const container = document.getElementById('messagesContainer');
            const messageDiv = document.createElement('div');

            // Handle system messages
            if (msg.type === 'system') {
                messageDiv.className = 'system-message';
                messageDiv.innerHTML = `
                    <div class="system-message-content">${escapeHtml(msg.message)}</div>
                `;
                container.prepend(messageDiv);
                return;
            }

            // Regular messages
            messageDiv.className = 'message' + (msg.username === username ? ' own' : '');

            const time = new Date(msg.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute:'2-digit',
                timeZone: 'America/New_York'
            });

            messageDiv.innerHTML = `
                <div class="message-header">
                    <span class="message-username">${escapeHtml(msg.username)}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.message)}</div>
            `;

            container.prepend(messageDiv);
        }

        function showNotification(msg) {
            if ('Notification' in window && Notification.permission === 'granted') {
                const notification = new Notification(`${msg.username}`, {
                    body: msg.message,
                    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white' font-family='Arial'>💬</text></svg>",
                    badge: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/></svg>",
                    vibrate: [200, 100, 200],
                    tag: 'chat-message',
                    requireInteraction: false
                });

                notification.onclick = function() {
                    window.focus();
                    notification.close();
                };
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function updateStatus(text, isError) {
            const status = document.getElementById('status');
            status.textContent = text;
            status.style.background = isError ? '#f8d7da' : '#d4edda';
            status.style.color = isError ? '#721c24' : '#155724';
        }

        // Enable sending message with Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Enable setting username with Enter key
        document.getElementById('usernameInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                setUsername();
            }
        });

        // Register service worker and request notification permission
        let notificationsEnabled = false;
        if ('serviceWorker' in navigator && 'Notification' in window) {
            navigator.serviceWorker.register('/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);

                    // Request notification permission after username is set
                    if (Notification.permission === 'default') {
                        // Will ask for permission after user sets username
                    } else if (Notification.permission === 'granted') {
                        notificationsEnabled = true;
                    }
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }

        async function requestNotificationPermission() {
            if ('Notification' in window && Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    notificationsEnabled = true;
                    console.log('Notifications enabled');
                }
            }
        }

        // Track if window is focused
        let isWindowFocused = true;
        window.addEventListener('focus', () => {
            isWindowFocused = true;
        });
        window.addEventListener('blur', () => {
            isWindowFocused = false;
        });

        // Check for saved username on page load
        const savedUsername = localStorage.getItem('chatUsername');
        if (savedUsername) {
            username = savedUsername;
            activateChat();
            // Request notifications after auto-login
            setTimeout(requestNotificationPermission, 1000);
        } else {
            // Focus username input if no saved username
            document.getElementById('usernameInput').focus();
        }

        // Handle disconnect
        window.addEventListener('beforeunload', function() {
            if (username) {
                // Send disconnect system message
                const data = JSON.stringify({
                    username: 'SYSTEM',
                    message: `${username} left the chat`,
                    type: 'system'
                });
                const blob = new Blob([data], { type: 'application/json' });
                navigator.sendBeacon('/send', blob);
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@web_app.post("/send")
async def send_message(request: Request):
    """Receive and store a new message."""
    data = await request.json()
    username = data.get("username", "Anonymous")
    message = data.get("message", "")
    msg_type = data.get("type", "regular")  # Support system messages

    if not message.strip():
        return JSONResponse({"error": "Empty message"}, status_code=400)

    # Create message object
    msg = {
        "id": len(messages) + 1,
        "username": username[:20],  # Limit username length
        "message": message[:500],  # Limit message length
        "timestamp": datetime.utcnow().isoformat() + 'Z',  # Add Z to indicate UTC
        "type": msg_type  # Include message type
    }

    messages.append(msg)

    # Keep only last MAX_MESSAGES
    if len(messages) > MAX_MESSAGES:
        messages.pop(0)

    # Save to persistent storage
    save_messages()

    return JSONResponse({"success": True, "message_id": msg["id"]})

@web_app.get("/messages")
async def get_messages(since: int = 0):
    """Get messages since a specific message ID."""
    new_messages = [msg for msg in messages if msg["id"] > since]
    return JSONResponse({"messages": new_messages})

@web_app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "message_count": len(messages)})

@web_app.get("/manifest.json")
async def get_manifest():
    """Serve PWA manifest for Add to Home Screen."""
    manifest = {
        "name": "Tesla Car Chat",
        "short_name": "Chat",
        "description": "Real-time chat for Tesla cars",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#667eea",
        "icons": [
            {
                "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white' font-family='Arial'>💬</text></svg>",
                "sizes": "512x512",
                "type": "image/svg+xml"
            }
        ]
    }
    return JSONResponse(manifest)

@web_app.get("/service-worker.js")
async def get_service_worker():
    """Serve service worker for notifications."""
    sw_content = """
self.addEventListener('install', (event) => {
    console.log('Service worker installed');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('Service worker activated');
    event.waitUntil(clients.claim());
});

self.addEventListener('push', (event) => {
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'New Message';
    const options = {
        body: data.body || 'You have a new message',
        icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white' font-family='Arial'>💬</text></svg>",
        badge: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/></svg>",
        vibrate: [200, 100, 200],
        tag: 'chat-message',
        requireInteraction: false
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});
"""
    return HTMLResponse(content=sw_content, media_type="application/javascript")

# Helper functions for persistent storage
def load_messages():
    """Load messages from volume storage."""
    global messages
    if MESSAGES_FILE.exists():
        try:
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
                print(f"Loaded {len(messages)} messages from storage")
        except Exception as e:
            print(f"Error loading messages: {e}")
            messages = []
    else:
        print("No existing messages file, starting fresh")
        messages = []

def save_messages():
    """Save messages to volume storage."""
    try:
        MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f)
        volume.commit()
        print(f"Saved {len(messages)} messages to storage")
    except Exception as e:
        print(f"Error saving messages: {e}")

# Expose the FastAPI app to Modal
@app.function(image=image, volumes={VOLUME_PATH: volume})
@modal.asgi_app()
def fastapi_app():
    load_messages()  # Load existing messages on startup
    return web_app
