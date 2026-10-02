# Free AI Chatbot

A browser-based AI chatbot built from scratch in Python. It costs nothing to run: it uses Google's free Gemini API tier, or a local model through Ollama that never sends data off your machine.

## What it does

- **3 switchable bots:** Helpful Assistant, Coding Buddy, and Sarcastic Pirate. Each one is just a system prompt, so adding a bot is one line in `app.py`.
- **Conversation memory:** the full chat history is sent with every request, so the bot remembers what was said earlier.
- **Streaming replies:** text appears as the model writes it.
- **Model picker:** change models from a dropdown without restarting.
- **Save and load chats:** conversations are written to disk as JSON and can be reloaded later.
- **Live personality editing:** edit a bot's system prompt in the UI and it applies on the next message.
- **Plain-English errors:** a bad key, a rate limit, or a wrong model name shows a short explanation in the chat instead of a crash.

## Tech stack

| Part | Technology |
|---|---|
| Language | Python 3.10+ |
| Web interface | Gradio 6 |
| Cloud AI | Google Gemini API (`google-genai`), free tier |
| Local AI | Ollama (Llama, Mistral, Qwen, Gemma) through the `openai` SDK |
| Secrets | `python-dotenv` and a gitignored `.env` file |
| Storage | JSON files |
| Tests | pytest |

## How it works

```
You type a message
      |
      v
app.py (Gradio UI)
  keeps the chat history, sends history + system prompt + model
      |
      v
providers.py
  GeminiProvider -> Google AI Studio API (cloud, free tier)
  OllamaProvider -> local model on your machine
      |
      v
Reply streams back chunk by chunk into the chat window
```

Memory is not magic. The model remembers nothing between calls. The app keeps the history list and resends all of it every turn.

## Quick start (Windows PowerShell)

You need Python 3.10+ and a free Gemini API key from [aistudio.google.com](https://aistudio.google.com). No credit card is required.

```powershell
git clone https://github.com/mj65825/cybersecurity-portfolio.git
cd cybersecurity-portfolio\Projects\AI-Chatbot

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
notepad .env        # paste your key after GEMINI_API_KEY=

python app.py
```

Open the link it prints (usually `http://127.0.0.1:7860`). On Mac or Linux, activate the environment with `source .venv/bin/activate` and use `cp` instead of `copy`.

## Configuration

Settings live in `.env`:

```
PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

To run fully offline instead, install [Ollama](https://ollama.com), run `ollama pull llama3.1`, and set `PROVIDER=ollama`. No key is needed.

## Adding a bot

Edit the `BOTS` dictionary near the top of `app.py`:

```python
BOTS = {
    "Helpful Assistant": "You are a helpful, concise assistant...",
    "Your New Bot":      "Describe the personality here.",
}
```

## Security notes

- **Secrets handling:** the API key is read from `.env` at runtime and is never written in the source. `.env` is listed in `.gitignore`, and so are saved conversations.
- **Local option:** with `PROVIDER=ollama`, prompts and replies stay on your own machine.
- **Provider layer:** the AI backend sits behind one small interface (`stream(model, system_prompt, history)`), so the app logic does not depend on any one vendor.
- **Known limits:** this is a learning project. There is no login, no rate limiting, and no prompt-injection filtering. Do not expose it to the public internet with a real key attached, and keep sensitive data off the Gemini free tier, since Google may use free-tier prompts to improve its models.

## Tests

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

20 tests run offline with a fake AI backend, so no key or internet is needed. They cover message handling, memory across turns, the Gradio 6 message-format fix, error messages, bot switching, and save/load.

## A bug worth mentioning

Gradio 6 stores streamed messages as a list like `[{"text": "hi", "type": "text"}]` instead of a plain string. Passing that straight to Gemini caused a validation error on the second message. The `_to_text()` helper in `providers.py` flattens either format to a plain string, and tests cover both.

## Project structure

```
AI-Chatbot/
├── app.py                 # UI, chat logic, bots, save/load
├── providers.py           # Gemini and Ollama backends
├── requirements.txt       # runtime dependencies
├── requirements-dev.txt   # adds pytest
├── .env.example           # copy to .env and add your key
├── .gitignore
└── tests/
    └── test_chatbot.py
```

## Ideas for next steps

- Separate memory for each bot
- Prompt-injection detection and logging
- Redacting personal data before messages leave the machine
- Free hosting on Hugging Face Spaces

## License

MIT, see the [LICENSE](../../LICENSE) at the repo root.
