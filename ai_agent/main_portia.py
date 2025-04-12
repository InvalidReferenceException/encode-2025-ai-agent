from portia import Portia, Config, StorageClass, LLMModel, LLMProvider, InMemoryToolRegistry
from portia.plan import PlanBuilder
from .tools.image_prompt_generation_tool import GeminiImagePromptTool
from .tools.input_validation_tool import SceneValidatorTool
from .tools.supabase_asset_uploader import SupabaseAssetUploaderTool
from .tools.image_generation_tool import OpenAIImageGenTool

import os
from dotenv import load_dotenv

load_dotenv()

_tool_registry = InMemoryToolRegistry.from_local_tools([
    SceneValidatorTool(),
    GeminiImagePromptTool(),
    OpenAIImageGenTool(),
    SupabaseAssetUploaderTool()
])

_config = Config.from_default(
    storage_class=StorageClass.CLOUD,
    llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
    llm_model_name=LLMModel.GEMINI_2_0_FLASH
)

_portia = Portia(config=_config, tools=_tool_registry)


def run_tile_generation_agent(prompt: str, tile_name: str) -> str:
    agent_prompt = f"""
    You are creating a tile named '{tile_name}'.

    1. Validate the scene: '{prompt}' using the scene validator tool.
    2. If the validator returns 'true', generate an image prompt from it.
    3. If the validator returns 'false', generate a better fitting prompt.
    4. Use the prompt to generate an image and save it as '{tile_name}.png'.
    5. Upload that file to Supabase as '{tile_name}.png' and return the public URL.
    """

    builder = PlanBuilder(query=agent_prompt)

    builder.step("Validate the scene", "gemini_scene_validator_tool", "scene_validation") \
        .input("prompt", "The scene to validate")

    builder.step("Generate image prompt", "gemini_image_prompt_tool", "image_prompt") \
        .input("scene_validation", "Result of the scene validation") \
        .condition("if $scene_validation is true")

    builder.step("Generate fallback prompt", "gemini_image_prompt_tool", "alternative_image_prompt") \
        .input("scene_validation", "Result of the scene validation") \
        .condition("if $scene_validation is false")

    builder.step("Generate image from prompt", "openai_image_gen_tool", "generated_image") \
        .input("image_prompt", "The image prompt") \
        .input("tile_name", "Filename for saving") \
        .condition("if $scene_validation is true")

    builder.step("Generate image from fallback", "openai_image_gen_tool", "generated_image") \
        .input("alternative_image_prompt", "The fallback image prompt") \
        .input("tile_name", "Filename for saving") \
        .condition("if $scene_validation is false")

    builder.step("Upload to Supabase", "supabase_asset_uploader_tool", "supabase_url") \
        .input("generated_image", "The generated image") \
        .input("tile_name", "Name to save in Supabase")

    plan = builder.build()
    plan_run = _portia.run_plan(plan)

    return plan_run.outputs.get("supabase_url", "Upload failed or URL not returned.")
