from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from pathlib import Path
import requests
import uuid
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class OpenAIImageGenSchema(BaseModel):
    prompt: str = Field(..., description="The prompt describing the image to generate")


class OpenAIImageGenTool(Tool[str]):
    id: str = "openai_image_gen_tool"
    name: str = "OpenAI Image Generator Tool"
    description: str = "Generates a low-resolution PNG image using OpenAI DALL·E 3 and saves it locally."
    args_schema: type[BaseModel] = OpenAIImageGenSchema
    output_schema: tuple[str, str] = ("str", "The local file path to the generated image")

    def run(self, _: ToolRunContext, prompt: str) -> str:
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)

        image_filename = f"{uuid.uuid4().hex}.png"
        image_path = output_dir / image_filename

        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="256x256",
                response_format="url",
            )
            image_url = response["data"][0]["url"]

            img_data = requests.get(image_url).content
            with open(image_path, "wb") as f:
                f.write(img_data)

            return str(image_path.resolve())

        except Exception as e:
            return f"OpenAI image generation failed: {e}"
