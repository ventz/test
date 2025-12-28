"""
Tesla Car Chat Application - Enhanced with Offline Support
Optimized for 2G/3G with reliability features and GPS
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

# In-memory storage for messages
messages: List[Dict] = []
MAX_MESSAGES = 100

# Create FastAPI app
web_app = FastAPI()

@web_app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve enhanced chat with offline support and GPS."""
    html_content = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="Tesla Chat"><link rel="manifest" href="/manifest.json"><title>Chat</title><style>* {margin:0;padding:0;box-sizing:border-box;}body {font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;background:#667eea;height:100vh;overflow:hidden;}.chat-container {background:white;width:100%;height:100vh;display:flex;flex-direction:column;overflow:hidden;}.username-section {padding:8px;background:#667eea;display:flex;gap:6px;align-items:center;}.username-section input {flex:1;padding:12px 14px;border:none;border-radius:8px;font-size:18px;background:white;color:#000;}.username-section button {padding:12px 20px;background:white;color:#667eea;border:none;border-radius:8px;cursor:pointer;font-size:18px;font-weight:bold;}.current-user {padding:4px 8px;background:#667eea;color:white;font-size:12px;text-align:center;font-weight:600;display:flex;justify-content:space-between;align-items:center;}.connection-status {display:flex;align-items:center;gap:4px;font-size:10px;}.status-dot {width:8px;height:8px;border-radius:50%;background:#4ade80;}.status-dot.offline {background:#ef4444;}.status-dot.slow {background:#facc15;}.messages-container {flex:1;overflow-y:auto;padding:8px;background:#fafafa;display:flex;flex-direction:column;}.message {margin-bottom:6px;animation:slideIn 0.2s ease-out;position:relative;}@keyframes slideIn {from {opacity:0;transform:translateY(-10px);}to {opacity:1;transform:translateY(0);}}.message-header {font-size:11px;color:#666;margin-bottom:3px;}.message-username {font-weight:bold;color:#667eea;}.message-time {color:#999;margin-left:8px;}.message-status {font-size:9px;color:#999;margin-left:4px;}.message-status.pending {color:#facc15;}.message-status.failed {color:#ef4444;cursor:pointer;}.message-content {background:white;padding:8px 12px;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1);word-wrap:break-word;font-size:16px;line-height:1.3;}.message.own .message-content {background:#667eea;color:white;margin-left:auto;}.message.own .message-username {color:#667eea;}.message.pending .message-content {opacity:0.6;}.message.failed .message-content {opacity:0.4;border:1px dashed #ef4444;}.location-message {background:#f0f9ff !important;border-left:3px solid #0ea5e9;color:#0c4a6e;}.location-link {color:#0284c7;text-decoration:underline;cursor:pointer;}.input-section {padding:6px;background:white;border-top:1px solid #e0e0e0;display:flex;gap:6px;}.input-section input {flex:1;padding:10px 12px;border:2px solid #ddd;border-radius:8px;font-size:18px;background:white;color:#000;}.input-section input:focus {outline:none;border-color:#667eea;}.input-section button {padding:10px 20px;background:#667eea;color:white;border:none;border-radius:8px;cursor:pointer;font-size:18px;font-weight:bold;transition:background 0.2s;}.input-section button:hover {background:#5568d3;}.input-section button:active {transform:scale(0.95);}.location-btn {background:#0ea5e9;padding:10px 16px;}.location-btn:hover {background:#0284c7;}.status {display:none;}.system-message {text-align:center;margin:8px 0;font-size:13px;color:#999;font-style:italic;}.system-message-content {background:rgba(0,0,0,0.05);display:inline-block;padding:4px 12px;border-radius:12px;}@media (max-width:768px) and (orientation:portrait) {body {background:#f5f5f5;}.chat-container {border-radius:0;background:#f5f5f5;display:flex;flex-direction:column;height:100vh;}.username-section {padding:12px 16px;padding-top:calc(12px + env(safe-area-inset-top));background:#fff;border-bottom:1px solid #e5e5e5;box-shadow:0 1px 3px rgba(0,0,0,0.1);order:0;}.username-section input {padding:14px 16px;border-radius:12px;font-size:17px;box-shadow:0 2px 8px rgba(0,0,0,0.08);background:#f7f7f7;}.username-section button {padding:14px 24px;border-radius:12px;font-size:17px;box-shadow:0 2px 8px rgba(0,0,0,0.08);background:#007AFF;color:white;}.current-user {padding:8px 16px;background:#007AFF;border-bottom:1px solid #0051D5;font-size:15px;color:#fff;order:1;text-align:center;font-weight:600;flex:0 0 auto;}.messages-container {padding:16px 16px 8px;background:#f5f5f5;flex-direction:column-reverse;justify-content:flex-start;order:2;flex:1 1 auto;overflow-y:auto;min-height:0;}.message {margin-top:12px;margin-bottom:0;max-width:75%;}.message-header {font-size:12px;margin-bottom:4px;}.message-content {padding:10px 14px;border-radius:18px;font-size:17px;line-height:1.35;box-shadow:0 1px 2px rgba(0,0,0,0.1);background:#fff;}.message.own {align-self:flex-end;}.message.own .message-content {background:#007AFF;color:white;margin-left:0;}.message.own .message-header {text-align:right;}.input-section {padding:12px 16px calc(95px + env(safe-area-inset-bottom));background:#fff;border-top:1px solid #e5e5e5;box-shadow:0 -2px 8px rgba(0,0,0,0.1);order:3;flex:0 0 auto;display:flex;gap:8px;position:relative;z-index:1000;}.input-section input {flex:1;padding:12px 16px;border-radius:20px;font-size:17px;border:1px solid #e5e5e5;background:#f7f7f7;}.input-section button {padding:12px 24px;border-radius:20px;font-size:17px;background:#007AFF;color:white;border:none;font-weight:600;}.location-btn {padding:12px 16px;background:#0ea5e9;}.input-section button:hover,.input-section button:active {background:#0051D5;}.location-btn:hover,.location-btn:active {background:#0284c7;}}@media (prefers-color-scheme:dark) {body {background:#1a1a2e;}.chat-container {background:#16213e;}.username-section {background:#0f3460;}.username-section input {background:#1a1a2e;color:#e0e0e0;border:1px solid #2d3561;}.username-section button {background:#0f3460;color:#e94560;}.current-user {background:#0f3460;border-bottom:1px solid #1a1a2e;}.messages-container {background:#0e1525;}.message-header {color:#a0a0a0;}.message-username {color:#4a9eff;}.message-time {color:#6a6a6a;}.message-content {background:#1a1a2e;color:#e0e0e0;box-shadow:0 2px 5px rgba(0,0,0,0.3);}.message.own .message-content {background:#0f3460;color:#fff;}.location-message {background:#1e3a5f !important;border-left:3px solid #0ea5e9;color:#93c5fd;}.input-section {background:#16213e;border-top:1px solid #0f3460;}.input-section input {background:#1a1a2e;color:#e0e0e0;border:2px solid #2d3561;}.input-section input:focus {border-color:#4a9eff;}.input-section button {background:#e94560;}.input-section button:hover {background:#c9325a;}.system-message {color:#888;}.system-message-content {background:rgba(255,255,255,0.05);}}@media (max-width:768px) and (orientation:portrait) and (prefers-color-scheme:dark) {body {background:#0e1525;}.chat-container {background:#0e1525;}.username-section {background:#16213e;border-bottom:1px solid #0f3460;box-shadow:0 1px 3px rgba(0,0,0,0.3);}.username-section input {background:#1a1a2e;color:#e0e0e0;border:1px solid #2d3561;box-shadow:0 2px 8px rgba(0,0,0,0.2);}.username-section button {background:#e94560;color:#fff;}.current-user {background:#0f3460;border-bottom:1px solid #1a1a2e;}.messages-container {background:#0e1525;}.message-content {background:#1a1a2e;color:#e0e0e0;}.message.own .message-content {background:#e94560;}.input-section {background:#16213e;border-top:1px solid #0f3460;box-shadow:0 -2px 8px rgba(0,0,0,0.3);}.input-section input {background:#1a1a2e;color:#e0e0e0;border:1px solid #2d3561;}.input-section button {background:#e94560;}}</style></head><body><div class="chat-container"><div class="username-section" id="usernameSection"><input type="text" id="usernameInput" placeholder="Your name..." maxlength="20"><button onclick="setUsername()">Start</button></div><div class="current-user" id="currentUser" style="display:none;cursor:pointer;" onclick="changeUsername()" title="Click to change username"><strong id="displayUsername"></strong><div class="connection-status"><span class="status-dot" id="statusDot"></span><span id="connectionText">Online</span></div></div><div class="input-section"><input type="text" id="messageInput" placeholder="Type a message..." disabled><button class="location-btn" id="locationBtn" onclick="shareLocation()" disabled title="Share location">📍</button><button id="sendButton" onclick="sendMessage()" disabled>Send</button></div><div class="status" id="status">Connected</div><div class="messages-container" id="messagesContainer"><div style="text-align:center;color:#999;padding:20px;"><p>Enter your name to start chatting</p></div></div></div><script>let username = '';let lastMessageId = 0;let pollInterval;let notificationsEnabled = false;let isWindowFocused = true;let isOnline = navigator.onLine;let messageQueue = [];let pendingMessages = new Map();// Track pending messageslet retryTimeouts = new Map();// Track retry timeouts// Load queue from localStoragefunction loadQueue() {try {const saved = localStorage.getItem('messageQueue');if (saved) {messageQueue = JSON.parse(saved);}}catch (e) {messageQueue = [];}}// Save queue to localStoragefunction saveQueue() {try {localStorage.setItem('messageQueue',JSON.stringify(messageQueue));}catch (e) {console.error('Failed to save queue');}}// Update connection status UIfunction updateConnectionStatus() {const dot = document.getElementById('statusDot');const text = document.getElementById('connectionText');if (!dot || !text) return;if (!isOnline) {dot.className = 'status-dot offline';text.textContent = 'Offline';}else if (navigator.connection) {const type = navigator.connection.effectiveType;if (type === 'slow-2g' || type === '2g') {dot.className = 'status-dot slow';text.textContent = '2G';}else if (type === '3g') {dot.className = 'status-dot slow';text.textContent = '3G';}else {dot.className = 'status-dot';text.textContent = 'Online';}}else {dot.className = 'status-dot';text.textContent = 'Online';}}// Monitor connection changeswindow.addEventListener('online',() => {isOnline = true;updateConnectionStatus();processQueue();// Process queued messages});window.addEventListener('offline',() => {isOnline = false;updateConnectionStatus();});if (navigator.connection) {navigator.connection.addEventListener('change',updateConnectionStatus);}const $ = (id) => document.getElementById(id);function escapeHtml(text) {const div = document.createElement('div');div.textContent = text;return div.innerHTML;}async function setUsername() {const input = $('usernameInput');const newUsername = input.value.trim();if (newUsername.length < 1) {alert('Please enter a username');return;}username = newUsername;localStorage.setItem('chatUsername',username);activateChat();}async function activateChat() {$('displayUsername').textContent = username;$('currentUser').style.display = 'flex';$('usernameSection').style.display = 'none';$('messageInput').disabled = false;$('sendButton').disabled = false;$('locationBtn').disabled = false;$('messageInput').focus();// Load any queued messagesloadQueue();// Send join system messageawait sendMessageToServer({username:'SYSTEM',message:`${username}joined the chat`,type:'system'});requestNotificationPermission();updateConnectionStatus();// Start polling for messagesloadMessages();pollInterval = setInterval(loadMessages,1500);// Process any queued messagesprocessQueue();}function changeUsername() {const newName = prompt('Enter new username:',username);if (newName && newName.trim()) {username = newName.trim();localStorage.setItem('chatUsername',username);$('displayUsername').textContent = username;}}async function sendMessage() {const input = $('messageInput');const message = input.value.trim();if (!message || !username) return;const messageData = {username:username,message:message,type:'regular'};// Clear input immediatelyinput.value = '';input.focus();// Send message (will queue if offline)await sendMessageToServer(messageData);}async function shareLocation() {if (!navigator.geolocation) {alert('Geolocation not supported');return;}const btn = $('locationBtn');btn.disabled = true;btn.textContent = '⌛';try {const position = await new Promise((resolve,reject) => {navigator.geolocation.getCurrentPosition(resolve,reject,{enableHighAccuracy:true,timeout:10000,maximumAge:0});});const lat = position.coords.latitude.toFixed(6);const lon = position.coords.longitude.toFixed(6);const mapsUrl = `https://maps.google.com/?q=${lat},${lon}`;const locationMessage = {username:username,message:`📍 Location:${lat},${lon}`,type:'location',location:{lat,lon,url:mapsUrl }};await sendMessageToServer(locationMessage);}catch (error) {alert('Could not get location:' + error.message);}finally {btn.disabled = false;btn.textContent = '📍';}}async function sendMessageToServer(messageData,tempId = null) {// Generate temporary ID for optimistic UIif (!tempId) {tempId = 'temp_' + Date.now() + '_' + Math.random();}// Show optimisticallyif (messageData.username === username && messageData.type !== 'system') {displayOptimisticMessage(messageData,tempId);}if (!isOnline) {// Queue for latermessageQueue.push({data:messageData,tempId:tempId,retries:0 });saveQueue();updateMessageStatus(tempId,'pending');return;}try {const response = await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json' },body:JSON.stringify(messageData)});if (response.ok) {const result = await response.json();updateMessageStatus(tempId,'sent');pendingMessages.delete(tempId);// Reload to get server IDsetTimeout(loadMessages,200);}else {throw new Error('Server error');}}catch (error) {// Queue for retrymessageQueue.push({data:messageData,tempId:tempId,retries:0 });saveQueue();updateMessageStatus(tempId,'failed');scheduleRetry(tempId);}}function scheduleRetry(tempId) {// Find message in queueconst queueItem = messageQueue.find(item => item.tempId === tempId);if (!queueItem) return;// Exponential backoff:2s,4s,8s,16s,32sconst delay = Math.min(32000,2000 * Math.pow(2,queueItem.retries));queueItem.retries++;const timeoutId = setTimeout(() => {retryMessage(tempId);},delay);retryTimeouts.set(tempId,timeoutId);}async function retryMessage(tempId) {const index = messageQueue.findIndex(item => item.tempId === tempId);if (index === -1) return;const queueItem = messageQueue[index];// Remove from queuemessageQueue.splice(index,1);saveQueue();// Retry sendawait sendMessageToServer(queueItem.data,tempId);}async function processQueue() {if (!isOnline || messageQueue.length === 0) return;// Process queue one at a timewhile (messageQueue.length > 0 && isOnline) {const queueItem = messageQueue[0];messageQueue.splice(0,1);saveQueue();await sendMessageToServer(queueItem.data,queueItem.tempId);// Small delay between sendsawait new Promise(resolve => setTimeout(resolve,500));}}function displayOptimisticMessage(messageData,tempId) {const container = $('messagesContainer');// Clear welcome messageif (container.children.length === 1 && container.children[0].style.textAlign === 'center') {container.innerHTML = '';}const messageDiv = document.createElement('div');messageDiv.className = 'message own pending';messageDiv.dataset.tempId = tempId;const time = new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',timeZone:'America/New_York'});const statusHtml = '<span class="message-status pending">⏳ Sending...</span>';if (messageData.type === 'location') {const loc = messageData.location;messageDiv.innerHTML = `<div class="message-header"><span class="message-username">${escapeHtml(messageData.username)}</span><span class="message-time">${time}</span>${statusHtml}</div><div class="message-content location-message">📍 <a href="${loc.url}" target="_blank" class="location-link">Location:${loc.lat},${loc.lon}</a></div>`;}else {messageDiv.innerHTML = `<div class="message-header"><span class="message-username">${escapeHtml(messageData.username)}</span><span class="message-time">${time}</span>${statusHtml}</div><div class="message-content">${escapeHtml(messageData.message)}</div>`;}container.prepend(messageDiv);pendingMessages.set(tempId,messageDiv);}function updateMessageStatus(tempId,status) {const messageDiv = pendingMessages.get(tempId);if (!messageDiv) return;const statusSpan = messageDiv.querySelector('.message-status');if (!statusSpan) return;messageDiv.classList.remove('pending','failed');if (status === 'sent') {statusSpan.innerHTML = '✓';statusSpan.className = 'message-status';// Remove after a momentsetTimeout(() => {if (statusSpan.parentNode) {statusSpan.remove();}},2000);}else if (status === 'pending') {messageDiv.classList.add('pending');statusSpan.innerHTML = '⏳ Queued';statusSpan.className = 'message-status pending';}else if (status === 'failed') {messageDiv.classList.add('failed');statusSpan.innerHTML = '✗ Retry';statusSpan.className = 'message-status failed';statusSpan.onclick = () => retryMessage(tempId);}}async function loadMessages() {try {const response = await fetch(`/messages?since=${lastMessageId}`);const data = await response.json();if (data.messages && data.messages.length > 0) {const container = $('messagesContainer');// Clear welcome message if it existsif (container.children.length === 1 && container.children[0].style.textAlign === 'center') {container.innerHTML = '';}data.messages.forEach(msg => {if (msg.id > lastMessageId) {appendMessage(msg);lastMessageId = msg.id;// Show notification if window not focusedif (!isWindowFocused && notificationsEnabled && msg.username !== username && msg.type !== 'system') {showNotification(msg);}}});}}catch (error) {// Silent fail on load errors}}function appendMessage(msg) {const container = $('messagesContainer');const messageDiv = document.createElement('div');// Handle system messagesif (msg.type === 'system') {messageDiv.className = 'system-message';messageDiv.innerHTML = `<div class="system-message-content">${escapeHtml(msg.message)}</div>`;container.prepend(messageDiv);return;}// Regular messagesmessageDiv.className = 'message' + (msg.username === username ? ' own' :'');const time = new Date(msg.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',timeZone:'America/New_York'});// Handle location messagesif (msg.type === 'location' && msg.location) {const loc = msg.location;messageDiv.innerHTML = `<div class="message-header"><span class="message-username">${escapeHtml(msg.username)}</span><span class="message-time">${time}</span></div><div class="message-content location-message">📍 <a href="${loc.url}" target="_blank" class="location-link">Location:${loc.lat},${loc.lon}</a></div>`;}else {messageDiv.innerHTML = `<div class="message-header"><span class="message-username">${escapeHtml(msg.username)}</span><span class="message-time">${time}</span></div><div class="message-content">${escapeHtml(msg.message)}</div>`;}container.prepend(messageDiv);}function showNotification(msg) {if ('Notification' in window && Notification.permission === 'granted') {const notification = new Notification(msg.username,{body:msg.message,icon:"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white' font-family='Arial'>💬</text></svg>",vibrate:[200,100,200],tag:'chat-message',requireInteraction:false});notification.onclick = () => {window.focus();notification.close();};}}// Event listeners$('messageInput').addEventListener('keypress',(e) => {if (e.key === 'Enter') sendMessage();});$('usernameInput').addEventListener('keypress',(e) => {if (e.key === 'Enter') setUsername();});// Service worker registrationif ('serviceWorker' in navigator && 'Notification' in window) {navigator.serviceWorker.register('/service-worker.js').then(registration => {if (Notification.permission === 'granted') {notificationsEnabled = true;}}).catch(e => {});}async function requestNotificationPermission() {if ('Notification' in window && Notification.permission === 'default') {const permission = await Notification.requestPermission();if (permission === 'granted') {notificationsEnabled = true;}}}// Track window focuswindow.addEventListener('focus',() => {isWindowFocused = true;});window.addEventListener('blur',() => {isWindowFocused = false;});// Check for saved usernameconst savedUsername = localStorage.getItem('chatUsername');if (savedUsername) {username = savedUsername;activateChat();setTimeout(requestNotificationPermission,1000);}else {$('usernameInput').focus();}// Handle disconnectwindow.addEventListener('beforeunload',() => {if (username) {const data = JSON.stringify({username:'SYSTEM',message:`${username}left the chat`,type:'system'});const blob = new Blob([data],{type:'application/json' });navigator.sendBeacon('/send',blob);}});</script></body></html>"""
    return HTMLResponse(content=html_content)

@web_app.post("/send")
async def send_message(request: Request):
    """Receive and store a new message."""
    data = await request.json()
    username = data.get("username", "Anonymous")
    message = data.get("message", "")
    msg_type = data.get("type", "regular")
    location = data.get("location", None)

    if not message.strip():
        return JSONResponse({"error": "Empty message"}, status_code=400)

    msg = {
        "id": len(messages) + 1,
        "username": username[:20],
        "message": message[:500],
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "type": msg_type
    }

    if location:
        msg["location"] = location

    messages.append(msg)

    if len(messages) > MAX_MESSAGES:
        messages.pop(0)

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
    """Serve minified service worker for notifications."""
    sw_content = """self.addEventListener('install',e=>{self.skipWaiting()});self.addEventListener('activate',e=>{e.waitUntil(clients.claim())});self.addEventListener('push',e=>{const d=e.data?e.data.json():{},t=d.title||'New Message',o={body:d.body||'You have a new message',icon:"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white' font-family='Arial'>💬</text></svg>",vibrate:[200,100,200],tag:'chat-message',requireInteraction:!1};e.waitUntil(self.registration.showNotification(t,o))});self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(clients.openWindow('/'))})"""
    return HTMLResponse(content=sw_content, media_type="application/javascript")

# Helper functions for persistent storage
def load_messages():
    """Load messages from volume storage."""
    global messages
    if MESSAGES_FILE.exists():
        try:
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
        except Exception as e:
            messages = []
    else:
        messages = []

def save_messages():
    """Save messages to volume storage."""
    try:
        MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f)
        volume.commit()
    except Exception as e:
        pass

# Expose the FastAPI app to Modal
@app.function(image=image, volumes={VOLUME_PATH: volume})
@modal.asgi_app()
def fastapi_app():
    load_messages()
    return web_app
