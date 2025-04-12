from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import requests
import os


class SupabaseUploadSchema(BaseModel):
    """Inputs for uploading an image to Supabase storage."""
    file_path: str = Field(..., description="Local path to the image file to upload (e.g. .png)")
    tile_name: str = Field(..., description="Name to save the image as in Supabase")


class SupabaseAssetUploaderTool(Tool[str]):
    """Uploads an asset file to Supabase and returns a public URL."""

    id: str = "supabase_asset_uploader_tool"
    name: str = "Supabase Asset Uploader Tool"
    description: str = "Uploads an asset file to a Supabase bucket and returns a public URL."
    args_schema: type[BaseModel] = SupabaseUploadSchema
    output_schema: tuple[str, str] = ("str", "The public URL of the uploaded file.")

    def run(self, _: ToolRunContext, file_path: str, tile_name: str) -> str:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        BUCKET = "encode-assets"

        local_file = Path(file_path)
        if not local_file.exists():
            return f"File not found at: {file_path}"

        with open(local_file, "rb") as f:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/png"
            }

            upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{tile_name}"
            response = requests.put(upload_url, headers=headers, data=f)

        if response.ok:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{tile_name}"
            return public_url
        else:
            return f"Upload failed: {response.status_code} - {response.text}"
