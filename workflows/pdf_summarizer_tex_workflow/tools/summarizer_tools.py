from openai import AsyncOpenAI
import os

ai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def summarize_bullets(prompt: str, **kwargs) -> str:
    resp = await ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize text into concise bullet points."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=800,
    )
    lines = [l.strip() for l in resp.choices[0].message.content.splitlines() if l.strip()]
    bullets = [l if l.startswith("- ") else f"- {l}" for l in lines]
    return "\n".join(bullets)
