import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia
)

load_dotenv()
print(os.environ["google_api_key"], "test")

# Create a default Portia config with LLM provider set to Google GenAI and model set to Gemini 2.0 Flash
google_config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
    llm_model_name=LLMModel.GEMINI_2_0_FLASH
)

# Instantiate a Portia instance. Load it with the config and with the example tools.
portia = Portia(config=google_config)

# Write a query to ask
query = "When is the Hailey's Comet?"

# Generate the plan from the user query
plan = portia.plan(query)

# Serialise into JSON and print the output
print(plan.model_dump_json(indent=2))

# Run the test query and print the output!
plan_run = portia.run(plan)
print(plan_run.model_dump_json(indent=2))