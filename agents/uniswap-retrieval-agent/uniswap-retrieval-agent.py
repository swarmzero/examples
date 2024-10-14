import os
import logging
import subprocess
import shutil


from dotenv import load_dotenv
load_dotenv()

langtrace_api_key = os.getenv("LANGTRACE_API_KEY", "")
if langtrace_api_key:
    from langtrace_python_sdk import langtrace
    langtrace.init(
        api_key=langtrace_api_key,
        disable_instrumentations={ "only": ["sqlalchemy"] }
    )


from swarmzero import Agent

logging.basicConfig(level=logging.INFO)

def get_config_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), filename))

document_path = 'swarmzero-data/files/user'
project = 'uniswap-docs'
repo_url = 'https://github.com/Uniswap/docs.git'

print(f"Cloning docs for {project}: {repo_url}")

project_repo_dir = os.path.join(document_path, project)
if not os.path.exists(project_repo_dir):
    subprocess.run(f"mkdir {project_repo_dir}", shell=True)
    subprocess.run(
        f'git clone {repo_url} {project_repo_dir}',
        shell=True
    )

print(f"Cloned {project}({repo_url}) to {project_repo_dir}")

documentation_files = ['docs']

remove_list = [item for item in os.listdir(project_repo_dir) if item not in documentation_files]

for item in remove_list:
    item_path = os.path.join(project_repo_dir, item)
    
    if os.path.isfile(item_path):
        os.remove(item_path)
        print(f'Removed file: {item_path}')
    elif os.path.isdir(item_path):
        shutil.rmtree(item_path)
        print(f'Removed directory: {item_path}')
    else:
        print(f'Item not found: {item_path}')


instruction = """ Welcome to the Uniswap Documentation Q&A Assistant! Your role is to provide accurate and concise answers to user queries based on the official Uniswap documentation. When responding, keep the following guidelines in mind:

	1.	Accuracy: Ensure your answers are directly based on the most current Uniswap documentation. Reference specific sections or pages when necessary.
	2.	Clarity: Communicate in simple, straightforward language. Avoid technical jargon unless it is necessary, and explain any complex concepts clearly.
	3.	Promptness: Aim to provide answers quickly, keeping your responses to the point to respect the user’s time.
	4.	User Engagement: Encourage users to ask follow-up questions if they need further clarification on a topic. Provide links to relevant sections of the documentation where they can read more in-depth information.
	5.	Updates and Feedback: Stay updated with the latest changes in the Uniswap platform and documentation. Promptly incorporate these updates into your responses. Encourage users to provide feedback on the accuracy and helpfulness of the information provided."""

my_agent = Agent(
    name="uniswap-retrieval-agent",
    functions=[],
    instruction=instruction,
    config_path=get_config_path("swarmzero_config.toml"),
    retrieve=True,
    required_exts=[".md"],
    retrieval_tool = 'pinecone-serverless',
    index_name="uniswap-protocol",
)
my_agent.run()
