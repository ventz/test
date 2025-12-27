# 🚗 Tesla Car Chat App

A simple, lightweight two-user chat application designed for Tesla web browsers, deployed on Modal. Takes advantage of Tesla's unlimited internet connectivity in Canada!

## Features

- **Simple & Fast**: Lightweight HTML/CSS/JS frontend optimized for Tesla browsers
- **Real-time Chat**: Auto-refreshing messages every 2 seconds
- **Custom Usernames**: Set your own username to identify yourself
- **Beautiful UI**: Modern gradient design with smooth animations
- **No Database Required**: Uses in-memory storage (keeps last 100 messages)
- **Serverless**: Deployed on Modal for zero-maintenance hosting

## Quick Start

### Prerequisites

1. Install Modal CLI:
```bash
pip install modal
```

2. Set up Modal account:
```bash
modal setup
```

### Deploy to Modal

1. Deploy the application:
```bash
modal deploy modal_chat.py
```

2. Modal will output a URL like: `https://YOUR-USERNAME--tesla-car-chat-fastapi-app.modal.run`

3. Open this URL in your Tesla browser!

### For Development/Testing

Run locally with hot-reload:
```bash
modal serve modal_chat.py
```

## How to Use in Your Tesla

1. **In Your Tesla**: Open the web browser and navigate to your Modal URL
2. **Set Username**: Enter a username (e.g., "Tesla 1" or "Model 3")
3. **Start Chatting**: Type messages and hit Send or press Enter
4. **The Other Tesla**: Do the same with a different username

The chat updates automatically every 2 seconds, so both cars will see messages in near real-time!

## Architecture

- **Backend**: FastAPI running on Modal (serverless)
- **Frontend**: Single-page HTML with vanilla JavaScript
- **Storage**: In-memory (messages persist while the Modal container is running)
- **Updates**: Long-polling every 2 seconds for new messages

## Technical Details

### Endpoints

- `GET /` - Serves the chat interface
- `POST /send` - Send a new message
- `GET /messages?since={id}` - Get messages since a specific ID
- `GET /health` - Health check endpoint

### Message Format

```json
{
  "id": 1,
  "username": "Tesla 1",
  "message": "Hello from the road!",
  "timestamp": "2025-12-27T18:30:00.000000"
}
```

### Limitations

- Messages are stored in memory (resets on deployment)
- Keeps only the last 100 messages
- Username limited to 20 characters
- Message limited to 500 characters
- Designed for 2 users (but supports more)

## Tips for Tesla Browsers

- **Bookmark the URL**: Save it for quick access
- **Landscape Mode**: Works great in Tesla's landscape display
- **Touch-Friendly**: Large buttons designed for touch interaction
- **Auto-Scroll**: Messages auto-scroll to the latest one

## Customization

Want to modify the app? Key sections:

- **Styling**: Edit the `<style>` section in `modal_chat.py`
- **Poll Interval**: Change `pollInterval = setInterval(loadMessages, 2000)` to adjust refresh rate
- **Message Limit**: Modify `MAX_MESSAGES = 100` in the Python code
- **Colors**: Update the gradient colors in CSS

## Cost

Modal offers a generous free tier. This simple chat app should stay well within free limits for personal use.

## Troubleshooting

**Messages not updating?**
- Check your internet connection
- Refresh the page
- Verify the Modal app is running: `modal app list`

**Can't set username?**
- Make sure you've entered at least 1 character
- Try refreshing the page

**URL not working?**
- Verify deployment succeeded: `modal app list`
- Check the URL is correct
- Try redeploying: `modal deploy modal_chat.py`

## License

MIT License - Feel free to modify and use as you wish!

## Contributing

This is a simple project, but improvements are welcome! Some ideas:
- Add message persistence (SQLite, Redis, etc.)
- Support for more than 2 users
- Message history pagination
- User typing indicators
- Read receipts

---

Enjoy chatting from your Tesla! 🚗⚡