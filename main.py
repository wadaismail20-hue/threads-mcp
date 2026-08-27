import os
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.requests import Request

# Inisialisasi FastMCP
mcp = FastMCP("Threads MCP Server")

THREADS_ACCESS_TOKEN = "THAAUaUiZAzuSFBYlpVeWdLb2hLYlAwMUNUZAW5OY1Y0QnBkY1p2cDgwRFZAIWkZARTXR3X01QenRueTRuTXpXeGYwalktOGVWRldueWhfLVlrdnI5LWd1a3RnWHBwYXdKSHh3U21BWVlqcGRXQXdPOFFpNmE0d2dRUTgyMjk2b2JWeEZAERHFfYWVkaEI3ck51QWsZD"
THREADS_USER_ID = "1436315018311969"

@mcp.tool()
def get_threads_profile() -> dict:
    """Mengambil data profil akun Threads."""
    url = f"https://graph.threads.net/v1.0/me?fields=id,username,threads_profile_picture_url,threads_biography&access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    return response.json()

@mcp.tool()
def get_recent_threads(limit: int = 5) -> dict:
    """Mengambil daftar postingan Threads terbaru."""
    url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads?fields=id,text,timestamp,permalink&limit={limit}&access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    return response.json()

@mcp.tool()
def publish_thread(text: str) -> dict:
    """Mempublikasikan postingan teks baru ke Threads."""
    create_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
    create_payload = {
        "media_type": "TEXT",
        "text": text,
        "access_token": THREADS_ACCESS_TOKEN
    }
    create_res = requests.post(create_url, data=create_payload).json()
    creation_id = create_res.get("id")

    if not creation_id:
        return {"status": "error", "error_details": create_res}

    publish_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": THREADS_ACCESS_TOKEN
    }
    publish_res = requests.post(publish_url, data=publish_payload).json()
    return {"status": "success", "response": publish_res}

# Setup Aplikasi FastAPI
app = FastAPI()

# Tambahkan CORS agar diizinkan oleh Google Gemini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Transport SSE MCP
sse = SseServerTransport("/messages/")

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return PlainTextResponse("Threads MCP Server is running!")

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp._mcp_server.run(
            streams[0], streams[1], mcp._mcp_server.create_initialization_options()
        )

@app.post("/messages/")
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
