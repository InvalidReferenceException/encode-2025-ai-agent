from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
import google.generativeai as genai
import os

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class GeminiPromptToolSchema(BaseModel):
    """Inputs for the Gemini Flash image prompt enhancer."""
    prompt: str = Field(..., min_length=5, max_length=200, description="A short prompt to expand into a vivid image scene.")


class GeminiImagePromptTool(Tool[str]):
    """Uses Gemini 2.0 Flash to generate a rich prompt for image generation."""

    id: str = "gemini_image_prompt_tool"
    name: str = "Gemini Image Prompt Tool"
    description: str = (
        "Enhances a basic text prompt into a detailed image prompt using Gemini 2.0 Flash. "
        "Useful for text-to-image pipelines."
    )
    args_schema: type[BaseModel] = GeminiPromptToolSchema
    output_schema: tuple[str, str] = ("str", "A vivid image generation prompt")

    def run(self, _: ToolRunContext, prompt: str) -> str:
        """Enhance a simple prompt using Gemini Flash."""
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")

            system_instruction = (
                "You are a visual prompt engineer for AI-generated art. "
                "Given a vague user prompt, rewrite it as a vivid, richly detailed description for image generation. "
                "Include elements such as colors, lighting, atmosphere, setting, and artistic style. "
                "Respond with only the final prompt, no explanation or commentary."
            )

            chat = model.start_chat(history=[])
            response = chat.send_message(f"{system_instruction}\n\n{prompt}")

            return response.text.strip()

        except Exception as e:
            return f"Image prompt generation failed: {str(e)}"
