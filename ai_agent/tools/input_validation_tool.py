from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from typing import List
from PIL import Image
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class SceneValidationSchema(BaseModel):
    """Inputs for checking whether a described scene fits the given images."""
    prompt: str = Field(..., description="The scene the user wants to place (e.g., 'a castle on a hill')")
    # image_paths: List[str] = Field(..., description="A list of image file paths representing the scene environment")


class SceneValidatorTool(Tool[str]):
    """Validates whether a described scene fits the given image environment."""

    id: str = "gemini_scene_validator_tool"
    name: str = "Scene Validator Tool"
    description: str = (
        "Uses Gemini 1.5 Pro to determine if a described scene fits contextually within the provided image(s)."
    )
    args_schema: type[BaseModel] = SceneValidationSchema
    output_schema: tuple[str, str] = ("str", "A reasoned response indicating whether the described scene fits.")

    def run(self, _: ToolRunContext, prompt: str) -> str:
        model = genai.GenerativeModel("gemini-1.5-pro")

        images = []
        image_paths = ["ai_agent/test_images/arctic_image.jpg", "ai_agent/test_images/desert_image.jpg"]
        for path in image_paths:
            try:
                img = Image.open(path)
                images.append(img)
            except Exception as e:
                return f"Failed to load image {path}: {e}"
            
        # Construct instruction + call Gemini
        query = (
            "Given the following images of a game environment, determine whether the user's described scene "
            f"('{prompt}') would be a natural fit or contextually appropriate. Be honest, and give reasoning."
        )

        response = model.generate_content([query] + images, generation_config={"temperature": 0})
        return response.text.strip()
