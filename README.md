\# ProjectDefender



ProjectDefender is an AI interview simulator for placement students. Paste a GitHub repo URL and an open-weight LLM reads your README and code, then grills you with hard questions tied to specific files, the way a real interviewer would.



\## The problem

In placement interviews, "tell me about your project" is where many students get exposed: why this database, what breaks at scale, what if this call fails. ProjectDefender makes you practice that before the real interview.



\## How it works

1\. `reader.py` clones the repo and picks the README plus key source files.

2\. The model writes 5 questions, each tied to a real file. Questions citing unknown files are discarded.

3\. You answer, and the model gives: what you got right, what you missed, and one follow-up. No numeric score.



\## Run it

&#x20;   pip install -r requirements.txt



Set environment variables (PowerShell):



&#x20;   $env:LLM\_BASE\_URL="https://api.groq.com/openai/v1"

&#x20;   $env:LLM\_API\_KEY="your-key"

&#x20;   $env:LLM\_MODEL="llama-3.3-70b-versatile"



Then:



&#x20;   streamlit run app.py



\## Fully local with Ollama

&#x20;   ollama pull qwen2.5:3b

&#x20;   $env:LLM\_BASE\_URL="http://localhost:11434/v1"

&#x20;   $env:LLM\_API\_KEY="ollama"

&#x20;   $env:LLM\_MODEL="qwen2.5:3b"



\## Open-weight models

Works with any OpenAI-compatible endpoint: Llama via Groq, gpt-oss via DigitalOcean Serverless Inference, or Qwen locally via Ollama. Never commit API keys.



\## License

MIT. Built for Hacktoberfest 2026 Hack Day Bhopal.

