from dotenv import load_dotenv
load_dotenv()

from swarmzero import Swarm
from app.tools import save_to_file

from swarmzero.sdk_context import SDKContext
from app.agents.qa_engineer.agent import get_qa_agent


config_path = "./app/swarmzero_config.toml"
sdk_context = SDKContext(config_path=config_path)

dapp_swarm = Swarm(
    name="DeFi Startup",
    description="A swarm of agents that collaborate as members of a DeFi (Decentralized Finance) startup.",
    instruction="You are a DeFi Startup whose goal is to create new DeFi products for your customers. You are to "
    "output working code that satisfies the user's needs. You must output all the code to the "
    "`./swarmzero-data/output/<users_task_name_goes_here>/<code_type_name_goes_here>` folder using the provided tools.",
    functions=[save_to_file],
    sdk_context=sdk_context, #We created sdkcontext to pass context to another agent.
    #config_path=config_path, # If you dont want to add agent you can pass config_path and remove sdkcontext to swarm it will create sdkcontext for you.
)

#add QA agent
qa_agent = get_qa_agent(sdk_context)

dapp_swarm.add_agent(qa_agent)

# remove QA agent
# dapp_swarm.remove_agent(qa_agent)

