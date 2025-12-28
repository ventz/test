"""
Tesla Car Chat Application - Minified for 2G/3G
Optimized for slow connections with aggressive minification
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
    """Serve minified chat interface optimized for 2G/3G."""
    html_content = """<!DOCTYPE html><html lang=en><head><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><meta name=apple-mobile-web-app-capable content=yes><meta name=apple-mobile-web-app-status-bar-style content=black-translucent><meta name=apple-mobile-web-app-title content="Tesla Chat"><link rel=manifest href=/manifest.json><title>Chat</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;background:#667eea;height:100vh;overflow:hidden}.chat-container{background:#fff;width:100%;height:100vh;display:flex;flex-direction:column;overflow:hidden}.username-section{padding:8px;background:#667eea;display:flex;gap:6px;align-items:center}.username-section input{flex:1;padding:12px 14px;border:none;border-radius:8px;font-size:18px}.username-section button{padding:12px 20px;background:#fff;color:#667eea;border:none;border-radius:8px;cursor:pointer;font-size:18px;font-weight:700}.current-user{padding:4px 8px;background:#667eea;color:#fff;font-size:12px;text-align:center;font-weight:600}.messages-container{flex:1;overflow-y:auto;padding:8px;background:#fafafa;display:flex;flex-direction:column}.message{margin-bottom:6px;animation:s .2s ease-out}@keyframes s{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:translateY(0)}}.message-header{font-size:11px;color:#666;margin-bottom:3px}.message-username{font-weight:700;color:#667eea}.message-time{color:#999;margin-left:8px}.message-content{background:#fff;padding:8px 12px;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,.1);word-wrap:break-word;font-size:16px;line-height:1.3}.message.own .message-content{background:#667eea;color:#fff;margin-left:auto}.message.own .message-username{color:#667eea}.input-section{padding:6px;background:#fff;border-top:1px solid #e0e0e0;display:flex;gap:6px}.input-section input{flex:1;padding:10px 12px;border:2px solid #ddd;border-radius:8px;font-size:18px}.input-section input:focus{outline:0;border-color:#667eea}.input-section button{padding:10px 20px;background:#667eea;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:18px;font-weight:700;transition:background .2s}.input-section button:hover{background:#5568d3}.input-section button:active{transform:scale(.95)}.status{display:none}.system-message{text-align:center;margin:8px 0;font-size:13px;color:#999;font-style:italic}.system-message-content{background:rgba(0,0,0,.05);display:inline-block;padding:4px 12px;border-radius:12px}@media(max-width:768px)and (orientation:portrait){body{background:#f5f5f5}.chat-container{border-radius:0;background:#f5f5f5;display:flex;flex-direction:column;height:100vh}.username-section{padding:12px 16px;padding-top:calc(12px + env(safe-area-inset-top));background:#fff;border-bottom:1px solid #e5e5e5;box-shadow:0 1px 3px rgba(0,0,0,.1);order:0}.username-section input{padding:14px 16px;border-radius:12px;font-size:17px;box-shadow:0 2px 8px rgba(0,0,0,.08);background:#f7f7f7}.username-section button{padding:14px 24px;border-radius:12px;font-size:17px;box-shadow:0 2px 8px rgba(0,0,0,.08);background:#007AFF;color:#fff}.current-user{padding:8px 16px;background:#007AFF;border-bottom:1px solid #0051D5;font-size:15px;color:#fff;order:1;text-align:center;font-weight:600;flex:0 0 auto}.messages-container{padding:16px 16px 8px;background:#f5f5f5;flex-direction:column-reverse;justify-content:flex-start;order:2;flex:1 1 auto;overflow-y:auto;min-height:0}.message{margin-top:12px;margin-bottom:0;max-width:75%}.message-header{font-size:12px;margin-bottom:4px}.message-content{padding:10px 14px;border-radius:18px;font-size:17px;line-height:1.35;box-shadow:0 1px 2px rgba(0,0,0,.1);background:#fff}.message.own{align-self:flex-end}.message.own .message-content{background:#007AFF;color:#fff;margin-left:0}.message.own .message-header{text-align:right}.input-section{padding:12px 16px calc(95px + env(safe-area-inset-bottom));background:#fff;border-top:1px solid #e5e5e5;box-shadow:0 -2px 8px rgba(0,0,0,.1);order:3;flex:0 0 auto;display:flex;gap:8px;position:relative;z-index:1000}.input-section input{flex:1;padding:12px 16px;border-radius:20px;font-size:17px;border:1px solid #e5e5e5;background:#f7f7f7}.input-section button{padding:12px 24px;border-radius:20px;font-size:17px;background:#007AFF;color:#fff;border:none;font-weight:600}.input-section button:active,.input-section button:hover{background:#0051D5}}</style></head><body><div class=chat-container><div class=username-section id=usernameSection><input type=text id=usernameInput placeholder="Your name..." maxlength=20><button onclick=setUsername()>Start</button></div><div class=current-user id=currentUser style=display:none;cursor:pointer onclick=changeUsername() title="Click to change username"><strong id=displayUsername></strong></div><div class=input-section><input type=text id=messageInput placeholder="Type a message..." disabled><button id=sendButton onclick=sendMessage() disabled>Send</button></div><div class=status id=status>Connected</div><div class=messages-container id=messagesContainer><div style=text-align:center;color:#999;padding:20px><p>Enter your name to start chatting</div></div></div><script>let u='',l=0,p,n=!1,f=!0;const $=e=>document.getElementById(e),eh=t=>{const d=document.createElement('div');d.textContent=t;return d.innerHTML};async function setUsername(){const i=$('usernameInput'),v=i.value.trim();if(v.length<1){alert('Please enter a username');return}u=v;localStorage.setItem('chatUsername',u);activateChat()}async function activateChat(){$('displayUsername').textContent=u;$('currentUser').style.display='block';$('usernameSection').style.display='none';$('messageInput').disabled=!1;$('sendButton').disabled=!1;$('messageInput').focus();await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:'SYSTEM',message:`${u} joined the chat`,type:'system'})});requestNotificationPermission();loadMessages();p=setInterval(loadMessages,1500)}function changeUsername(){const v=prompt('Enter new username:',u);if(v&&v.trim()){u=v.trim();localStorage.setItem('chatUsername',u);$('displayUsername').textContent=u}}async function sendMessage(){const i=$('messageInput'),m=i.value.trim();if(!m||!u)return;const r=await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,message:m})});if(r.ok){i.value='';i.focus();loadMessages()}}async function loadMessages(){try{const r=await fetch(`/messages?since=${l}`),d=await r.json();if(d.messages&&d.messages.length>0){const c=$('messagesContainer');if(c.children.length===1&&c.children[0].style.textAlign==='center')c.innerHTML='';d.messages.forEach(m=>{if(m.id>l){appendMessage(m);l=m.id;if(!f&&n&&m.username!==u&&m.type!=='system')showNotification(m)}})}}catch(e){}}function appendMessage(m){const c=$('messagesContainer'),d=document.createElement('div');if(m.type==='system'){d.className='system-message';d.innerHTML=`<div class=system-message-content>${eh(m.message)}</div>`;c.prepend(d);return}d.className='message'+(m.username===u?' own':'');const t=new Date(m.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',timeZone:'America/New_York'});d.innerHTML=`<div class=message-header><span class=message-username>${eh(m.username)}</span> <span class=message-time>${t}</span></div><div class=message-content>${eh(m.message)}</div>`;c.prepend(d)}function showNotification(m){if('Notification'in window&&Notification.permission==='granted'){const x=new Notification(m.username,{body:m.message,icon:"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23667eea'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white' font-family='Arial'>💬</text></svg>",vibrate:[200,100,200],tag:'chat-message',requireInteraction:!1});x.onclick=()=>{window.focus();x.close()}}}$('messageInput').addEventListener('keypress',e=>{if(e.key==='Enter')sendMessage()});$('usernameInput').addEventListener('keypress',e=>{if(e.key==='Enter')setUsername()});if('serviceWorker'in navigator&&'Notification'in window)navigator.serviceWorker.register('/service-worker.js').then(r=>{if(Notification.permission==='granted')n=!0}).catch(e=>{});async function requestNotificationPermission(){if('Notification'in window&&Notification.permission==='default'){const p=await Notification.requestPermission();if(p==='granted')n=!0}}window.addEventListener('focus',()=>f=!0);window.addEventListener('blur',()=>f=!1);const s=localStorage.getItem('chatUsername');if(s){u=s;activateChat();setTimeout(requestNotificationPermission,1e3)}else $('usernameInput').focus();window.addEventListener('beforeunload',()=>{if(u){const d=JSON.stringify({username:'SYSTEM',message:`${u} left the chat`,type:'system'}),b=new Blob([d],{type:'application/json'});navigator.sendBeacon('/send',b)}})</script></body></html>"""
    return HTMLResponse(content=html_content)

@web_app.post("/send")
async def send_message(request: Request):
    """Receive and store a new message."""
    data = await request.json()
    username = data.get("username", "Anonymous")
    message = data.get("message", "")
    msg_type = data.get("type", "regular")

    if not message.strip():
        return JSONResponse({"error": "Empty message"}, status_code=400)

    msg = {
        "id": len(messages) + 1,
        "username": username[:20],
        "message": message[:500],
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "type": msg_type
    }

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
