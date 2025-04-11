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
from tools.image_generation_tool import GeminiImageGenTool

load_dotenv()

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        SceneValidatorTool(),
        GeminiImagePromptTool(),
        GeminiImageGenTool(),
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
Create an image prompt of {user_input}.
Only do this if you think that this will fit contextually within the current images.
If the request doesn't fit into contextually give an image prompt of something that you think should fit.
Use the prompt to generate an image and save it locally.
Upload the locally saved image to supabase and give the supabase url.
"""

# Generate the plan from the user query
plan = portia.plan(agent_prompt)

# Serialise into JSON and print the output
print(plan.model_dump_json(indent=2))

# Run the test query and print the output!
plan_run = portia.run(agent_prompt)
print(plan_run.model_dump_json(indent=2))
