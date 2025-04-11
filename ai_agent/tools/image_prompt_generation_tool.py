from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
import google.generativeai as genai
import os

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiPromptToolSchema(BaseModel):
    """Inputs for the Gemini Flash image prompt enhancer."""
    prompt: str = Field(..., description="The simple user prompt to enhance into a rich visual description")


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
        model = genai.GenerativeModel("gemini-1.5-flash")

        system_instruction = (
            "You are a creative AI helping generate richly detailed prompts for image generation. "
            "Expand this prompt into a vivid, visual description:"
        )

        chat = model.start_chat(history=[])
        response = chat.send_message(f"{system_instruction}\n\n{prompt}")

        return response.text.strip()
