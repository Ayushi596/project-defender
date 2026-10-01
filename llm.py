import os
from openai import OpenAI

DEFAULT_BASE_URL = "https://inference.do-ai.run/v1/"
DEFAULT_MODEL = "openai-gpt-oss-20b"


def ask(system: str, user: str) -> str:
    base_url = os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL)
    model = os.getenv("LLM_MODEL", DEFAULT_MODEL)
    api_key = os.getenv("LLM_API_KEY", "")

    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"LLM call failed: {exc}"