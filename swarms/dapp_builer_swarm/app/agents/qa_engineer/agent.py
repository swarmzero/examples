from swarmzero import Agent
from app.agents.instructions import QA_ENGINEER_INSTRUCTION

def get_qa_agent(sdk_context):

    sdk_context.add_agent_config("./app/agents/qa_engineer/swarmzero_config.toml")

    qa_agent = Agent(
        name="Quality Assurance Engineer Agent",
        description="This agent acts like a QA Engineer on a team and can review code.",
        instruction=QA_ENGINEER_INSTRUCTION,
        role="QA engineer",
        functions=[],
        swarm_mode=True,
        sdk_context=sdk_context,
    )

    return qa_agent
