"""
Chat backends for the free chatbot.
Supports Gemini (free cloud) and Ollama (free, local).

Set PROVIDER=gemini or PROVIDER=ollama in your .env file.
"""
import os


def get_provider(name):
    name = (name or "gemini").lower()
    if name == "gemini":
        return GeminiProvider(api_key=os.environ.get("GEMINI_API_KEY", ""))
    if name == "ollama":
        return OllamaProvider(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        )
    raise ValueError(f"Unknown PROVIDER '{name}'. Use 'gemini' or 'ollama'.")


def _to_text(content):
    """
    Gradio 6 stores streamed messages as a list of dicts like:
        [{"text": "hello", "type": "text"}]
    Earlier turns may still be plain strings.
    This always returns a plain string no matter which format comes in.
    """
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict):
                parts.append(p.get("text", ""))
            else:
                parts.append(str(p))
        return "".join(parts)
    return str(content or "")


class GeminiProvider:
    """
    Uses the Google Gemini free tier.
    Get a free key at: https://aistudio.google.com
    No credit card required. 1500 requests/day free.
    """

    def __init__(self, api_key):
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing.\n"
                "1. Go to https://aistudio.google.com\n"
                "2. Sign in with Google\n"
                "3. Create an API key\n"
                "4. Paste it into your .env file as: GEMINI_API_KEY=your_key_here"
            )
        from google import genai
        from google.genai import types
        self._types = types
        self.client = genai.Client(api_key=api_key)

    def stream(self, model, system_prompt, history):
        """Stream the reply chunk by chunk."""
        types = self._types

        # Convert history to Gemini format.
        # Gemini calls the assistant role "model" (not "assistant").
        contents = []
        for turn in history:
            role = "user" if turn["role"] == "user" else "model"
            text = _to_text(turn["content"])
            contents.append({
                "role": role,
                "parts": [{"text": text}]
            })

        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None
        )

        for chunk in self.client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            if getattr(chunk, "text", None):
                yield chunk.text


class OllamaProvider:
    """
    Uses a local model via Ollama. Fully private, no rate limits, $0 forever.
    Install from: https://ollama.com
    Then run: ollama pull llama3.1
    """

    def __init__(self, base_url="http://localhost:11434/v1"):
        from openai import OpenAI
        # Ollama uses an OpenAI-compatible endpoint.
        # The API key value is ignored but the SDK requires something non-empty.
        self.client = OpenAI(base_url=base_url, api_key="ollama")

    def stream(self, model, system_prompt, history):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for turn in history:
            messages.append({
                "role": turn["role"],
                "content": _to_text(turn["content"])
            })
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
