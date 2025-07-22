import asyncio
import os
import sys
from typing import List

from swarmzero.sdk_context import SDKContext
from swarmzero.workflow import Workflow, WorkflowStep, StepMode

from agents import formatter_agent, summarizer_agent
from util import extract_text_from_pdf, chunk_text

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "swarmzero_config.toml")
sdk_context = SDKContext(CONFIG_PATH)

async def run_summarizer(chunk: str, **kwargs) -> str:
    return await summarizer_agent.chat(chunk)

async def run_formatter(bullets: str, **kwargs) -> str:
    return await formatter_agent.chat(bullets)

workflow = Workflow(
    name="pdf_latex_summary",
    instruction="Summarize PDF and convert to LaTeX.",
    description="Runs summarizer then formatter agents sequentially.",
    steps=[
        WorkflowStep(name="SummarizeBullets",
                     runner=run_summarizer,
                     mode=StepMode.SEQUENTIAL),

        WorkflowStep(name="FormatLatex",
                     runner=run_formatter,  
                     mode=StepMode.SEQUENTIAL),
    ],
    sdk_context=sdk_context,
)

async def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample.pdf"
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)

    all_items: List[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        print(f"Chunk {idx}/{len(chunks)} → processing…")
        latex_doc = await workflow.run(chunk)
        all_items += [line.strip() for line in latex_doc.splitlines() if line.strip().startswith("\\item")]

    final = (
        "\\documentclass{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{enumitem}\n"
        "\\begin{document}\n"
        "\\section*{Summary Notes}\n"
        "\\begin{itemize}[leftmargin=*, label=--]\n"
        + "\n".join(all_items) +
        "\n\\end{itemize}\n"
        "\\end{document}"
    )

    out_file = os.path.splitext(os.path.basename(pdf_path))[0] + "_summary.tex"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(final)
    print(f"Written LaTeX summary to {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
