from pydantic import BaseModel,Field
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import requests
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET = "encode-assets"


class SupabaseUploadSchema(BaseModel):
    """Inputs for creating a prompt to generate an image."""
    scene_description: str = Field(..., description="The scene the user wants to place.")
    tile_index: str = Field(..., description="The tile position number.")
    image_path: str = Field(..., description="The local path of the image to be stored.")


class SupabaseAssetUploaderTool(Tool[dict]):
    """Uploads an asset file to Supabase and adds the public URL to tile_context."""

    id: str = "supabase_asset_uploader_tool"
    name: str = "Supabase Asset Uploader Tool"
    description: str = (
        "Uploads an image file to a Supabase bucket using the provided path and returns a dict with the updated url from Supabase"
    )
    args_schema: type[BaseModel] = SupabaseUploadSchema
    output_schema: tuple[str, str] = ("json", "Dict with 'uploaded_url' that has the Supabase url.")

    def run(self, _: ToolRunContext, scene_description: str, tile_index: str, image_path: str) -> dict:
        if not image_path:
            return {
                "uploaded_url": "Error: 'generated_image_path' is missing from tile_context"
            }

        local_file = Path(image_path)
        if not local_file.exists():
            return {
                "uploaded_url": f"File not found at: {image_path}"
            }
        
        try:
            with open(local_file, "rb") as f:
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "image/png"
                }

                upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{tile_index}"
                response = requests.put(upload_url, headers=headers, data=f)

            if response.ok:
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{tile_index}"
            else:
                public_url = f"Upload failed: {response.status_code} - {response.text}"

        except Exception as e:
            public_url = f"Exception during upload: {e}"

        return {
            "uploaded_url": public_url
        }
