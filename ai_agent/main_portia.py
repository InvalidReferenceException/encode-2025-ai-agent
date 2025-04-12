from portia import Portia, Config, LLMModel, LLMProvider, InMemoryToolRegistry
from portia.plan import PlanBuilder, Variable
from .tools.image_prompt_generation_tool import GeminiImagePromptTool
from .tools.input_validation_tool import SceneValidatorTool
from .tools.supabase_asset_uploader import SupabaseAssetUploaderTool
from .tools.image_generation_tool import OpenAIImageGenTool
from portia.templates.example_plans import DEFAULT_EXAMPLE_PLANS
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
    llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
    llm_model_name=LLMModel.GEMINI_2_0_FLASH
)

_portia = Portia(config=_config, tools=_tool_registry)


from portia.plan import PlanBuilder, Variable

def run_tile_generation_agent(scene_description: str, output_tile_name: str) -> str:
    agent_instruction = f"""
    You are generating a tile named '{output_tile_name}'.
    This is the scene description: '{scene_description}'.
    Use the shared dictionary `tile_context` to pass all inputs and outputs across tool steps.
    Always read from and return the entire `tile_context` object to maintain continuity between tools.
    """

    builder = PlanBuilder(query=agent_instruction)

    initial_tile_context = {
        "scene_description": scene_description,
        "tile_index": output_tile_name
    }

    # STEP 1: Scene validation
    builder.step(
        task="Validate scene from tile_context['scene_description']",
        tool_id="gemini_scene_validator_tool",
        output="validated_context",
        inputs=[Variable(name="tile_context", description="Initial tile context")]
    )

    # STEP 2: Generate image prompt if valid
    builder.step(
        task="Generate image prompt from scene description",
        tool_id="gemini_image_prompt_tool",
        output="prompt_context_valid",
        inputs=[Variable(name="validated_context", description="tile_context with validation result")],
        condition="if $validated_context.scene_validation_result is true"
    )

    # STEP 3: Generate fallback image prompt if invalid
    builder.step(
        task="Generate fallback image prompt",
        tool_id="gemini_image_prompt_tool",
        output="prompt_context_fallback",
        inputs=[Variable(name="validated_context", description="tile_context with validation result")],
        condition="if $validated_context.scene_validation_result is false"
    )

    # STEP 4: Generate image from final_image_prompt
    builder.step(
        task="Generate image from final_image_prompt",
        tool_id="openai_image_gen_tool",
        output="image_context_valid",
        inputs=[Variable(name="prompt_context_valid", description="tile_context with final prompt")],
        condition="if $validated_context.scene_validation_result is true"
    )

    # STEP 5: Generate image from fallback_image_prompt
    builder.step(
        task="Generate image from fallback_image_prompt",
        tool_id="openai_image_gen_tool",
        output="image_context_fallback",
        inputs=[Variable(name="prompt_context_fallback", description="tile_context with fallback prompt")],
        condition="if $validated_context.scene_validation_result is false"
    )

    # STEP 6: Upload image to Supabase (from whichever branch generated the image)
    builder.step(
        task="Upload image to Supabase",
        tool_id="supabase_asset_uploader_tool",
        output="final_context",
        inputs=[
            Variable(name="image_context_valid", description="tile_context from valid prompt image"),
            Variable(name="image_context_fallback", description="tile_context from fallback prompt image")
        ]
    )

    plan = builder.build()

    new_plan = _portia.plan(
        query=agent_instruction,
        inputs={"tile_context": initial_tile_context},
        example_plans=[*DEFAULT_EXAMPLE_PLANS, plan]
    )

    print(new_plan.pretty_print())

    plan_run = _portia.run_plan(new_plan)
    print(plan_run.model_dump_json(indent=2))

    final_context = plan_run.outputs.final_context or {}
    return final_context.get("uploaded_url", "Upload failed or no output")
