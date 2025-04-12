from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Tuple
from ai_agent.main_portia import run_tile_generation_agent
from pyngrok import ngrok
import uvicorn

app = FastAPI()

class AssetRequest(BaseModel):
    prompt: str
    tile: int
    neighbours: Tuple[int, ...]
    asset_type: Optional[str] = "voxel"


@app.get("/")
def root():
    return {"message": "STEVE is online and ready to generate!"}


@app.post("/generate")
def generate_asset(data: AssetRequest):
    tile_name = f"tile_{data.tile}"
    supabase_url = run_tile_generation_agent(prompt=data.prompt, tile_name=tile_name)

    return {
        "status": "success" if "http" in supabase_url else "error",
        "tile": tile_name,
        "supabase_url": supabase_url,
        "prompt": data.prompt
    }


if __name__ == "__main__":
    # Start ngrok tunnel
    public_url = ngrok.connect(8080)
    print(f"STEVE is live at: {public_url}\n")

    # Start the FastAPI server
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
