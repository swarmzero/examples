from dotenv import load_dotenv
load_dotenv()

from swarmzero import Swarm
from app.tools import save_to_file,list_files, read_from_file
from app.tools import download_from_url

from swarmzero.sdk_context import SDKContext


config_path = "./app/swarmzero_config.toml"
sdk_context = SDKContext(config_path=config_path)

livepeer_swarm = Swarm(
    name="Livepeer Youtube Video Generator",
    description="A swarm of agents that collaborate as members of a Livepeer Youtube Video Generator team.",
    instruction="""You are the manager of a video production team for Livepeer Youtube Video Generator. Your goal is to guide the team in creating an engaging and informative video. Follow these steps:

    1. Coordinate with these agents in order:
       a. Script Writer Agent
       b. Scene Writer Agent
       c. Scene Prompt Generator Agent
       d. Scene Image Generator Agent (max 3 files at a time)
       e. Scene Image to Video Generator Agent (max 3 files at a time)
       f. Video Editor Agent
       g. Youtube Upload Agent

    2. After each interaction with agents, save the output as a separate file in:
       `./swarmzero-data/output/<video_topic>/<agent_type>/`
       Use the save_to_file tool for this purpose.

    3. Scene Image Generator Agent and Scene Image to Video Agent will return url or list of urls. You should use download_from_url tool to download images and videos.

    4. Use list_files and read_from_file tools to access and review previous outputs.

    5. Ensure each agent receives the relevant input from the previous step.

    6. Maintain consistency and coherence throughout the video creation process.

    7. Monitor the quality and relevance of each output, requesting revisions if necessary.

    8. Provide clear, concise instructions to each agent, specifying their task and any relevant constraints.

    9. After all steps are complete, review the entire project for cohesiveness and alignment with the original video concept.

    Remember to adapt your management style based on the specific video topic and requirements provided by the user.
    """,
    functions=[save_to_file, list_files, read_from_file, download_from_url],
    sdk_context=sdk_context,
    # max_iterations=30,
)
