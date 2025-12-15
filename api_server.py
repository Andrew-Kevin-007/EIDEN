"""
FastAPI Backend for JARVIS Web GUI
Connects React frontend with Python voice assistant
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from assistant.core import Assistant
from utils.config_manager import get_config

app = FastAPI(title="JARVIS API")

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assistant
config = get_config()
assistant = None


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    response: str
    success: bool


@app.on_event("startup")
async def startup():
    """Initialize assistant on startup."""
    global assistant
    try:
        assistant = Assistant(config=config)
        assistant.initialize()
        print("✅ JARVIS assistant initialized")
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")


@app.post("/api/command", response_model=CommandResponse)
@app.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """Process voice command and return response."""
    if not assistant or not assistant.is_initialized:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        command = request.command
        print(f"\n🎤 Command received: {command}")
        
        # Get response using assistant's method
        response = assistant._get_response_for_command(command)
        print(f"💬 Response: {response}")
        
        # Also speak it
        try:
            assistant.speak(response)
        except Exception as e:
            print(f"⚠️  Speech error: {e}")
        
        return CommandResponse(
            response=response,
            success=True
        )
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        print(f"❌ Error: {e}")
        return CommandResponse(
            response=error_msg,
            success=False
        )


@app.get("/status")
async def get_status():
    """Get assistant status."""
    return {
        "initialized": assistant is not None and assistant.is_initialized,
        "running": assistant is not None and assistant.running
    }


@app.get("/")
async def root():
    """Health check."""
    return {"status": "online", "service": "JARVIS API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
