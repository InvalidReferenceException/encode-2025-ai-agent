import os
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ImageGenSchema(BaseModel):
    """Inputs for creating a prompt to generate an image."""
    scene_description: str = Field(..., description="The scene the user wants to place.")
    tile_index: str = Field(..., description="The tile position number.")
    image_prompt: str = Field(..., description="The prompt to be used to generate the image - it is either from the 'final_image_prompt' or the 'fallback_image_prompt'.")


class OpenAIImageGenTool(Tool[dict]):
    """Generates a low-res image using DALL·E 2 and saves it locally."""

    id: str = "openai_image_gen_tool"
    name: str = "OpenAI Image Generator Tool"
    description: str = "Uses a prompt to generate an image with DALL·E 2 and saves it locally."
    args_schema: type[BaseModel] = ImageGenSchema
    output_schema: tuple[str, str] = (
        "json",
        "A dictionary with the 'scene_description', 'tile_index', and 'local_image_path'."
    )

    def run(self, _: ToolRunContext, scene_description: str, tile_index: str, image_prompt: str) -> dict:
        if not image_prompt:
            return {
                "scene_description": scene_description,
                "tile_index": tile_index,
                "local_image_path": ""
            }

        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)

        image_filename = f"{tile_index}.png"
        image_path = output_dir / image_filename

        try:
            response = client.images.generate(
                model="dall-e-2",
                prompt=image_prompt,
                n=1,
                size="256x256",
                response_format="url"
            )

            image_url = response.data[0].url
            print(f"Image URL: {image_url}")

            img_data = requests.get(image_url).content
            print(f"Downloaded image size: {len(img_data)} bytes")

            with open(image_path, "wb") as f:
                f.write(img_data)

            saved_path = str(image_path.resolve())
            print(f"Image successfully saved at: {saved_path}")

        except Exception as e:
            print(f"Image generation failed: {e}")
            saved_path = ""

        return {
            "scene_description": scene_description,
            "tile_index": tile_index,
            "local_image_path": saved_path
        }
