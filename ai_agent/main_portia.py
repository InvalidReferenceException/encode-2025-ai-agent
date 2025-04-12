from portia import Portia, Config, StorageClass, LLMModel, LLMProvider, InMemoryToolRegistry
from portia.plan import PlanBuilder, Variable
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

    prompt_var = Variable(name="prompt", description="The user prompt for the scene")
    tile_name_var = Variable(name="tile_name", description="The tile name used as filename")

    # Step 1: Scene validation
    builder.step("Validate the scene", "gemini_scene_validator_tool", "scene_validation", inputs=[prompt_var])

    # Step 2: Generate prompt if valid
    builder.step(
        "Generate image prompt",
        "gemini_image_prompt_tool",
        "image_prompt",
        inputs=[Variable(name="scene_validation", description="validation output")],
        condition="if $scene_validation is true"
    )

    # Step 3: Generate fallback if invalid
    builder.step(
        "Generate fallback prompt",
        "gemini_image_prompt_tool",
        "alternative_image_prompt",
        inputs=[Variable(name="scene_validation", description="validation output")],
        condition="if $scene_validation is false"
    )

    # Step 4: Generate image with valid prompt
    builder.step(
        "Generate image from prompt",
        "openai_image_gen_tool",
        "generated_image",
        inputs=[
            Variable(name="image_prompt", description="valid prompt"),
            tile_name_var
        ],
        condition="if $scene_validation is true"
    )

    # Step 5: Generate image with fallback
    builder.step(
        "Generate image from fallback prompt",
        "openai_image_gen_tool",
        "generated_image",
        inputs=[
            Variable(name="alternative_image_prompt", description="fallback prompt"),
            tile_name_var
        ],
        condition="if $scene_validation is false"
    )

    # Step 6: Upload to Supabase
    builder.step(
        "Upload to Supabase",
        "supabase_asset_uploader_tool",
        "supabase_url",
        inputs=[
            Variable(name="generated_image", description="image path"),
            tile_name_var
        ]
    )

    # Build plan and run
    plan = builder.build()
    print(plan.model_dump_json(indent=2))

    plan_run = _portia.run_plan(plan)
    print(plan_run.model_dump_json(indent=2))

    return plan_run.outputs.final_output or "Upload failed or no output"
