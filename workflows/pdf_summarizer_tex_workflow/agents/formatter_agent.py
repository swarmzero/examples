from swarmzero.agent import Agent, SDKContext
import os
from tools import format_latex

CONFIG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 
        os.pardir,                   
        "swarmzero_config.toml"    
    )
)
sdk_context = SDKContext(CONFIG_PATH)
formatter_agent = Agent(
    name="formatter",
    functions=[format_latex],
    instruction="Format bullet points into LaTeX.",
    description="Wraps bullets into a LaTeX itemize document.",
    sdk_context=sdk_context,
    chat_only_mode=True,
)