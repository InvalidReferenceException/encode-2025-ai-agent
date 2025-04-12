from pydantic import BaseModel
from portia.tool import Tool, ToolRunContext
import google.generativeai as genai
import os

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class TileContext(BaseModel):
    tile_context: dict


class GeminiImagePromptTool(Tool[dict]):
    """Uses Gemini 2.0 Flash to generate a rich prompt for image generation."""

    id: str = "gemini_image_prompt_tool"
    name: str = "Gemini Image Prompt Tool"
    description: str = (
        "Enhances a basic scene description into a vivid image prompt using Gemini 2.0 Flash. "
        "Stores result as 'final_image_prompt' or 'fallback_image_prompt' depending on usage context."
    )
    args_schema: type[BaseModel] = TileContext
    output_schema: tuple[str, str] = ("json", "Updated tile_context with generated image prompt")

    def run(self, _: ToolRunContext, tile_context: dict) -> dict:
        scene = tile_context.get("scene_description", "")

        try:
            model = genai.GenerativeModel("gemini-2.0-flash")

            system_instruction = (
                "You are a visual prompt engineer for AI-generated art. "
                "Given a vague user prompt, rewrite it as a vivid, richly detailed description for image generation. "
                "Include elements such as colors, lighting, atmosphere, setting, and artistic style. "
                "Respond with only the final prompt, no explanation or commentary."
            )

            chat = model.start_chat(history=[])
            response = chat.send_message(f"{system_instruction}\n\n{scene}")
            prompt = response.text.strip()

            # Caller (the plan) determines the step: valid or fallback
            if "scene_validation_result" in tile_context and tile_context["scene_validation_result"] is False:
                tile_context["fallback_image_prompt"] = prompt
            else:
                tile_context["final_image_prompt"] = prompt

            return tile_context

        except Exception as e:
            tile_context["image_prompt_error"] = f"Image prompt generation failed: {str(e)}"
            return tile_context
