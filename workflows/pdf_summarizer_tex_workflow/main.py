import asyncio
import os
import sys
import uuid
from typing import List

import fitz  # PyMuPDF

from swarmzero.agent import Agent
from swarmzero.sdk_context import SDKContext
from swarmzero.workflow import Workflow, WorkflowStep, StepMode


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def chunk_text(text: str, max_chars: int = 2000) -> List[str]:
    paragraphs = text.split("\n")
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) < max_chars:
            current += para + "\n"
        else:
            chunks.append(current.strip())
            current = para + "\n"
    if current:
        chunks.append(current.strip())
    return chunks


def summarize_bullets(prompt: str, **kwargs):
    lines = [line.strip() for line in prompt.split(".") if line.strip()]
    bullets = "\n".join(f"- {line}" for line in lines)
    return f"[Bullet Point Summary]:\n{bullets}"

def format_latex(prompt: str, **kwargs) -> str:
    bullet_lines = prompt.strip().split("\n")
    latex_items = "\n".join(f"\\item {line.lstrip('- ').strip()}" for line in bullet_lines if line.startswith("-"))

    latex_doc = (
        "\\documentclass{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{enumitem}\n"
        "\\begin{document}\n"
        "\\section*{Summary Notes}\n"
        "\\begin{itemize}[leftmargin=*, label=--]\n"
        f"{latex_items}\n"
        "\\end{itemize}\n"
        "\\end{document}"
    )
    return latex_doc



CONFIG_PATH = os.path.join(os.path.dirname(__file__), "swarmzero_config.toml")

sdk_context = SDKContext(CONFIG_PATH)

summarizer_agent = Agent(
    name="BulletSummarizerAgent",
    functions=[summarize_bullets],
    instruction="Summarize input in bullet points.",
    agent_id=str(uuid.uuid4()),
    config_path=CONFIG_PATH,
    sdk_context=sdk_context,
    chat_only_mode=True
)


async def run_agent(prompt, **kwargs):
    return await summarizer_agent.chat(prompt)

latex_agent = Agent(
    name="LatexFormatterAgent",
    functions=[format_latex],
    instruction="Format input bullet points into a LaTeX document.",
    agent_id=str(uuid.uuid4()),
    config_path=CONFIG_PATH,
    sdk_context=sdk_context,
    chat_only_mode=True
)

async def run_latex_agent(prompt, **kwargs):
    return await latex_agent.chat(prompt)

workflow = Workflow(
    name="pdf_latex_summary",
    instruction="Summarize PDF and convert to LaTeX notes.",
    description="A workflow that summarizes and formats PDF text as LaTeX.",
    steps=[
        WorkflowStep(name="SummarizeBullets", runner=run_agent, mode=StepMode.SEQUENTIAL),
        WorkflowStep(name="FormatLatex", runner=run_latex_agent, mode=StepMode.SEQUENTIAL),
    ],
    sdk_context=sdk_context,
)

async def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample.pdf"
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)

    # Step 1: Summarize each chunk into bullets
    bullet_summaries = []
    for chunk in chunks:
        summary = await run_agent(chunk)
        bullet_summaries.append(summary)

    # Step 2: Merge all bullet summaries into one bullet string
    merged_bullets = "\n".join(bullet_summaries)

    # Step 3: Extract just the bullet lines
    bullet_lines = [line.strip() for line in merged_bullets.split("\n") if line.strip().startswith("-")]
    latex_items = "\n".join(f"\\item {line.lstrip('- ').strip()}" for line in bullet_lines)

    # Step 4: Hardcoded LaTeX wrapping
    final_latex = (
        "\\documentclass{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{enumitem}\n"
        "\\begin{document}\n"
        "\\section*{Summary Notes}\n"
        "\\begin{itemize}[leftmargin=*, label=--]\n"
        f"{latex_items}\n"
        "\\end{itemize}\n"
        "\\end{document}"
    )

    # Step 5: Write the final LaTeX doc to file
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = f"{base_name}_summary.tex"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_latex)

    print(f"Summary written to: {output_path}")




if __name__ == "__main__":
    asyncio.run(main())
