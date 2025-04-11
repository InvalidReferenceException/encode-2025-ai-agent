from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import os
import uuid
import urllib.request


class GeminiImageGenSchema(BaseModel):
    """Input schema for generating an image from a prompt."""
    prompt: str = Field(..., description="The visual scene to generate (e.g. 'a castle in the forest')")


class GeminiImageGenTool(Tool[str]):
    """Generates an image from a prompt and saves it locally."""

    id: str = "gemini_image_gen_tool"
    name: str = "Gemini Image Generator Tool"
    description: str = (
        "Simulates generating an image from a prompt and saves it to the 'generated_images' folder."
    )
    args_schema: type[BaseModel] = GeminiImageGenSchema
    output_schema: tuple[str, str] = ("str", "The local path to the generated image")

    def run(self, _: ToolRunContext, prompt: str) -> str:
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)

        image_filename = f"{uuid.uuid4().hex}.png"
        image_path = output_dir / image_filename

        try:
            # Placeholder image simulating generated content
            placeholder = "https://via.placeholder.com/512.png?text=Gemini+Generated"
            urllib.request.urlretrieve(placeholder, image_path)
        except Exception as e:
            return f"Failed to generate/save image: {e}"

        return str(image_path.resolve())
