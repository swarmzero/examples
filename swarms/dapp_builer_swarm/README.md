# dApp Builder Swarm

This is an example of a Swarm of AI Agents that are able to coordinate and build a web3 dApp (decentralized application) based on a users' prompt.

> NOTE: this is only a demonstration and is not intended for production use. The simpler the dApp you ask the swarm to build, the more likely it is to be completed.


## Project Requirements
- Python >= 3.11

## Setup
- Create a new file called .env
- Copy the contents of [.env.example](.env.example) into your new .env file
- API keys for third party tools are not provided.
  - `OPENAI_API_KEY` from OpenAI
  
  You can use other LLMs, in which case you can add a corresponding API key
  - `ANTHROPIC_API_KEY` from Anthropic
  - `MISTRAL_API_KEY` from Mistral 
- Create a virtual Python environment
```
$ python -m venv ./venv
```
- Activate the Python virtual env.
  - Windows:
    - In cmd.exe: `venv\Scripts\activate.bat`
    - In PowerShell: `venv\Scripts\Activate.ps1`
  - Unix: `source venv/bin/activate`
- Install dependencies.
```
$ pip install -r requirements.txt
```


## Usage
- Run it
```
(venv) $ python main.py
```
- You can now describe the dApp you want to build e.g. *"build a dApp to mint new NFTs of AI models"*.
- The code will be stored in [swarmzero-data/output](./swarmzero-data/output).


## More
- Powered by [SwarmZero](https://swarmzero.ai).
