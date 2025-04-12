import os
from pydantic import BaseModel
from portia.tool import Tool, ToolRunContext
from PIL import Image
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class TileContext(BaseModel):
    tile_context: dict


class SceneValidatorTool(Tool[dict]):
    """Validates whether a described scene fits the given image environment."""

    id: str = "gemini_scene_validator_tool"
    name: str = "Scene Validator Tool"
    description: str = (
        "Uses Gemini 1.5 Pro to determine if a described scene fits contextually within provided game environment images. "
        "Reads 'scene_description' from tile_context and writes 'scene_validation_result': true/false."
    )
    args_schema: type[BaseModel] = TileContext
    output_schema: tuple[str, str] = (
        "json",
        "Updated tile_context with 'scene_validation_result': true or false"
    )

    def run(self, _: ToolRunContext, tile_context: dict) -> dict:
        scene_description = tile_context.get("scene_description", "")

        if not scene_description:
            tile_context["scene_validation_result"] = False
            tile_context["validation_error"] = "Missing 'scene_description'"
            return tile_context

        model = genai.GenerativeModel("gemini-1.5-pro")

        image_paths = [
            "ai_agent/test_images/arctic_image.jpg",
            "ai_agent/test_images/desert_image.jpg"
        ]

        image_list = []
        for path in image_paths:
            try:
                img = Image.open(path)
                image_list.append(img)
            except Exception:
                tile_context["scene_validation_result"] = False
                tile_context["validation_error"] = f"Failed to load image: {path}"
                return tile_context

        query = (
            "You are an AI scene validator. Given the following images of a game environment and a described scene, "
            "answer only with 'true' or 'false'. No explanation. "
            f"Scene: '{scene_description}'. Does this scene contextually fit with the environment shown in the images?"
        )

        try:
            response = model.generate_content([query] + image_list, generation_config={"temperature": 0})
            answer = response.text.strip().lower()

            tile_context["scene_validation_result"] = "true" in answer

        except Exception as e:
            tile_context["scene_validation_result"] = False
            tile_context["validation_error"] = f"Validation failed: {e}"

        return tile_context
