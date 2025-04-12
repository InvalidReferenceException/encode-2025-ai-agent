import os
from dotenv import load_dotenv
from portia import (
    Config,
    StorageClass,
    LLMModel,
    LLMProvider,
    Portia
)

from portia import InMemoryToolRegistry
from tools.image_prompt_generation_tool import GeminiImagePromptTool
from tools.input_validation_tool import SceneValidatorTool
from tools.supabase_asset_uploader import SupabaseAssetUploaderTool
from tools.image_generation_tool import OpenAIImageGenTool

load_dotenv()

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        SceneValidatorTool(),
        GeminiImagePromptTool(),
        OpenAIImageGenTool(),
        SupabaseAssetUploaderTool()
    ]
)


# Create a default Portia config with LLM provider set to Google GenAI and model set to Gemini 2.0 Flash
google_config = Config.from_default(
    storage_class=StorageClass.CLOUD,
    llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
    llm_model_name=LLMModel.GEMINI_2_0_FLASH
)

# Instantiate a Portia instance. Load it with the config and with the example tools.
portia = Portia(config=google_config, tools=custom_tool_registry)

# User input
user_input = "A desert outpost."

agent_prompt = f"""
1. Validate the scene: '{user_input}' using the scene validator tool.
2. If the validator returns 'true', use it directly to generate an image prompt.
3. If the validator returns 'false', generate an alternative image prompt that fits better with the existing images.
4. Use the image prompt to generate an image.
5. Upload the image to Supabase and return the URL.
"""

# Generate the plan from the user query
plan = portia.plan(agent_prompt)

# Serialise into JSON and print the output
print(plan.model_dump_json(indent=2))

# Run the test query and print the output!
plan_run = portia.run(agent_prompt)
print(plan_run.model_dump_json(indent=2))
