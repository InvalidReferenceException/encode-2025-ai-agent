from pydantic import BaseModel
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class TileContext(BaseModel):
    tile_context: dict


class OpenAIImageGenTool(Tool[dict]):
    """Generates a low-res image using DALL·E 2 and saves it locally, updating tile_context."""

    id: str = "openai_image_gen_tool"
    name: str = "OpenAI Image Generator Tool"
    description: str = (
        "Uses a prompt in tile_context['final_image_prompt'] or tile_context['fallback_image_prompt'] "
        "to generate an image with DALL·E 2. Saves it locally and adds 'generated_image_path' to tile_context."
    )
    args_schema: type[BaseModel] = TileContext
    output_schema: tuple[str, str] = ("json", "Updated tile_context with 'generated_image_path'")

    def run(self, _: ToolRunContext, tile_context: dict) -> dict:
        prompt = tile_context.get("final_image_prompt") or tile_context.get("fallback_image_prompt")
        if not prompt:
            tile_context["generated_image_path"] = "Error: No image prompt found in context."
            return tile_context

        output_filename_base = tile_context.get("tile_index", f"tile_{os.urandom(4).hex()}")
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)

        image_filename = f"{output_filename_base}.png"
        image_path = output_dir / image_filename

        try:
            response = client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                n=1,
                size="256x256",
                response_format="url"
            )

            image_url = response.data[0].url
            img_data = requests.get(image_url).content

            with open(image_path, "wb") as f:
                f.write(img_data)

            tile_context["generated_image_path"] = str(image_path.resolve())

        except Exception as e:
            tile_context["generated_image_path"] = f"Image generation failed: {e}"

        return tile_context
