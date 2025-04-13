import json
import subprocess
import asyncio
from main import process_tile_request
from pydantic import BaseModel


class TileEvent(BaseModel):
    scene: str
    tile_index: int


def felt_to_str(felt):
    if isinstance(felt, str) and felt.startswith("0x"):
        try:
            return bytes.fromhex(felt[2:]).decode("utf-8").strip('\x00')
        except:
            return str(felt)
    return str(felt)


async def run_event_listener():
    print("Background listener started for Dojo events...")

    process = await asyncio.create_subprocess_exec(
        "sozo", "events", "--follow",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    while True:
        line = await process.stdout.readline()
        if not line:
            break

        try:
            event_data = json.loads(line.decode())

            if event_data.get("name") == "TileRequested":
                scene = felt_to_str(event_data["data"]["scene"])
                tile_index = int(event_data["data"]["tile_index"])

                tile_event = TileEvent(scene=scene, tile_index=tile_index)
                print(f"[EVENT] Triggering generation for tile {tile_event.tile_index}")

                result = process_tile_request(
                    scene_description=tile_event.scene,
                    tile_index=tile_event.tile_index
                )

                print("Generation Result:", result)

        except Exception as e:
            print("[EVENT ERROR]", e)
