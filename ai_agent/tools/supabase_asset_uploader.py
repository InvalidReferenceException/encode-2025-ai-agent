from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import requests
import os


class SupabaseUploadSchema(BaseModel):
    """Inputs for uploading a 3D asset to Supabase storage."""
    file_path: str = Field(..., description="Local path to the 3D asset file to upload (e.g. .gltf)")
    destination_name: str = Field(..., description="The name the file should be saved as in Supabase storage")


class SupabaseAssetUploaderTool(Tool[str]):
    """Uploads a 3D asset file to Supabase and returns a public URL."""

    id: str = "supabase_asset_uploader_tool"
    name: str = "Supabase Asset Uploader Tool"
    description: str = (
        "Uploads a 3D asset file (ONLY model/gltf-binary MIME type is accepted) to a Supabase storage bucket and returns the public URL."
    )
    args_schema: type[BaseModel] = SupabaseUploadSchema
    output_schema: tuple[str, str] = ("str", "The public URL where the asset can be accessed.")

    def run(self, _: ToolRunContext, file_path: str, destination_name: str) -> str:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        local_file = Path(file_path)
        if not local_file.exists():
            return f"File not found at: {file_path}"

        with open(local_file, "rb") as f:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/octet-stream"
            }

            upload_url = f"{SUPABASE_URL}/storage/v1/object/encode-assets/{destination_name}"
            response = requests.post(upload_url, headers=headers, data=f)

        if response.ok:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/encode-assets/{destination_name}"
            return public_url
        else:
            return f"Upload failed: {response.status_code} - {response.text}"
