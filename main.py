import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    example_tool_registry,
)

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Create a default Portia config with LLM provider set to Google GenAI and model set to Gemini 2.0 Flash
google_config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
    llm_model_name=LLMModel.GEMINI_2_0_FLASH,
    google_api_key=GOOGLE_API_KEY
)

# Instantiate a Portia instance. Load it with the config and with the example tools.
portia = Portia(config=google_config, tools=example_tool_registry)

# Write a query to ask
query = "When is the Hailey's Comet?"

# Generate the plan from the user query
plan = portia.plan(query)

# Serialise into JSON and print the output
print(plan.model_dump_json(indent=2))

# Run the test query and print the output!
plan_run = portia.run(plan)
print(plan_run.model_dump_json(indent=2))