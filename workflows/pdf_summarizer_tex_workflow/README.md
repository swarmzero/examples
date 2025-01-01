# PDF Summarizer to Tex Workflow

A sequential workflow built using SwarmZero framework that enables concise summarization of large pdf's to be outputted in a tex file 

## Description

This workflow utilizes PyMuPDF for extracting text out of a pdf and is built on top fo the SwarmZero framework, providing enhanced summarization cpabilities wiht AI-powered processing. 

## Prerequisites

- Python 3.11 or higher
- Poetry package manager
- OpenAI API Key
- Langtrace API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/swarmzero/examples.git
cd examples/workflows/pdf_summarizer_tex_workflow
```

2. Install dependencies using Poetry:
```bash
poetry install --no-root
```

3. Set up environment variables:
Create a `.env` file in the root directory and add your API keys based on the .env.example file
## Usage

Run the workflow on a pdf like so:
``` bash
python main.py path/to/pdf/text.pdf
```

## Learn more
Visit [SwarmZero](https://swarmzero.ai) to learn more about the SwarmZero framework.
