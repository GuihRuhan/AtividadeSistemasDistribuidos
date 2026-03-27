import asyncio
import websockets
import json

clients = {}  # websocket -> username

async def broadcast_users():
    users = list(clients.values())
    message = json.dumps({
        "type": "users",
        "users": users
    })

    for client in clients:
        await client.send(message)


async def handler(websocket):
    try:
        # primeiro recebe o nome
        data = json.loads(await websocket.recv())
        username = data["username"]

        clients[websocket] = username
        print(f"{username} conectado")

        await broadcast_users()

        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "message":
                msg = data["message"]
                msg_id = data["id"]

                payload = {
                    "type": "message",
                    "from": username,
                    "message": msg,
                    "time": data["time"]
                }

                # envia para todos
                for client in clients:
                    await client.send(json.dumps(payload))

                # ACK
                await websocket.send(json.dumps({
                    "type": "ack",
                    "id": msg_id
                }))

    except:
        pass

    # desconectou
    if websocket in clients:
        print(f"{clients[websocket]} desconectado")
        del clients[websocket]
        await broadcast_users()


async def main():
    async with websockets.serve(handler, "localhost", 5050):
        print("Servidor rodando em wss://SEU-SERVIDOR.onrender.com")
        await asyncio.Future()

asyncio.run(main())