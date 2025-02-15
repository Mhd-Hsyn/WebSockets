import socketio

sio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[]
)

sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path='socket.io'
)


@sio_server.event
async def connect(sid, environ, auth):
    print(f'{sid}: connected')
    await sio_server.emit('join', {'sid': sid})


@sio_server.event
async def chat(sid, message):
    print("sid==>",sid)
    print("message==>",message)
    await sio_server.emit('chat', {'sid': sid, 'message': message})


@sio_server.on("*")
async def handle_all_events(sid, event_name, data):
    print(f'Received event {event_name} from client {sid}: {data}')

@sio_server.event
async def disconnect(sid):
    print(f'{sid}: disconnected')
