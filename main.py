from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Tuple
from ai_agent.main_portia import run_tile_generation_agent

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
