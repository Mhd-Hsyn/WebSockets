import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sockets import sio_app,sio_server

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/home')
async def home():
    return {'message': 'Hello👋 Developers💻'}

@app.get('/emit-chat')
async def emit_chat(channel_name:str):
    print("channel_name===>",channel_name)
    await sio_server.emit(channel_name, {'sid': "123", 'message': "Hello how are you?"})
    return {"message": "Chat event emitted successfully"}


@app.post('/emit_chat/')
async def emit_chat(message_obj: dict):
    channel_name = message_obj['message_obj']['channel_name']
    message = message_obj['message_obj']['message']
    await sio_server.emit(channel_name, {'message': message})
    return {"message": "Chat event emitted successfully"}



app.mount('/', app=sio_app)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)

