def format_latex(bullet_text: str, **kwargs) -> str:
    items = [f"\\item {b[2:].strip()}" for b in bullet_text.splitlines() if b.startswith("- ")]
    return (
        "\\documentclass{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{enumitem}\n"
        "\\begin{document}\n"
        "\\section*{Summary Notes}\n"
        "\\begin{itemize}[leftmargin=*, label=--]\n"
        + "\n".join(items) +
        "\n\\end{itemize}\n"
        "\\end{document}"
    )