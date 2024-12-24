from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    users[request.sid] = "Anonymous"

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    username = users.get(request.sid, "Anonymous")
    formatted_message = f"{username}: {data}"
    print(f"Sending formatted message: {formatted_message}")
    emit('new_message', formatted_message, broadcast=True)

@socketio.on('set_username')
def handle_username(username):
    print(f"Setting username for {request.sid} to {username}")
    users[request.sid] = username
    # Optionally notify others that a new user joined
    emit('new_message', f"{username} has joined the chat", broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        emit('new_message', f"{username} has left the chat", broadcast=True)

@socketio.on('typing')
def handle_typing(username):
    emit('user_typing', username, broadcast=True, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(username):
    emit('user_stop_typing', username, broadcast=True, include_self=False)

@socketio.on('image')
def handle_image(data):
    print(f"Received image from {data['username']}")
    emit('new_image', data, broadcast=True)

if __name__ == '__main__':
    print("Starting Flask server...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)