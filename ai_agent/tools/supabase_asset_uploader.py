from pydantic import BaseModel
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import requests
import os

class TileContext(BaseModel):
    tile_context: dict


class SupabaseAssetUploaderTool(Tool[dict]):
    """Uploads an asset file to Supabase and adds the public URL to tile_context."""

    id: str = "supabase_asset_uploader_tool"
    name: str = "Supabase Asset Uploader Tool"
    description: str = (
        "Uploads an image file to a Supabase bucket using the provided path in tile_context['generated_image_path'] "
        "and returns the updated tile_context with 'uploaded_url'."
    )
    args_schema: type[BaseModel] = TileContext
    output_schema: tuple[str, str] = ("json", "Updated tile_context with 'uploaded_url'")

    def run(self, _: ToolRunContext, tile_context: dict) -> dict:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        BUCKET = "encode-assets"

        image_path = tile_context.get("generated_image_path")
        output_filename = f"{tile_context.get('tile_index', 'tile')}.png"

        if not image_path:
            tile_context["uploaded_url"] = "Error: 'generated_image_path' is missing from tile_context"
            return tile_context

        local_file = Path(image_path)
        if not local_file.exists():
            tile_context["uploaded_url"] = f"File not found at: {image_path}"
            return tile_context

        try:
            with open(local_file, "rb") as f:
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "image/png"
                }

                upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{output_filename}"
                response = requests.put(upload_url, headers=headers, data=f)

            if response.ok:
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{output_filename}"
                tile_context["uploaded_url"] = public_url
            else:
                tile_context["uploaded_url"] = f"Upload failed: {response.status_code} - {response.text}"

        except Exception as e:
            tile_context["uploaded_url"] = f"Exception during upload: {e}"

        return tile_context
