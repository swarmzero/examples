# Dune Agent
This Dune Agent enables you to search for indexes and crypto narratives using the DUNE API, providing updated market data. You can access detailed insights into the ALPHA, Beta, and Gamma Indexes, as well as Daily, Weekly, Monthly, and Quarterly Crypto Narratives. This offers comprehensive and timely information on the latest crypto trends.

Source: https://dune.com/dyorcrypto/relative-strength-crypto-narrative

Built with [SwarmZero SDK](https://github.com/swarmzero/swarmzero).


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
  - [All models supplied by Ollama](https://ollama.com/library)
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


## Testing
- Install the dev dependencies:
```
(venv) $ pip install -r requirements-dev.txt
```
- Run the test suite
```
$ pytest
```
- Run tests for a specific module
```
$ pytest tests/path/to/test_module.py
```
- Run with verbose output:
```
$ pytest -v
```
- Run with a detailed output of each test (including print statements):
```
$ pytest -s
```

## More
- Powered by [SwarmZero](https://swarmzero.ai).
