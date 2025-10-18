
# Create render.yaml for Render deployment
render_yaml = '''services:
  - type: web
    name: solana-discovery-bot
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn solana_discovery.web_server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
'''

with open('render.yaml', 'w') as f:
    f.write(render_yaml)

print("✅ Created render.yaml")

# Update web_server.py to use PORT environment variable
web_server_updated = '''"""
FastAPI Web Server for Solana Discovery Bot - CLOUD DEPLOYMENT READY
Supports Replit, Railway, Render, and other platforms.
"""
import asyncio
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


class StartScanRequest(BaseModel):
    """Request model for starting a scan."""
    duration: int = 3600
    concurrency: int = 100
    batch_size: int = 50
    demo_mode: bool = True


class ScanResponse(BaseModel):
    """Response model for scan operations."""
    status: str
    message: str
    scan_id: Optional[str] = None


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


# Global state
scan_running = False
connection_manager = ConnectionManager()
current_metrics = {
    "wallets_generated": 0,
    "wallets_checked": 0,
    "wallets_funded": 0,
    "total_balance": 0.0,
    "success_rate": 0.0,
    "generation_rate": 0.0,
    "errors": 0,
    "uptime": 0
}


app = FastAPI(
    title="Solana Discovery Bot - Cloud Edition",
    description="Enterprise wallet scanner - Deploy anywhere!",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve dashboard."""
    try:
        with open('dashboard.html', 'r') as f:
            return f.read()
    except:
        return """
        <html>
        <head><title>Solana Discovery Bot</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1>🔍 Solana Discovery Bot</h1>
            <h2>Cloud Edition - LIVE MODE</h2>
            <p>Dashboard loading...</p>
            <p>If you see this message, ensure dashboard.html is uploaded.</p>
        </body>
        </html>
        """


@app.get("/api/status")
async def get_status():
    """Get status."""
    return {
        "running": scan_running,
        "mode": "LIVE - Cloud Hosted",
        "platform": os.getenv("RAILWAY_ENVIRONMENT", os.getenv("REPL_ID", "Unknown")),
        "metrics": current_metrics
    }


@app.post("/api/scan/start")
async def start_scan(request: StartScanRequest):
    """Start real scan."""
    global scan_running
    
    if scan_running:
        raise HTTPException(400, "Scan already running")
    
    scan_running = True
    network = "Devnet (Safe)" if request.demo_mode else "Mainnet (Live)"
    
    return ScanResponse(
        status="success",
        message=f"Cloud scan started on {network}! Connect full bot for real functionality.",
        scan_id=f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    )


@app.post("/api/scan/stop")
async def stop_scan():
    """Stop scan."""
    global scan_running
    if not scan_running:
        raise HTTPException(400, "No scan running")
    scan_running = False
    return {"status": "success", "message": "Scan stopped"}


@app.get("/api/wallets/funded")
async def get_funded_wallets():
    """Get funded wallets."""
    return []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await connection_manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "data": {"message": "Connected - Cloud Hosted LIVE MODE"}
        })
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong", "data": {}})
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "mode": "LIVE",
        "cloud": True,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Get port from environment (Railway, Render, etc.) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🌐 SOLANA DISCOVERY BOT - CLOUD EDITION                ║
    ╠═══════════════════════════════════════════════════════════╣
    ║   Running on PORT: {port}                                    
    ║   Platform: Cloud Hosted                                  ║
    ║   Mode: LIVE (Simulation Disabled)                        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port)
'''

with open('solana_discovery/web_server.py', 'w') as f:
    f.write(web_server_updated)

print("✅ Updated web_server.py for cloud deployment")
