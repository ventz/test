"""
Tesla Car Chat Application
A simple two-user chat app deployed on Modal for Tesla web browsers.
"""

import modal
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from typing import List, Dict

# Create Modal app
app = modal.App("tesla-car-chat")

# Create Modal image with required dependencies
image = modal.Image.debian_slim().pip_install("fastapi[standard]")

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tesla Car Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 600px;
            height: 80vh;
            max-height: 700px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }

        .username-section {
            padding: 15px;
            background: #f7f7f7;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .username-section input {
            flex: 1;
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
        }

        .username-section button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }

        .username-section button:hover {
            background: #5568d3;
        }

        .current-user {
            padding: 10px 20px;
            background: #e8f5e9;
            color: #2e7d32;
            font-size: 14px;
            text-align: center;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }

        .message {
            margin-bottom: 15px;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-header {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
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
            padding: 12px 15px;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            word-wrap: break-word;
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
            padding: 15px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }

        .input-section input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 12px;
            font-size: 16px;
        }

        .input-section input:focus {
            outline: none;
            border-color: #667eea;
        }

        .input-section button {
            padding: 12px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
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
            padding: 5px 10px;
            background: #fff3cd;
            color: #856404;
            text-align: center;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            🚗 Tesla Car Chat 🚗
        </div>

        <div class="username-section" id="usernameSection">
            <input type="text" id="usernameInput" placeholder="Enter your username..." maxlength="20">
            <button onclick="setUsername()">Set Username</button>
        </div>

        <div class="current-user" id="currentUser" style="display: none;">
            Chatting as: <strong id="displayUsername"></strong>
        </div>

        <div class="status" id="status">Connected</div>

        <div class="messages-container" id="messagesContainer">
            <div style="text-align: center; color: #999; margin-top: 50px;">
                <h3>Welcome to Tesla Car Chat!</h3>
                <p style="margin-top: 10px;">Set your username to start chatting</p>
            </div>
        </div>

        <div class="input-section">
            <input type="text" id="messageInput" placeholder="Type a message..." disabled>
            <button id="sendButton" onclick="sendMessage()" disabled>Send</button>
        </div>
    </div>

    <script>
        let username = '';
        let lastMessageId = 0;
        let pollInterval;

        function setUsername() {
            const input = document.getElementById('usernameInput');
            const newUsername = input.value.trim();

            if (newUsername.length < 1) {
                alert('Please enter a username');
                return;
            }

            username = newUsername;
            document.getElementById('displayUsername').textContent = username;
            document.getElementById('currentUser').style.display = 'block';
            document.getElementById('usernameSection').style.display = 'none';
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendButton').disabled = false;
            document.getElementById('messageInput').focus();

            // Start polling for messages
            loadMessages();
            pollInterval = setInterval(loadMessages, 2000); // Poll every 2 seconds
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
                        }
                    });

                    // Scroll to bottom
                    container.scrollTop = container.scrollHeight;
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
            messageDiv.className = 'message' + (msg.username === username ? ' own' : '');

            const time = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

            messageDiv.innerHTML = `
                <div class="message-header">
                    <span class="message-username">${escapeHtml(msg.username)}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.message)}</div>
            `;

            container.appendChild(messageDiv);
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

        // Focus username input on load
        document.getElementById('usernameInput').focus();
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

    if not message.strip():
        return JSONResponse({"error": "Empty message"}, status_code=400)

    # Create message object
    msg = {
        "id": len(messages) + 1,
        "username": username[:20],  # Limit username length
        "message": message[:500],  # Limit message length
        "timestamp": datetime.utcnow().isoformat()
    }

    messages.append(msg)

    # Keep only last MAX_MESSAGES
    if len(messages) > MAX_MESSAGES:
        messages.pop(0)

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

# Expose the FastAPI app to Modal
@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return web_app
