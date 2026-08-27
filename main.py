import os
import requests
from mcp.server.fastmcp import FastMCP

# Baca port dinamis dari Render (default 8000) dan bind ke 0.0.0.0
port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Threads MCP Server", host="0.0.0.0", port=port)

THREADS_ACCESS_TOKEN = "THAAUaUiZAzuSFBYlpYemhOcDl4X2dva2FuRDFIRFpsZAFAzSHBNcTRUVnlWVzhpMDduaUhnTUU2ZAW85NkpMR042ZAVpDdjNlbTRFdGNZAdUNqUzZAnRHRZAdTlvSE1EMVVzbGxMWFNYNEhNVmlOZAUlqRnhlV2dTWDdIaVRLWHJRaHN5XzNZAeEN2eGxMV0Q5YXh4NjQZD"
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

if __name__ == "__main__":
    mcp.run(transport="sse")
