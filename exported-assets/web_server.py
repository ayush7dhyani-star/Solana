"""
FastAPI Web Server - CLOUD DEPLOYMENT READY
"""
import os
from datetime import datetime
from typing import Optional, List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


class StartScanRequest(BaseModel):
    duration: int = 3600
    concurrency: int = 100
    batch_size: int = 50
    demo_mode: bool = True


class ScanResponse(BaseModel):
    status: str
    message: str
    scan_id: Optional[str] = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)


scan_running = False
connection_manager = ConnectionManager()

app = FastAPI(title="Solana Discovery Bot - Cloud Edition", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    try:
        with open('dashboard.html', 'r') as f:
            return f.read()
    except:
        return "<h1>🔍 Solana Discovery Bot - Cloud Edition</h1><p>Upload dashboard.html</p>"


@app.get("/api/status")
async def get_status():
    return {"running": scan_running, "mode": "LIVE - Cloud Hosted"}


@app.post("/api/scan/start")
async def start_scan(request: StartScanRequest):
    global scan_running
    if scan_running:
        raise HTTPException(400, "Already running")
    scan_running = True
    return ScanResponse(status="success", message="Scan started!", scan_id=f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")


@app.post("/api/scan/stop")
async def stop_scan():
    global scan_running
    scan_running = False
    return {"status": "success"}


@app.get("/api/wallets/funded")
async def get_funded_wallets():
    return []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        await websocket.send_json({"type": "connected", "data": {"message": "Cloud connected"}})
        while True:
            await websocket.receive_text()
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "cloud": True}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
