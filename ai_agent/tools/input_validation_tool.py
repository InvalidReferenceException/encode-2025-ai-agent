import os
import json
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from PIL import Image
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class SceneValidationSchema(BaseModel):
    """Inputs for checking whether a described scene fits the given images."""
    prompt: str = Field(..., description="The scene the user wants to place (e.g., 'a castle on a hill')")


class SceneValidatorTool(Tool[dict]):
    """Validates whether a described scene fits the given image environment."""

    id: str = "gemini_scene_validator_tool"
    name: str = "Scene Validator Tool"
    description: str = (
        "Uses Gemini 1.5 Pro to determine if a described scene fits contextually within the provided image(s). "
        "Returns a JSON object with 'is_valid': true or false."
    )
    args_schema: type[BaseModel] = SceneValidationSchema
    output_schema: tuple[str, str] = (
        "json",
        "A JSON object like { 'is_valid': true/false } indicating if the scene fits the context."
    )

    def run(self, _: ToolRunContext, prompt: str) -> dict:
        model = genai.GenerativeModel("gemini-1.5-pro")

        images = []
        image_paths = ["ai_agent/test_images/arctic_image.jpg", "ai_agent/test_images/desert_image.jpg"]
        for path in image_paths:
            try:
                img = Image.open(path)
                images.append(img)
            except Exception as e:
                return {"is_valid": False}

        query = (
            "You are an AI scene validator. Given the following images of a game environment and a described scene, "
            "answer only with 'true' or 'false'. Do not include explanations. "
            f"Scene: '{prompt}'. Does this scene contextually fit with the images?"
        )

        try:
            response = model.generate_content([query] + images, generation_config={"temperature": 0})
            answer = response.text.strip().lower()

            if "true" in answer:
                return {"is_valid": True}
            elif "false" in answer:
                return {"is_valid": False}
            else:
                return {"is_valid": False}
        except Exception as e:
            return {"is_valid": False}
