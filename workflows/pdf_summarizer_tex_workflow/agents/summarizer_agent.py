from swarmzero.agent import Agent, SDKContext
import os
from tools import summarize_bullets

CONFIG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 
        os.pardir,                   
        "swarmzero_config.toml"    
    )
)
sdk_context = SDKContext(CONFIG_PATH)
summarizer_agent = Agent(
    name="summarizer",
    functions=[summarize_bullets],
    instruction="Summarize text into bullet points.",
    description="Returns bullet-point summary for a given text chunk.",
    sdk_context=sdk_context,
    chat_only_mode=True,
)