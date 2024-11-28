import socketio

# Initialize Socket.IO server
sio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[],
    logger=True,
    engineio_logger=True
)

# Wrap the server with an ASGI app
sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path='socket.io'
)


@sio_server.event
async def connect(sid, environ, auth):
    print(f'{sid}: connected')
    await sio_server.emit('connection_success', {'sid': sid})


@sio_server.event
async def join_channel(sid, data):
    if not isinstance(data, dict):
        print(f"Invalid data format received: {data}")
        return

    # Log the received data for debugging
    print(f"Received join_channel data: {data}")

    channel_name = data.get('channel_name')
    user_data = data.get('user_data')

    print("channel_name __________________ ", channel_name)
    print("user_data __________________ ", user_data)

    if not channel_name or not user_data:
        print(f"Missing channel_name or user_data in: {data}")
        return

    session_data = {'channel_name': channel_name, 'user_data': user_data}
    await sio_server.save_session(sid, session_data)
    print(f"Session saved for {sid}: {session_data}")

    print(f"\n\n sid _________ ", sid, "\n\n")

    if channel_name:
        try:
            await sio_server.enter_room(sid, channel_name)
            print("\n\n Entering room \n\n")
            await sio_server.emit('user_joined', {'user_data': user_data}, room=channel_name, skip_sid=sid)
            print(f"\n\n COMPLETE JOIN \n\n")
        except Exception as e:
            print(f"Error during room entry: {e}")
    else:
        print(f"Error: Channel name is None. Cannot join room.")

@sio_server.event
async def leave_channel(sid):
    """
    Allow a user to leave a channel and notify other members.
    """
    session = await sio_server.get_session(sid)
    channel_name = session.get('channel_name')
    user_data = session.get('user_data')

    if channel_name:
        await sio_server.leave_room(sid, channel_name)
        await sio_server.emit('user_left', {'user_data': user_data}, room=channel_name)
        print(f'User {user_data} left channel {channel_name}')


@sio_server.event
async def send_message(sid, data):
    """
    Handle messages sent by a user to a channel.
    """
    session = await sio_server.get_session(sid)
    channel_name = session.get('channel_name')
    user_data = session.get('user_data')

    message = data.get('message')
    if not message or not channel_name:
        return

    # Broadcast the message to the channel
    await sio_server.emit('new_message', {'user_data': user_data, 'message': message}, room=channel_name)
    print(f'Message from {user_data} in channel {channel_name}: {message}')


@sio_server.event
async def disconnect(sid):
    """
    Handle disconnection and notify the channel.
    """
    session = await sio_server.get_session(sid)
    channel_name = session.get('channel_name')
    user_data = session.get('user_data')

    if channel_name:
        await sio_server.leave_room(sid, channel_name)
        await sio_server.emit('user_left', {'user_data': user_data}, room=channel_name)
    print(f'{sid} disconnected')
