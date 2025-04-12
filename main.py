from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class AssetRequest(BaseModel):
    prompt: str
    tile: int
    neighbours: tuple[int]
    asset_type: Optional[str] = "voxel"

@app.get("/")
def root():
    return {"message": "STEVE is online and ready to generate!"}

@app.post("/generate")
def generate_asset(data: AssetRequest):
    # Placeholder logic
    file_name = f"{data.asset_type}_asset_for_{data.prompt.replace(' ', '_')}.glb"
    return {
        "status": "success",
        "asset": file_name
    }

# blockchain sends request to craft tile x
# blockchain sends neighbouring tiles